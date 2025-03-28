from typing import Union

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError, BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.user import UserController
from app.core.config import config
from app.core.database import get_session
from app.core.exceptions import UnauthorizedException
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", scheme_name="JWT")


class TokenData(BaseModel):
    username: Union[str, None] = None
    expiry: Union[int, None] = None


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        session: AsyncSession = Depends(get_session),
        user_controller: UserController = Depends(UserController),
) -> User:
    """
    Get the current authenticated user based on the provided security
    scopes and token.

    Args:
        user_controller: User controller dependency.
        token (str): The authentication token.

    Returns:
        User: The current authenticated user.

    Raises:
        HTTPException: If the credentials cannot be validated or the token
        is expired.
    """
    async with session as db:
        try:
            payload = jwt.decode(
                token,
                config.SECRET_KEY,
                algorithms=[config.JWT_ALGORITHM]
            )
            username: str = payload.get("sub")
            if username is None:
                raise UnauthorizedException("Could not validate credentials")

            expiry: int = payload.get("exp")
            token_data = TokenData(username=username, expiry=expiry)
        except jwt.ExpiredSignatureError:
            raise UnauthorizedException("Token expired")
        except (JWTError, ValidationError):
            raise UnauthorizedException("Could not validate credentials")


        user: User = await user_controller.user_repository.get_by_email(db=db, email=token_data.username)
        if user is None:
            raise UnauthorizedException("Could not validate credentials")

        return user
