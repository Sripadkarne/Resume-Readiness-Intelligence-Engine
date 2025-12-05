"""Placeholder for the revamped ingestion pipeline.

This module can later replace ``backend/RAG/ingest.py`` once the rest of the
codebase has migrated into the ``backend/app`` package structure.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import chromadb


def ingest_documents(documents: Iterable[Path], collection_name: str = "rrie") -> None:
    """Example hook for wiring ingestion scripts into the shared package."""

    client = chromadb.PersistentClient(path="chroma_db")
    collection = client.get_or_create_collection(collection_name)
    for doc_path in documents:
        text = doc_path.read_text(encoding="utf-8")
        collection.add(documents=[text], ids=[doc_path.name])
