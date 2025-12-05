"""High-level pipeline wiring functional services together."""

from __future__ import annotations

from ..models import JobProfile, ResumeProfile
from ..services import parse_job_description, parse_resume_pdf


def analyze_inputs(
    *,
    resume_pdf_path: str,
    job_description_text: str,
    job_title: str | None = None,
    company: str | None = None,
    default_job_title: str | None = None,
    default_company: str | None = None,
) -> tuple[ResumeProfile, JobProfile]:
    """Return structured résumé and job profiles ready for downstream agents."""

    resume_profile = parse_resume_pdf(resume_pdf_path)
    job_profile = parse_job_description(
        job_description_text,
        title=job_title,
        company=company,
        default_title=default_job_title,
        default_company=default_company,
    )
    return resume_profile, job_profile


__all__ = ["analyze_inputs"]
