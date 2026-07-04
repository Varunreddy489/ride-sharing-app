from src.shared.utils.config import get_settings

REDIS_STATUS_KEY = "ride:{ride_id}:status"


class RedisUtils:
    def __init__(self, redis_client):
        self.redis_client = redis_client
        self.settings = get_settings()

    async def cache_ride_status(self, ride_id: int, status: str):
        key = f"ride:{ride_id}:status"
        await self.redis_client.setex(key, self.settings.ride_status_cache_ttl, status)

    async def get_cache_ride_status(self, ride_id: int):
        key = f"ride:{ride_id}:status"
        return await self.redis_client.get(key)
