import hashlib
import json
import logging

import redis.asyncio as aioredis

logger = logging.getLogger(__name__)


class CacheService:
    def __init__(self, redis: aioredis.Redis) -> None:
        self.redis = redis

    async def get_embedding(self, text: str) -> list[float] | None:
        """Get cached embedding for text."""
        key = f"emb:{hashlib.sha256(text.encode()).hexdigest()}"
        data = await self.redis.get(key)
        if data:
            return json.loads(data)
        return None

    async def set_embedding(self, text: str, embedding: list[float], ttl: int = 86400) -> None:
        """Cache an embedding with TTL (default 24 hours)."""
        key = f"emb:{hashlib.sha256(text.encode()).hexdigest()}"
        await self.redis.set(key, json.dumps(embedding), ex=ttl)

    async def get_search_results(self, cache_key: str) -> dict | None:
        """Get cached search results."""
        data = await self.redis.get(f"search:{cache_key}")
        if data:
            return json.loads(data)
        return None

    async def set_search_results(
        self, cache_key: str, results: dict, ttl: int = 300
    ) -> None:
        """Cache search results with TTL (default 5 minutes)."""
        await self.redis.set(f"search:{cache_key}", json.dumps(results), ex=ttl)
