from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PocketSmart AI"
    environment: str = "development"
    secret_key: str = "dev-only-change-me"
    database_url: str = "sqlite:///./pocketsmart.db"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-3.8-flash"
    access_token_expire_minutes: int = 60
    max_upload_mb: int = 5
    frontend_origins: str = "http://127.0.0.1:8000,http://localhost:8000"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def origins(self) -> list[str]:
        return [x.strip() for x in self.frontend_origins.split(",") if x.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
