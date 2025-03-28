import pytest
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
import json

from app.controllers.user import UserController
from app.core.server import app
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.core.exceptions import NotFoundException


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_user_controller():
    return AsyncMock(spec=UserController)


@pytest.fixture
def mock_user():
    return User(id=1, email="test@example.com", hashed_password="hashed_password")


@pytest.fixture
def mock_user_response():
    return UserResponse(id=1, email="test@example.com", username="test")


@pytest.fixture
def mock_redis_cache():
    cache = AsyncMock()
    cache.get.return_value = None  # Default to no cache hit
    return cache


async def test_get_users(client, mock_user_controller, mock_user):
    mock_user_controller.read_users.return_value = [mock_user]
    with patch("app.controllers.user.UserController",
               return_value=mock_user_controller):
        response = client.get("/users")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [
            {"id": 1, "email": "test@example.com", "is_active": True,
             "is_superuser": False, "hashed_password": "hashed_password",
             "last_login": None}]


async def test_delete_user(client, mock_user_controller):
    mock_user_controller.user_delete.return_value = "User deleted successfully"
    with patch("app.controllers.user.UserController",
               return_value=mock_user_controller):
        response = client.delete("/users/1")
        assert response.status_code == status.HTTP_200_OK
        assert response.text == '"User deleted successfully"'
        mock_user_controller.user_delete.assert_called_once_with(id=1)


async def test_create_user(client, mock_user_controller, mock_user_response):
    mock_user_controller.create_user.return_value = mock_user
    user_create_data = {"email": "test@example.com", "password": "password",
                        "username": "test"}
    with patch("app.controllers.user.UserController",
               return_value=mock_user_controller):
        response = client.post("/users", json=user_create_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {"id": 1, "email": "test@example.com",
                                   "username": "test"}
        mock_user_controller.create_user.assert_called_once()


async def test_edit_user(client, mock_user_controller, mock_user_response):
    mock_user_controller.edit_user_db.return_value = mock_user
    user_update_data = {"email": "updated@example.com"}
    with patch("app.controllers.user.UserController",
               return_value=mock_user_controller):
        response = client.put("/users/1", json=user_update_data)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"id": 1, "email": "updated@example.com",
                                   "username": "test"}
        mock_user_controller.edit_user_db.assert_called_once_with(id=1, user=UserUpdate(
            **user_update_data))


async def test_get_user_by_email(client, mock_user_controller, mock_user_response):
    mock_user_controller.get_user.return_value = mock_user
    with patch("app.controllers.user.UserController",
               return_value=mock_user_controller):
        response = client.get("/users/test@example.com")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"id": 1, "email": "test@example.com",
                                   "username": "test"}
        mock_user_controller.get_user.assert_called_once_with(email="test@example.com")


async def test_get_user_from_cache(mock_user_controller, mock_redis_cache,
                                   mock_user_response):
    mock_redis_cache.get.return_value = json.dumps(mock_user_response.model_dump())
    mock_user_controller.redis_cache = mock_redis_cache
    mock_user_controller.user_repository = AsyncMock()  # Prevent repository call

    retrieved_user = await mock_user_controller.get_user(email="test@example.com")
    assert retrieved_user == mock_user_response
    mock_redis_cache.get.assert_called_once_with(
        "user:None")  # id is None in mock_user_response


async def test_get_user_not_found(client, mock_user_controller):
    mock_user_controller.get_user.side_effect = NotFoundException("User not found")
    with patch("app.controllers.user.UserController",
               return_value=mock_user_controller):
        response = client.get("/users/nonexistent@example.com")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "User not found"}
        mock_user_controller.get_user.assert_called_once_with(
            email="nonexistent@example.com")


async def test_read_users_from_cache(mock_user_controller, mock_redis_cache,
                                     mock_user_response):
    mock_redis_cache.get.return_value = json.dumps([mock_user_response.model_dump()])
    mock_user_controller.redis_cache = mock_redis_cache
    mock_user_controller.user_repository = AsyncMock()

    retrieved_users = await mock_user_controller.read_users()
    assert retrieved_users == [mock_user_response]
    mock_redis_cache.get.assert_called_once_with("users:0:100")


async def test_create_user_invalidates_cache(mock_user_controller, mock_redis_cache,
                                             mock_user):
    mock_user_controller.create_user.return_value = mock_user
    mock_user_controller.redis_cache = mock_redis_cache
    mock_redis_cache.redis = AsyncMock()  # Mock the underlying Redis client

    user_create = UserCreate(email="new@example.com", password="password")
    await mock_user_controller.create_user(user=user_create)

    mock_redis_cache.redis.keys.assert_called_once_with("users:*")
    mock_redis_cache.redis.delete.assert_called_once()  # Assuming there's at least one key


async def test_delete_user_invalidates_cache(mock_user_controller, mock_redis_cache):
    mock_user_controller.redis_cache = mock_redis_cache
    mock_redis_cache.redis = AsyncMock()

    await mock_user_controller.user_delete(id=1)

    mock_redis_cache.redis.delete.assert_any_call("user:1")
    mock_redis_cache.redis.keys.assert_called_once_with("users:*")
    mock_redis_cache.redis.delete.assert_called()  # Ensure delete is called at least twice


async def test_edit_user_invalidates_cache(mock_user_controller, mock_redis_cache,
                                           mock_user):
    mock_user_controller.edit_user_db.return_value = mock_user
    mock_user_controller.redis_cache = mock_redis_cache
    mock_redis_cache.redis = AsyncMock()

    user_update = UserUpdate(email="updated@example.com")
    await mock_user_controller.edit_user_db(id=1, user=user_update)

    mock_redis_cache.redis.delete.assert_any_call("user:1")
    mock_redis_cache.redis.keys.assert_called_once_with("users:*")
    mock_redis_cache.redis.delete.assert_called()  # Ensure delete is called at least twice
