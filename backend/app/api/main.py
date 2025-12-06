"""FastAPI entrypoint exposing the analysis workflow."""

from __future__ import annotations

import shutil
from dataclasses import asdict
from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from ..workflow import WorkflowArtifacts, analyze_inputs

app = FastAPI(title="Resume Readiness Intelligence Engine")

# Allow local static frontends (file:// or localhost) to call the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


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

    job_description = payload.get("job_description")
    if not job_description:
        raise HTTPException(status_code=422, detail="job_description is required.")

    result: WorkflowArtifacts = analyze_inputs(
        resume_pdf_path=payload["resume_pdf_path"],
        job_description_text=job_description,
    )

    return asdict(result)


@app.post("/analyze-upload")
async def analyze_upload(
    resume_pdf: UploadFile = File(...),
    job_description: str = Form(...),
) -> dict[str, object]:
    """Accept an uploaded PDF + pasted job description, run the workflow, and return the study plan."""

    if not resume_pdf.filename:
        raise HTTPException(status_code=400, detail="A resume PDF must be provided.")
    # Persist the uploaded PDF temporarily so downstream parsers can read it.
    with NamedTemporaryFile(suffix=Path(resume_pdf.filename).suffix or ".pdf", delete=False) as tmp:
        tmp_path = Path(tmp.name)
        try:
            shutil.copyfileobj(resume_pdf.file, tmp)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Failed to read uploaded file: {exc}") from exc

    try:
        result: WorkflowArtifacts = analyze_inputs(
            resume_pdf_path=str(tmp_path),
            job_description_text=job_description,
        )
    except Exception as exc:  # pragma: no cover - runtime protection
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}") from exc
    finally:
        try:
            tmp_path.unlink(missing_ok=True)
        except Exception:
            pass

    return {
        "study_plan": result.study_plan,
        "job_skills": result.job_skills,
        "resume_skills": result.resume_skills,
        "skill_gap_xml": result.skill_gap_xml,
    }
