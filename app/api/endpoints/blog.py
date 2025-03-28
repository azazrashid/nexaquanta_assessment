from fastapi import APIRouter, Depends, Security

from app.controllers.blog import BlogController
from app.core.dependencies.current_user import get_current_user
from app.models import User
from app.schemas.blog import BlogCreate, BlogUpdate
from app.schemas.blog import BlogResponse

router = APIRouter()


@router.get("", response_model=list[BlogResponse])
async def get_blogs(
        offset: int = 0,
        limit: int = 100,
        current_user: User = Security(get_current_user),
        blog_controller: BlogController = Depends(BlogController),
):
    return await blog_controller.read_blogs(
        offset=offset, limit=limit
    )


@router.delete("{id}", status_code=204)
async def delete_blog(
        id: int,
        current_user: User = Security(get_current_user),
        blog_controller: BlogController = Depends(BlogController),
):
    return await blog_controller.blog_delete(id=id, current_user=current_user)


@router.post("", status_code=201, response_model=BlogResponse)
async def create_blog(
        blog: BlogCreate,
        current_user: User = Security(get_current_user),
        blog_controller: BlogController = Depends(BlogController),
):
    return await blog_controller.create_blog(current_user=current_user, blog=blog)


@router.put("/{id}", status_code=200, response_model=BlogResponse)
async def edit_blog(
        id: int,
        blog: BlogUpdate,
        blog_controller: BlogController = Depends(BlogController),
        current_user: User = Security(get_current_user),
):
    return await blog_controller.edit_blog_db(blog=blog, id=id)


@router.get("/{id}", status_code=200, response_model=BlogResponse)
async def get_blog_by_email(
        id: int,
        blog_controller: BlogController = Depends(BlogController),
        current_user: User = Security(get_current_user),
):
    return await blog_controller.get_blog(id=id)
