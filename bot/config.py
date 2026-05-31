from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str
    groq_api_key: str | None = None
    groq_model: str = "qwen/qwen3-32b"
    groq_base_url: str = "https://api.groq.com/openai/v1"
    groq_timeout: float = 30.0
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
