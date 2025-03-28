import json
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.exceptions import (
    NotFoundException,
)
from app.core.password import PasswordHandler
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.core.cache import get_redis_cache, RedisCache


class UserController:
    def __init__(
            self,
            session: AsyncSession = Depends(get_session),
            user_repository: UserRepository = Depends(UserRepository),
            redis_cache: RedisCache = Depends(get_redis_cache)
    ):
        """
        Controller handling user operations.
        """
        self.session = session
        self.user_repository: UserRepository = user_repository
        self.redis_cache = redis_cache

    async def get_user(self, email: str):
        cache_key = f"user:{id}"
        cached_user = await self.redis_cache.get(cache_key)

        if cached_user:
            return json.loads(cached_user)  # Return cached data

        async with self.session as db:
            result = await self.user_repository.get_by_email(email=email, db=db)
            if result is None:
                raise NotFoundException("User not found")

                # Store result in cache
            blog = UserResponse.model_validate(result.__dict__).model_dump()
            await self.redis_cache.set(cache_key, json.dumps(blog), expire=600)

            return result

    async def read_users(self, offset: int = 0, limit: int =100):
        cache_key = f"users:{offset}:{limit}"
        cached_users = await self.redis_cache.get(cache_key)

        if cached_users:
            return json.loads(cached_users)  # Return cached data

        async with self.session as db:
            users = await self.user_repository.get_all(db=db)
            if users is None:
                raise NotFoundException("Users not found")
            # Convert SQLAlchemy model to Pydantic response model before caching
            blog_list = [UserResponse.model_validate(user.__dict__).model_dump() for
                         user in users]
            # Store in Redis
            await self.redis_cache.set(cache_key, json.dumps(blog_list), expire=600)

            return users

    async def create_user(self, user: UserCreate) -> User:
        async with self.session as db:
            user_dict = user.model_dump(exclude_unset=True)
            password = user_dict.pop("password")
            user_dict["hashed_password"] = PasswordHandler.hash(password)
            db_user = await self.user_repository.create(db=db, **user_dict)
            await db.commit()

            # Invalidate cache
            keys = await self.redis_cache.redis.keys("users:*")
            if keys:
                await self.redis_cache.redis.delete(*keys)
            return db_user

    async def user_delete(self,  id: int):
        async with self.session as db:
            await self.user_repository.delete(db=db, id=id)

            # Invalidate cache
            await self.redis_cache.redis.delete(f"user:{id}")
            keys = await self.redis_cache.redis.keys("users:*")
            if keys:
                await self.redis_cache.redis.delete(*keys)
            await db.commit()

    async def edit_user_db(self, id: int, user: UserUpdate) -> User:
        async with self.session as db:
            user_ = user.model_dump()
            if user.password:
                password = user_.pop("password")
                user_["hashed_password"] = PasswordHandler.hash(password)

            user = await self.user_repository.update(db=db, id_=id,
                                                     update_data=user_)
            # Invalidate cache
            await self.redis_cache.redis.delete(f"user:{id}")
            keys = await self.redis_cache.redis.keys("users:*")
            if keys:
                await self.redis_cache.redis.delete(*keys)
            return user
