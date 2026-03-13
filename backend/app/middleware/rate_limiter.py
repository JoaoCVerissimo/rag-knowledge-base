import time

import redis.asyncio as aioredis
from fastapi import HTTPException, Request

from app.config import settings
from app.dependencies import redis_client


async def check_rate_limit(request: Request) -> None:
    """Redis sliding window rate limiter.

    Raises HTTPException(429) if rate limit exceeded.
    """
    client_ip = request.client.host if request.client else "unknown"
    key = f"ratelimit:{client_ip}"
    limit = settings.RATE_LIMIT_REQUESTS
    window = settings.RATE_LIMIT_WINDOW

    now = time.time()
    pipe = redis_client.pipeline()
    pipe.zremrangebyscore(key, 0, now - window)
    pipe.zadd(key, {str(now): now})
    pipe.zcard(key)
    pipe.expire(key, window)
    results = await pipe.execute()

    request_count = results[2]
    if request_count > limit:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Maximum {limit} requests per {window} seconds.",
        )
