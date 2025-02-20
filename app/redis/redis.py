import sys

from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis.asyncio import Redis

from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis_client = Redis(
        host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True
    )
    try:
        if not await app.state.redis_client.ping():
            print("Redis is not running! Exiting application.")
            sys.exit(1)

        print("Redis connected!")
        yield

    finally:
        await app.state.redis_client.close()
        print("Redis disconnected!")
