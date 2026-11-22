from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "DiagnoVision API"
    database_url: str = "sqlite:///./diagnovision.db"
    jwt_secret: str = "development-only-change-me-32-characters"
    access_minutes: int = 15
    refresh_days: int = 7
    allowed_origins: str = "http://localhost:3000,http://localhost:8080"
    secure_cookies: bool = False
    demo_mode: bool = True
    max_upload_bytes: int = 20 * 1024 * 1024
    redis_url: str = "redis://redis:6379/0"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def origins(self) -> list[str]:
        return [value.strip() for value in self.allowed_origins.split(",") if value.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()

