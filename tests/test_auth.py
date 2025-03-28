import pytest
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.controllers.auth import AuthController
from app.core.server import app
from app.models.user import User
from app.schemas.user import Token


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_auth_controller():
    return AsyncMock(spec=AuthController)


@pytest.fixture
def mock_user():
    return User(id=1, email="test@example.com", hashed_password="hashed_password")


@pytest.fixture
def mock_token():
    return Token(access_token="mock_access_token", refresh_token="mock_refresh_token",
                 token_type="bearer")


async def test_login_success(client, mock_auth_controller, mock_user, mock_token):
    mock_auth_controller.login.return_value = mock_token
    with patch("app.controllers.auth.AuthController",
               return_value=mock_auth_controller):
        response = client.post(
            "/login", data={"username": "test@example.com", "password": "password"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == mock_token.dict()
        mock_auth_controller.login.assert_called_once_with(
            email="test@example.com", password="password"
        )


async def test_login_invalid_credentials_user_not_found(client, mock_auth_controller):
    mock_auth_controller.login.side_effect = Exception(
        "Invalid credentials")  # Simulate user not found
    with patch("app.controllers.auth.AuthController",
               return_value=mock_auth_controller):
        response = client.post(
            "/login",
            data={"username": "nonexistent@example.com", "password": "password"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"detail": "Invalid credentials"}
        mock_auth_controller.login.assert_called_once_with(
            email="nonexistent@example.com", password="password"
        )


async def test_login_invalid_credentials_incorrect_password(client,
                                                            mock_auth_controller):
    mock_auth_controller.login.side_effect = Exception(
        "Invalid credentials")  # Simulate incorrect password
    with patch("app.controllers.auth.AuthController",
               return_value=mock_auth_controller):
        response = client.post(
            "/login",
            data={"username": "test@example.com", "password": "wrong_password"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Invalid credentials"}
        mock_auth_controller.login.assert_called_once_with(
            email="test@example.com", password="wrong_password"
        )


async def test_read_users_me_authenticated(client, mock_user, mock_auth_controller):
    async def mock_get_current_user():
        return mock_user

    with patch("app.core.dependencies.current_user.get_current_user",
               new=mock_get_current_user):
        response = client.get(
            "/me",
            headers={"Authorization": "Bearer mock_access_token"}
            # In a real scenario, you'd have a valid token
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"id": 1, "email": "test@example.com",
                                   "is_active": True, "is_superuser": False,
                                   "hashed_password": "hashed_password",
                                   "last_login": None}  # Adjust based on your User model
