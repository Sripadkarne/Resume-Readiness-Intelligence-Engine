"""Centralized configuration for backend services (no Pydantic dependency)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(slots=True)
class Settings:
    """Application-level configuration loaded from environment variables."""

    groq_api_key: str | None = None
    resume_parser_model: str = "llama-3.1-8b-instant"
    resume_parser_max_tokens: int = 2000
    resume_parser_temperature: float = 0.0


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached instance so every module shares the same settings object."""

    return Settings(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        resume_parser_model=os.getenv("RESUME_PARSER_MODEL", "llama-3.1-8b-instant"),
        resume_parser_max_tokens=int(os.getenv("RESUME_PARSER_MAX_TOKENS", "2000")),
        resume_parser_temperature=float(os.getenv("RESUME_PARSER_TEMPERATURE", "0.0")),
    )


settings = get_settings()
