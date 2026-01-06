import json

from app.cache.redis_client import init_redis


class CacheService:
    def __init__(self, namespace: str = ""):
        self.namespace = namespace

    async def _key(self, key: str) -> str:
        return f"{self.namespace}:{key}" if self.namespace else key

    async def get(self, key: str):
        redis = await init_redis()
        data = await redis.get(await self._key(key))
        return json.loads(data) if data else None

    async def set(self, key: str, value, ttl: int = 600):
        redis = await init_redis()
        await redis.setex(await self._key(key), ttl, json.dumps(value))

    async def delete(self, key: str):
        redis = await init_redis()
        await redis.delete(await self._key(key))
