# Resume Readiness Intelligence Engine — Product Brief

## Problem
Data/ML candidates struggle to judge role fit and to find credible learning paths. Existing AI tools often give surface-level advice that does not build skills.

## Solution
ResumeJobHelpAI evaluates a résumé against a target role, detects skill gaps, retrieves vetted learning resources, and generates a 4‑week study plan grounded in those resources.

## Users and Scope
- Primary: Data Scientist, ML Engineer.
- Near-term expansion: adjacent technical roles (software, analytics).

## System Overview
1) Upload résumé PDF + paste job description.  
2) Backend agents:
   - Parse résumé to structured XML.
   - Extract job-required skills (LLM).
   - Score résumé skills (LLM).
   - Compute skill gaps (XML).
   - RAG agent retrieves resources and produces a study plan.  
3) Frontend renders the plan (markdown, structured tasks, reasoning view).

## Architecture (current prototype)
- **Frontend**: static HTML/CSS/JS; fetches `POST /analyze-upload` with `FormData`.
- **API**: FastAPI (`backend/app/api/main.py`), entrypoint `uvicorn backend.app.api.main:app`.
- **Workflow**: `backend/app/workflow/orchestrator.py` wires parsers, evaluators, gap calc, and RAG agent.
- **Services**:
  - `resume_parser.py` → résumé XML.
  - `job_skill_eval.py` → job skills XML.
  - `resume_skill_eval.py` → résumé skills (aligned when needed).
  - `skill_gap_eval.py` → gap XML.
  - `rag_agent.py` → study plan (markdown) using retrieved docs.
- **RAG**: Chroma vector store (`VectorDB`), HuggingFace embeddings, Groq LLM.

## Demo Narrative (before/after)
- Before: Candidate unsure if qualified for “Data Scientist, fintech”; scattered resources.
- After: Upload résumé + JD → study plan with weekly tasks tied to specific resources; gap table shows where to focus.

## Key Decisions / Lessons
- XML throughout (skills, gaps) to avoid brittle parsing.
- Retrieval filtered to exclude backend code; resource metadata surfaced for citations.
- Simple static frontend to minimize setup friction.
- Chose Groq LLM + Chroma for fast, local-friendly prototype; can swap in cloud-native later.
