from fastapi import APIRouter, Depends, Security

from app.controllers.user import UserController
from app.core.dependencies.current_user import get_current_user
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.schemas.user import UserResponse

router = APIRouter()


@router.get("", response_model=list[UserResponse])
async def get_users(
        current_user: User = Security(get_current_user),
        user_controller: UserController = Depends(UserController),
):
    return await user_controller.read_users()


@router.delete("{id}", status_code=200, response_model=str)
async def delete_user(
        id: int,
        current_user: User = Security(get_current_user),
        user_controller: UserController = Depends(UserController),
):
    return await user_controller.user_delete(id=id)


@router.post("", status_code=201, response_model=UserResponse)
async def create_user(
        user: UserCreate,
        user_controller: UserController = Depends(UserController),
):
    return await user_controller.create_user(user=user)


@router.put("/{id}", status_code=200, response_model=UserResponse)
async def edit_user(
        id: int,
        user: UserUpdate,
        user_controller: UserController = Depends(UserController),
        current_user: User = Security(get_current_user),
):
    return await user_controller.edit_user_db(id=id, user=user)


@router.get("/{email}", status_code=200, response_model=UserResponse)
async def get_user_by_email(
        email: str,
        user_controller: UserController = Depends(UserController),
        current_user: User = Security(get_current_user),
):
    return await user_controller.get_user(email=email)
