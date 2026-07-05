import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class GoogleMapsSettings:
    """
    Configuration for Google Maps integration
    """

    @property
    def google_maps_base_url(self) -> str:
        return os.environ.get(
            "GOOGLE_MAPS_BASE_API", "https://maps.googleapis.com/maps/api"
        )

    @property
    def maps_timeout(self) -> int:
        return int(os.environ.get("MAPS_TIMEOUT", "10"))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # Database
    postgres_user: str = "postgresdbuser"
    postgres_password: str = "postgresdbpw"
    postgres_db: str = "ride_sharing_db"
    db_host: str = "postgres"
    db_port: int = 5433

    # redis
    redis_host: str | None = os.environ.get("REDIS_HOST")
    redis_port: int = int(os.environ.get("REDIS_PORT", 6379))
    redis_password: str | None = os.getenv("REDIS_PASSWORD")
    redis_db: int = int(os.getenv("REDIS_DB", "0"))
    ride_cache_ttl: int = int(os.getenv("RIDE_CACHE_TTL", 60 * 60))  # 1 Hour

    # Google Maps
    google_maps_api_key: str | None = os.environ.get("GOOGLE_MAPS_KEY")

    # Fare
    base_fare: int = int(os.environ.get("BASE_FARE", "30"))

    # JWT (optional, for future auth if needed)
    jwt_secret: str | None = os.environ.get("JWT_SECRET", "your_jwt_secret_key")
    jwt_algorithm: str = os.environ.get("ALGORITHM", "HS256")
    jwt_expire_minutes: int = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

    # App
    app_name: str = "FastAPI Starter"
    debug: bool = False

    @property
    def redis_url(self) -> str:
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @property
    def database_url(self) -> str:
        return f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}@{self.db_host}:{self.db_port}/{self.postgres_db}"

    @property
    def google_maps_settings(self) -> GoogleMapsSettings:
        return GoogleMapsSettings()


@lru_cache
def get_settings() -> Settings:
    return Settings()
