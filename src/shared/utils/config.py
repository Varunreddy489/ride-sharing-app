from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


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

    # JWT (optional, for future auth if needed)
    jwt_secret: str | None = None
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30

    # App
    app_name: str = "FastAPI Starter"
    debug: bool = False

    @property
    def database_url(self) -> str:
        return f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}@{self.db_host}:{self.db_port}/{self.postgres_db}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
