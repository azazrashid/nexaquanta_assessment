import pytest
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
import json

from app.controllers.blog import BlogController
from app.core.server import app
from app.models import User, BlogPost
from app.schemas.blog import BlogCreate, BlogUpdate, BlogResponse
from app.core.exceptions import NotFoundException, BadRequestException


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_blog_controller():
    return AsyncMock(spec=BlogController)


@pytest.fixture
def mock_user():
    return User(id=1, email="test@example.com")


@pytest.fixture
def mock_blog():
    return BlogPost(id=1, title="Test Blog", content="Test Content", author_id=1)


@pytest.fixture
def mock_blog_response():
    return BlogResponse(id=1, title="Test Blog", content="Test Content", author_id=1)


@pytest.fixture
def mock_redis_cache():
    cache = AsyncMock()
    cache.get.return_value = None  # Default to no cache hit
    return cache


async def test_get_blogs(client, mock_blog_controller, mock_blog_response):
    mock_blog_controller.read_blogs.return_value = [mock_blog]
    with patch("app.controllers.blog.BlogController",
               return_value=mock_blog_controller):
        response = client.get("/blogs")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [
            {"id": 1, "title": "Test Blog", "content": "Test Content", "author_id": 1}]
        mock_blog_controller.read_blogs.assert_called_once_with(offset=0, limit=100)


async def test_delete_blog_success(client, mock_blog_controller, mock_user):
    mock_blog_controller.blog_delete.return_value = None
    with patch("app.controllers.blog.BlogController",
               return_value=mock_blog_controller):
        response = client.delete("/blogs/1")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        mock_blog_controller.blog_delete.assert_called_once_with(id=1,
                                                                 current_user=mock_user)


async def test_delete_blog_unauthorized(client, mock_blog_controller, mock_user,
                                        mock_blog):
    mock_blog_controller.blog_delete.side_effect = BadRequestException(
        "Only authors can delete their blogs.")
    with patch("app.controllers.blog.BlogController",
               return_value=mock_blog_controller):
        response = client.delete(
            "/blogs/2")  # Assuming blog with id=2 has a different author
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"detail": "Only authors can delete their blogs."}
        mock_blog_controller.blog_delete.assert_called_once_with(id=2,
                                                                 current_user=mock_user)


async def test_create_blog(client, mock_blog_controller, mock_blog_response, mock_user):
    mock_blog_controller.create_blog.return_value = mock_blog
    blog_create_data = {"title": "New Blog", "content": "New Content", "author_id": 1}
    with patch("app.controllers.blog.BlogController",
               return_value=mock_blog_controller):
        response = client.post("/blogs", json=blog_create_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {"id": 1, "title": "Test Blog",
                                   "content": "Test Content", "author_id": 1}
        mock_blog_controller.create_blog.assert_called_once_with(current_user=mock_user,
                                                                 blog=BlogCreate(
                                                                     **blog_create_data))


async def test_edit_blog(client, mock_blog_controller, mock_blog_response):
    mock_blog_controller.edit_blog_db.return_value = mock_blog
    blog_update_data = {"title": "Updated Blog"}
    with patch("app.controllers.blog.BlogController",
               return_value=mock_blog_controller):
        response = client.put("/blogs/1", json=blog_update_data)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"id": 1, "title": "Test Blog",
                                   "content": "Test Content", "author_id": 1}
        mock_blog_controller.edit_blog_db.assert_called_once_with(id=1, blog=BlogUpdate(
            **blog_update_data))


async def test_get_blog_by_id(client, mock_blog_controller, mock_blog_response):
    mock_blog_controller.get_blog.return_value = mock_blog
    with patch("app.controllers.blog.BlogController",
               return_value=mock_blog_controller):
        response = client.get("/blogs/1")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"id": 1, "title": "Test Blog",
                                   "content": "Test Content", "author_id": 1}
        mock_blog_controller.get_blog.assert_called_once_with(id=1)


async def test_get_blog_from_cache(mock_blog_controller, mock_redis_cache,
                                   mock_blog_response):
    mock_redis_cache.get.return_value = json.dumps(mock_blog_response.model_dump())
    mock_blog_controller.redis_cache = mock_redis_cache
    mock_blog_controller.blog_repository = AsyncMock()

    retrieved_blog = await mock_blog_controller.get_blog(id=1)
    assert retrieved_blog == mock_blog_response
    mock_redis_cache.get.assert_called_once_with("blog:1")


async def test_get_blog_not_found(client, mock_blog_controller):
    mock_blog_controller.get_blog.side_effect = NotFoundException("Blog not found")
    with patch("app.controllers.blog.BlogController",
               return_value=mock_blog_controller):
        response = client.get("/blogs/2")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "Blog not found"}
        mock_blog_controller.get_blog.assert_called_once_with(id=2)


async def test_read_blogs_from_cache(mock_blog_controller, mock_redis_cache,
                                     mock_blog_response):
    mock_redis_cache.get.return_value = json.dumps([mock_blog_response.model_dump()])
    mock_blog_controller.redis_cache = mock_redis_cache
    mock_blog_controller.blog_repository = AsyncMock()

    retrieved_blogs = await mock_blog_controller.read_blogs()
    assert retrieved_blogs == [mock_blog_response]
    mock_redis_cache.get.assert_called_once_with("blogs:0:100")


async def test_create_blog_invalidates_cache(mock_blog_controller, mock_redis_cache,
                                             mock_user, mock_blog):
    mock_blog_controller.create_blog.return_value = mock_blog
    mock_blog_controller.redis_cache = mock_redis_cache
    mock_redis_cache.redis = AsyncMock()

    blog_create = BlogCreate(title="New Blog", content="New Content", author_id=1)
    await mock_blog_controller.create_blog(current_user=mock_user, blog=blog_create)

    mock_redis_cache.redis.keys.assert_called_once_with("blogs:*")
    mock_redis_cache.redis.delete.assert_called_once()


async def test_delete_blog_invalidates_cache(mock_blog_controller, mock_redis_cache,
                                             mock_user, mock_blog):
    mock_blog_controller.blog_delete.return_value = None
    mock_blog_controller.redis_cache = mock_redis_cache
    mock_redis_cache.redis = AsyncMock()

    await mock_blog_controller.blog_delete(current_user=mock_user, id=1)

    mock_redis_cache.redis.delete.assert_any_call("blog:1")
    mock_redis_cache.redis.keys.assert_called_once_with("blogs:*")
    mock_redis_cache.redis.delete.assert_called()


async def test_edit_blog_invalidates_cache(mock_blog_controller, mock_redis_cache,
                                           mock_blog):
    mock_blog_controller.edit_blog_db.return_value = mock_blog
    mock_blog_controller.redis_cache = mock_redis_cache
    mock_redis_cache.redis = AsyncMock()

    blog_update = BlogUpdate(title="Updated Title")
    await mock_blog_controller.edit_blog_db(id=1, blog=blog_update)

    mock_redis_cache.redis.delete.assert_any_call("blog:1")
    mock_redis_cache.redis.keys.assert_called_once_with("blogs:*")
    mock_redis_cache.redis.delete.assert_called()
