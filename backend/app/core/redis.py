from collections.abc import AsyncGenerator

from redis.asyncio import Redis, from_url

from app.core.config import settings

redis_client: Redis | None = None


async def init_redis() -> None:
    global redis_client  # noqa: PLW0603
    redis_client = from_url(settings.REDIS_URL, decode_responses=True)


async def close_redis() -> None:
    global redis_client  # noqa: PLW0603
    if redis_client:
        await redis_client.close()
        redis_client = None


async def get_redis() -> AsyncGenerator[Redis, None]:
    if redis_client is None:
        raise RuntimeError("Redis not initialised. Call init_redis() first.")
    yield redis_client
