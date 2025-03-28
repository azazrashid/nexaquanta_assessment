from typing import Dict

from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.exceptions import (
    BadRequestException,
    UnauthorizedException,
)
from app.core.jwt import JWTHandler
from app.core.password import PasswordHandler
from app.repositories.user import UserRepository


class AuthController:
    def __init__(
            self,
            session: AsyncSession = Depends(get_session),
            user_repository: UserRepository = Depends(UserRepository)
    ):
        """
        Controller handling authentication-related operations.
        """
        self.session = session
        self.user_repository = user_repository

    async def login(self, email: str, password: str) -> Dict:
        """
        Handles user login.

        :param email: User's email address.
        :param password: User's password.

        :return: Token: The access token for the authenticated user.
        """
        async with self.session as db:
            # Retrieve user based on email
            user = await self.user_repository.get_by_email(email=email, db=db)

            if not user:
                raise BadRequestException("Invalid credentials")

            # Verify the password against the stored hash
            if not PasswordHandler.verify(hashed_password=user.hashed_password,
                                          plain_password=password):
                raise UnauthorizedException("Invalid credentials")

            # Generate an access token for the user
            access_token = JWTHandler.encode(
                payload={"sub": user.email},
            )
            refresh_token = JWTHandler.encode(payload={"sub": user.email})
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer"
            }
