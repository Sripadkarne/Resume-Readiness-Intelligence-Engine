# Technical Appendix (Snapshot)

## Models and Services
- **LLM**: Groq `settings.resume_parser_model` / `settings.rag_model` (defaults in `backend/app/config.py`).
- **Embeddings**: HuggingFace `all-MiniLM-L6-v2`.
- **Vector DB**: Chroma persisted in `VectorDB` (override via `RAG_PERSIST_DIR`).

## Pipelines
- **Résumé parsing**: `resume_parser.py` → XML structure (skills, experience, projects).
- **Job skill extraction**: `job_skill_eval.py` → `<jobSkills>` XML with 0–3 priorities.
- **Résumé skill scoring**: `resume_skill_eval.py` → `<skillsEvaluation>` XML; optional alignment to job skills when requested.
- **Skill gap calc**: `skill_gap_eval.py` → `<skillGaps>` XML (non-negative gaps).
- **Study plan**: `rag_agent.py` uses retrieved context + gap XML to emit a 4-week markdown plan.
- **Workflow glue**: `backend/app/workflow/orchestrator.py` orchestrates the steps and returns artifacts to the API.

## Prompt Strategy (high level)
- Job skills: emphasize critical vs. nice-to-have; cap skill count; XML-only output.
- Résumé skills: rubric 0–3; few-shot guidance; optional right-join to job skills.
- Study plan: structured 4-week format; allocate effort proportional to gap; ground every action in retrieved docs; fallback message when context is missing.

## Data and Retrieval
- Local Chroma store seeded from curated PDFs/notes (see `VectorDB/`).
- Retriever filtered to avoid leaking backend/code files; resource metadata (title/id/url) included in context formatting.

## Evaluation (manual, current)
- Smoke test end-to-end with sample résumé/JD; verify gap XML and plan coherence.
- Check that skills with gap ≤ 0 are excluded from tasks.
- Confirm plan references provided resources and omits backend/code snippets.

## Configuration
- `.env` to set `GROQ_API_KEY` and optional overrides (`RAG_MODEL`, `RAG_PERSIST_DIR`, `RAG_TOP_K`, etc.).
- Defaults loaded via `backend/app/config.py`.

## Extensibility Notes
- Swap embeddings/vector DB by adjusting `EMBEDDING_MODEL_NAME` and `Chroma` instantiation in `rag_agent.py`.
- Replace Groq with another LangChain-compatible chat model by updating `ChatGroq` usage.
- Structured plan output can be extended to include practice questions or assessments before rendering.
