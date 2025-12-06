"""Centralized configuration for backend services (no Pydantic dependency)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

# Load .env once at import time so services inherit local configuration.
load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")


@dataclass(slots=True)
class Settings:
    """Application-level configuration loaded from environment variables."""

    groq_api_key: str | None = None
    resume_parser_model: str = "llama-3.1-8b-instant"
    resume_parser_max_tokens: int = 2000
    resume_parser_temperature: float = 0.0
    rag_model: str = "llama-3.3-70b-versatile"
    rag_temperature: float = 0.1
    rag_persist_dir: str | None = None
    rag_collection_name: str = "RAG_DB_Learning_Resources"
    rag_embedding_model: str = "all-MiniLM-L6-v2"
    rag_top_k: int = 3


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached instance so every module shares the same settings object."""

    return Settings(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        resume_parser_model=os.getenv("RESUME_PARSER_MODEL", "llama-3.1-8b-instant"),
        resume_parser_max_tokens=int(os.getenv("RESUME_PARSER_MAX_TOKENS", "2000")),
        resume_parser_temperature=float(os.getenv("RESUME_PARSER_TEMPERATURE", "0.0")),
        rag_model=os.getenv("RAG_MODEL", "llama-3.1-8b-instant"),
        rag_temperature=float(os.getenv("RAG_TEMPERATURE", "0.1")),
        rag_persist_dir=os.getenv("RAG_PERSIST_DIR"),
        rag_collection_name=os.getenv("RAG_COLLECTION_NAME", "RAG_DB_Learning_Resources"),
        rag_embedding_model=os.getenv("RAG_EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
        rag_top_k=int(os.getenv("RAG_TOP_K", "3")),
    )


settings = get_settings()
