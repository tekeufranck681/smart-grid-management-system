import redis.asyncio as aioredis
from app.core.config import settings

redis = None


async def init_redis():
    global redis
    if redis is None:
        redis = await aioredis.from_url(
            settings.REDIS_URL, encoding="utf-8", decode_responses=True
        )

    return redis


async def close_redis():
    global redis
    if redis:
        await redis.close()
        redis = None
