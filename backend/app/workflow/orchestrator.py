"""High-level pipeline that connects the individual services."""

from __future__ import annotations

from ..models import JobProfile, ResumeProfile
from ..services import JobParsingService, ResumeParsingService


class AnalysisOrchestrator:
    """Coordinates parsing for the résumé and job description inputs."""

    def __init__(
        self,
        *,
        resume_parser: ResumeParsingService | None = None,
        job_parser: JobParsingService | None = None,
    ) -> None:
        self.resume_parser = resume_parser or ResumeParsingService()
        self.job_parser = job_parser or JobParsingService()

    def analyze(
        self,
        *,
        resume_pdf_path: str,
        job_description_text: str,
        job_title: str | None = None,
        company: str | None = None,
    ) -> tuple[ResumeProfile, JobProfile]:
        """Return structured objects to feed into later agents."""

        resume_profile = self.resume_parser.parse_pdf(resume_pdf_path)
        job_profile = self.job_parser.parse_text(
            job_description_text,
            title=job_title,
            company=company,
        )
        return resume_profile, job_profile
