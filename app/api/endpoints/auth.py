from app.core.dependencies.current_user import get_current_user
from app.models.user import User
from fastapi import APIRouter, Depends, status, Security, Body
from fastapi.security import OAuth2PasswordRequestForm

from app.controllers.auth import AuthController
from app.schemas.user import Token, UserResponse

router = APIRouter()


@router.post("/login", response_model=Token)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        auth_controller: AuthController = Depends(AuthController)
):
    """Logs in a user using email and password."""
    return await auth_controller.login(
        email=form_data.username, password=form_data.password
    )


@router.get("/me", response_model=UserResponse)
async def read_users_me(
        current_user: User = Security(
            get_current_user,
            scopes=["Admin", "Creator", "Publisher", "Superuser", "Fmtv"]
        )
):
    return current_user