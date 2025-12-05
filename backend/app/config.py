"""Centralized configuration for backend services."""

from functools import lru_cache
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application-level configuration loaded from environment variables."""

    groq_api_key: str | None = Field(default=None, env="GROQ_API_KEY")
    resume_parser_model: str = Field(default="llama-3.1-8b-instant")
    resume_parser_max_tokens: int = Field(default=2000)
    resume_parser_temperature: float = Field(default=0.0)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached instance so every module shares the same settings object."""

    return Settings()


settings = get_settings()
