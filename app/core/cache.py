import redis.asyncio as redis
from app.core.config import config


class RedisCache:
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis = None

    async def connect(self):
        self.redis = await redis.from_url(self.redis_url, decode_responses=True)

    async def get(self, key: str):
        return await self.redis.get(key)

    async def set(self, key: str, value: str, expire: int = 600):  # Default expiration: 10 minutes
        await self.redis.set(key, value, ex=expire)

    async def close(self):
        if self.redis:
            await self.redis.close()


redis_cache = RedisCache(redis_url=config.REDIS_URL)


async def get_redis_cache():
    return redis_cache
