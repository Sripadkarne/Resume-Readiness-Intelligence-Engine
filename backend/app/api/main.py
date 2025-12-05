"""FastAPI entrypoint exposing the analysis workflow.

This is a placeholder implementation to demonstrate how the orchestrator will
be called. Replace the dummy response once downstream services (skill gap,
RAG, study plan) are wired in.
"""

from __future__ import annotations

from fastapi import FastAPI

from ..workflow import analyze_inputs

app = FastAPI(title="Resume Readiness Intelligence Engine")


@app.get("/health")
def healthcheck() -> dict[str, str]:
    """Simple probe for uptime monitoring."""

    return {"status": "ok"}


@app.post("/analyze")
def analyze_resume(payload: dict[str, str]) -> dict[str, object]:
    """Run résumé/job parsing and return structured models.

    Expected payload keys:
    - `resume_pdf_path`: Absolute or repo-relative path to a PDF résumé.
    - `job_description`: Raw text of the job description.
    - `job_title` / `company` (optional): Overrides when the JD lacks metadata.
    """

    resume_xml, job_profile = analyze_inputs(
        resume_pdf_path=payload["resume_pdf_path"],
        job_description_text=payload["job_description"],
        job_title=payload.get("job_title"),
        company=payload.get("company"),
    )

    # Downstream: pass these objects into skill extraction, gap analysis, etc.
    return {
        "resume_xml": resume_xml,
        "job_profile": job_profile,
    }
