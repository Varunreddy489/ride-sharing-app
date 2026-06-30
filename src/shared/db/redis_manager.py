from collections.abc import AsyncGenerator

from redis.asyncio import Redis

from src.shared.utils.config import get_settings

_settings = get_settings()
_client: Redis | None = None


def get_redis_client() -> Redis:
    """
    Return a process-wide Redis client (async) backed by an internal pool.
    Lazily created on first use.
    """
    global _client
    if _client is None:
        _client = Redis.from_url(
            _settings.redis_url,
            encoding="utf-8",
            decode_responses=True,  # get/set str instead of bytes
            health_check_interval=30,
            socket_timeout=5,
        )
    return _client


async def get_redis() -> AsyncGenerator[Redis, None]:
    """
    FastAPI dependency, analogous to get_db in
    """
    client = get_redis_client()
    # Optionally verify readiness on first call:
    # await client.ping()
    try:
        yield client
    finally:
        # Keep the singleton alive; close on app shutdown via lifespan
        pass
