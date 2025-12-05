# RAG Package Overview

- `ingest.py`: Example helper that loads documents into a Chroma collection (update with chunking + embedding logic).
- Future files:
  - `chunkers.py` – break long documents into overlapping windows.
  - `embeddings.py` – wrap embedding providers (OpenAI, Vertex, SentenceTransformers).
  - `retriever.py` – expose a class/function that given `SkillGap` items returns ranked `StudyResource` objects.

Keep large vector-store artifacts out of git; point to local folders (e.g., `chroma_db/`) in `.gitignore`.
