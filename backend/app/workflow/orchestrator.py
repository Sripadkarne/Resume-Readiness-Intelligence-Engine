"""High-level pipeline wiring functional services together."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..services import (
    evaluate_job_skills,
    evaluate_resume_skills,
    generate_skill_gap_xml,
    job_skills_to_dict,
    parse_resume_pdf,
)
from ..services.rag_agent import generate_study_plan, rag_chain as default_rag_chain

SkillDict = dict[str, int | str]


@dataclass(slots=True)
class WorkflowArtifacts:
    """Structured payload returned by the job readiness workflow."""

    resume_xml: str
    job_skill_xml: str
    job_skills: list[SkillDict]
    resume_skills: list[SkillDict]
    skill_gap_xml: str
    study_plan: str | None = None


def analyze_inputs(
    *,
    resume_pdf_path: str,
    job_description_text: str,
    rag_chain: Any | None = None,
    fail_on_rag_error: bool = False,
) -> WorkflowArtifacts:
    """Return the parsed résumé, skill scores, and optional study plan."""

    if not job_description_text:
        raise ValueError("job_description_text must be provided for analysis.")

    resume_xml = parse_resume_pdf(resume_pdf_path)

    job_skill_xml = evaluate_job_skills(job_description_text)
    job_skills = job_skills_to_dict(job_skill_xml)["skills"]

    resume_eval = evaluate_resume_skills(resume_xml, job_skill_targets=job_skills)
    resume_skills = resume_eval.get("skills", [])

    skill_gap_xml = generate_skill_gap_xml(
        job_skills=job_skills,
        resume_skills=resume_skills,
    )

    rag = rag_chain if rag_chain is not None else default_rag_chain
    study_plan: str | None

    if rag is None:
        if fail_on_rag_error:
            raise RuntimeError(
                "RAG chain is required to generate the study plan but is unavailable. "
                "Verify backend/app/services/rag_agent.py."
            )
        study_plan = _rag_error_message("RAG agent is unavailable.")
    else:
        try:
            if rag is default_rag_chain:
                study_plan = generate_study_plan(skill_gap_xml)
            else:
                study_plan = rag.invoke(skill_gap_xml)
        except Exception as exc:
            if fail_on_rag_error:
                raise
            study_plan = _rag_error_message(f"RAG retrieval failed: {exc}")

    return WorkflowArtifacts(
        resume_xml=resume_xml,
        job_skill_xml=job_skill_xml,
        job_skills=job_skills,
        resume_skills=resume_skills,
        skill_gap_xml=skill_gap_xml,
        study_plan=study_plan,
    )


def _rag_error_message(reason: str) -> str:
    """Return a human-readable fallback when the RAG agent fails but workflow continues."""

    return (
        "The RAG agent could not generate a study plan at this time. "
        f"Reason: {reason}"
    )


__all__ = ["WorkflowArtifacts", "analyze_inputs"]
