# Project Structure Guide

This document explains how the Resume Readiness Intelligence Engine repository is organized and where to add new code, prompts, or data. Use it as a map while extending the system or wiring up the future front end.

## Top-Level Layout

| Path | Purpose |
| --- | --- |
| `backend/` | Python services (agents, API, RAG utilities). Contains the new `app/` package. |
| `backend/app/` | Source of truth for backend logic, configuration, and workflow orchestration. |
| `frontend/` | Placeholder for the future web client (Lovable/React). |
| `docs/` | Design docs, diagrams, and project notes (this file lives here). |
| `demo/` | Quick-start assets such as sample job descriptions or resumes for demos. |
| `scripts/` | CLI helpers (ingestion, deployment, maintenance tasks). |
| `requirements.txt` | Shared Python dependency list for the backend. |

## Backend Package (`backend/app`)

```
backend/app/
├── __init__.py               # Exposes shared config when importing `app`
├── api/                      # FastAPI routes or other HTTP entrypoints
├── config.py                 # Environment-driven settings (LLM models, API keys)
├── data/                     # Static XML assets (skill taxonomies, curated catalogs)
├── prompts/                  # Prompt templates and instructions for LLM calls
├── rag/                      # RAG ingestion + retrieval helpers
├── services/                 # Business logic (resume parser, skill evaluators, etc.)
└── workflow/                 # Orchestrators and pipelines that stitch services together
```

### Key Services

- `services/resume_parser.py`: Converts PDFs or plaintext into the canonical XML schema via Groq (returned as a raw XML string).
- `services/resume_skill_eval.py`: Accepts the résumé XML, calls an LLM with a few-shot prompt, and returns a `{ "skills": [{"name": str, "level": int}] }` dictionary with 0-3 mastery levels. It can also take job-required skill targets so the returned names/ordering match the job description (missing résumé evidence is scored as `0`).
- `services/job_skill_eval.py`: Reads raw job descriptions and emits `<jobSkills>` XML with 0-3 priority levels per skill (useful for gap comparisons). Use `job_skills_to_dict` when you need the parsed `{ "skills": [...] }` structure for downstream agents.
- Future modules (`skill_extractor.py`, `gap_analyzer.py`, etc.) belong in `services/` as they handle a single domain task.

### Workflow Layer

`workflow/orchestrator.py` shows how services get composed. Add new pipeline modules here (e.g., LangGraph or task runners) so the API and CLI can invoke a single interface.

### API Layer

`api/` will host the FastAPI app that the simple web front end will call. Start with `api/main.py` (see placeholder) and add routers or dependencies as needed.

### Prompts & Data

- Drop prompt templates into `prompts/` (Markdown). Include variable placeholders in Jinja-style (`{{ skill }}`) or whatever templating engine you pick.
- Store curated resources, taxonomies, or scoring rubrics inside `data/` as XML (preferred) or other hierarchical formats that mirror the structure expected by downstream services (see `backend/app/data/sample_skill_taxonomy.xml` for an example). They are versioned alongside the code.

### RAG Utilities

`rag/ingest.py` demonstrates how to ingest documents into Chroma. Expand this package with chunking, embedding, and retrieval code so both CLI scripts and services can reuse the same vector-store logic.

## Frontend Placeholder

`frontend/` is intentionally empty today. When ready, scaffold a React/Lovable app here and call the backend API endpoints defined under `backend/app/api`.

## Demo Assets

`demo/` can hold synthetic resumes, job descriptions, and notebooks for quick demos. Keep sensitive data out of the repo.

## Scripts

Reusable CLI scripts (for ingestion, deployment, or batch jobs) live under `scripts/`. They can import from `backend/app` to ensure consistency.

## How to Extend

1. **Add raw assets** (prompts, data) under `backend/app/prompts` or `backend/app/data`.
2. **Create/extend services** inside `backend/app/services` with clear docstrings and dictionary-based contracts (keep schemas simple and documented in code/comments).
3. **Wire logic** via an orchestrator in `backend/app/workflow`.
4. **Expose endpoints** in `backend/app/api/main.py` once the workflow is ready.
5. **Update this README** if you add new top-level directories or conventions.
