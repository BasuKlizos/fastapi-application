from fastapi import Request
from redis.asyncio import Redis

def get_redis_client(request: Request) -> Redis:
    redis_client = request.app.state.redis_client
    if not redis_client:
        raise RuntimeError("Redis client is not initialized!")

    return redis_client