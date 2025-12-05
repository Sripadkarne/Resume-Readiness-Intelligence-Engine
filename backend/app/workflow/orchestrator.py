"""High-level pipeline wiring functional services together."""

from __future__ import annotations

from ..services import parse_resume_pdf


def analyze_inputs(
    *,
    resume_pdf_path: str,
    job_description_text: str | None = None,
) -> str:
    """Return structured résumé XML ready for downstream agents."""

    # job_description_text retained for compatibility but unused.
    return parse_resume_pdf(resume_pdf_path)


__all__ = ["analyze_inputs"]
