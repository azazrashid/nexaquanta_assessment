from sqlalchemy import select
from app.models.user import User
from app.repositories.base_repo import BaseRepo


class UserRepository(BaseRepo[User]):
    """
    User repository provides all the database operations for the User model.
    """

    def __init__(self):
        super().__init__(User)

    async def get_by_email(self, db, email: str) -> User | None:
        """
        Get user by email.

        :param email: Email.
        :return: User.
        """
        query = select(User).filter(User.email == email)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_name(self, db, username: str) -> User | None:
        """
        Get user by username.

        :param username: User name.
        :return: User.
        """
        query = select(User).filter(User.username == username)
        result = await db.execute(query)
        return result.scalar_one_or_none()
