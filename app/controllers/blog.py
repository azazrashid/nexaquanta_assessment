import json
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.exceptions import NotFoundException, BadRequestException
from app.models import User, BlogPost
from app.repositories.blog import BlogRepository
from app.schemas.blog import BlogCreate, BlogUpdate, BlogResponse
from app.core.cache import get_redis_cache, RedisCache


class BlogController:
    def __init__(
        self,
        session: AsyncSession = Depends(get_session),
        blog_repository: BlogRepository = Depends(BlogRepository),
        redis_cache: RedisCache = Depends(get_redis_cache)
    ):
        """
        Controller handling blog operations.
        """
        self.session = session
        self.blog_repository: BlogRepository = blog_repository
        self.redis_cache = redis_cache

    async def get_blog(self, id: int):
        cache_key = f"blog:{id}"
        cached_blog = await self.redis_cache.get(cache_key)

        if cached_blog:
            return json.loads(cached_blog)  # Return cached data

        async with self.session as db:
            result = await self.blog_repository.get_by_id(id_=id, db=db)
            if result is None:
                raise NotFoundException("Blog not found")

            # Store result in cache
            blog = BlogResponse.model_validate(result.__dict__).model_dump()
            await self.redis_cache.set(cache_key, json.dumps(blog), expire=600)

            return result

    async def read_blogs(self, offset: int = 0, limit: int = 100):
        cache_key = f"blogs:{offset}:{limit}"
        cached_blogs = await self.redis_cache.get(cache_key)

        if cached_blogs:
            return json.loads(cached_blogs)  # Return cached data

        async with self.session as db:
            blogs = await self.blog_repository.get_all(db=db)
            if blogs is None:
                raise NotFoundException("Blogs not found")

            # Convert SQLAlchemy model to Pydantic response model before caching
            blog_list = [BlogResponse.model_validate(blog.__dict__).model_dump() for blog in blogs]

            # Store in Redis
            await self.redis_cache.set(cache_key, json.dumps(blog_list), expire=600)
            return blogs

    async def create_blog(self, current_user: User, blog: BlogCreate) -> BlogPost:
        async with self.session as db:
            blog_dict = blog.model_dump(exclude_unset=True)
            blog_dict["author_id"] = current_user.id
            db_blog = await self.blog_repository.create(db=db, **blog_dict)
            await db.commit()

            # Invalidate cache
            keys = await self.redis_cache.redis.keys("blogs:*")
            if keys:
                await self.redis_cache.redis.delete(*keys)
            return db_blog

    async def blog_delete(self, current_user: User, id: int):
        async with self.session as db:
            blog = await self.blog_repository.get_by_id(db=db, id_=id)
            if blog.author_id != current_user.id:
                raise BadRequestException("Only authors can delete their blogs.")
            await self.blog_repository.delete(db=db, id=id)
            await db.commit()

            # Invalidate cache
            await self.redis_cache.redis.delete(f"blog:{id}")
            keys = await self.redis_cache.redis.keys("blogs:*")
            if keys:
                await self.redis_cache.redis.delete(*keys)

    async def edit_blog_db(self, id: int, blog: BlogUpdate) -> BlogPost:
        async with self.session as db:
            blog_ = blog.model_dump()
            blog = await self.blog_repository.update(db=db, id_=id, update_data=blog_)

            # Invalidate cache
            await self.redis_cache.redis.delete(f"blog:{id}")
            keys = await self.redis_cache.redis.keys("blogs:*")
            if keys:
                await self.redis_cache.redis.delete(*keys)

            return blog
