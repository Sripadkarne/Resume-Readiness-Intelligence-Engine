"""Functional helpers for normalizing job descriptions.

Example
-------
>>> jd_text = "Data Scientist\\nResponsibilities:\\n- Build ML models\\nRequirements:\\n- Python\\n- SQL"
>>> job = parse_job_description(jd_text, default_title="Data Scientist")
>>> job.required_skills
['Python', 'SQL']
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from ..models import JobProfile


@dataclass(frozen=True, slots=True)
class SectionAliases:
    responsibilities: tuple[str, ...] = (
        "responsibilities",
        "what you'll do",
        "what you will do",
        "your impact",
    )
    requirements: tuple[str, ...] = (
        "requirements",
        "qualifications",
        "basic qualifications",
        "must haves",
    )
    nice_to_have: tuple[str, ...] = (
        "preferred qualifications",
        "nice to have",
        "bonus points",
    )


DEFAULT_ALIASES = SectionAliases()


def parse_job_description(
    job_text: str,
    *,
    title: str | None = None,
    company: str | None = None,
    default_title: str | None = None,
    default_company: str | None = None,
    section_aliases: SectionAliases = DEFAULT_ALIASES,
) -> JobProfile:
    """Return a :class:`JobProfile` built from raw job-description text."""

    sections = _split_sections(job_text, section_aliases)
    responsibilities = _normalize_items(sections.get("responsibilities", []))
    required = _normalize_items(sections.get("requirements", []))
    nice_to_have = _normalize_items(sections.get("nice_to_have", []))

    summary_lines = sections.get("summary", [])
    summary = " ".join(summary_lines[:2]).strip() or None

    return JobProfile(
        title=title or default_title,
        company=company or default_company,
        summary=summary,
        responsibilities=responsibilities,
        required_skills=required,
        nice_to_have_skills=nice_to_have,
    )


def _split_sections(text: str, section_aliases: SectionAliases) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {"summary": []}
    current = "summary"
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        normalized_header = line.rstrip(":").lower()
        new_section = _match_section(normalized_header, section_aliases)
        if new_section:
            current = new_section
            sections.setdefault(current, [])
            continue
        sections.setdefault(current, []).append(line)
    return sections


def _match_section(header: str, section_aliases: SectionAliases) -> str | None:
    if header in section_aliases.responsibilities:
        return "responsibilities"
    if header in section_aliases.requirements:
        return "requirements"
    if header in section_aliases.nice_to_have:
        return "nice_to_have"
    return None


def _normalize_items(lines: Iterable[str]) -> list[str]:
    normalized: list[str] = []
    for line in lines:
        cleaned = line.lstrip("-*• \t").strip()
        if cleaned:
            normalized.append(cleaned)
    return normalized


__all__ = ["parse_job_description", "SectionAliases"]
