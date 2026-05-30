from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str
    openrouter_api_key: str | None = None
    openrouter_model: str = "qwen/qwen3-8b:free"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_timeout: float = 30.0
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
