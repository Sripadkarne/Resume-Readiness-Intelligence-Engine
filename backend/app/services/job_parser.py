"""Utilities for normalizing job descriptions into :class:`JobProfile` objects.

Example
-------
>>> jd_text = "Data Scientist at Example AI\nResponsibilities:\n- Build ML models\nRequirements:\n- Python\n- SQL"
>>> service = JobParsingService(default_title="Data Scientist")
>>> job = service.parse_text(jd_text)
>>> job.required_skills
['Python', 'SQL']
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from ..models import JobProfile


@dataclass(slots=True)
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


class JobParsingService:
    """Heuristic job-description parser meant for lightweight preprocessing."""

    def __init__(self, *, default_title: str | None = None, default_company: str | None = None) -> None:
        self.default_title = default_title
        self.default_company = default_company
        self.aliases = SectionAliases()

    def parse_text(
        self,
        job_text: str,
        *,
        title: str | None = None,
        company: str | None = None,
    ) -> JobProfile:
        sections = self._split_sections(job_text)
        responsibilities = self._normalize_items(sections.get("responsibilities", []))
        required = self._normalize_items(sections.get("requirements", []))
        nice_to_have = self._normalize_items(sections.get("nice_to_have", []))

        summary_lines = sections.get("summary", [])
        summary = " ".join(summary_lines[:2]).strip() or None

        return JobProfile(
            title=title or self.default_title,
            company=company or self.default_company,
            summary=summary,
            responsibilities=responsibilities,
            required_skills=required,
            nice_to_have_skills=nice_to_have,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _split_sections(self, text: str) -> dict[str, list[str]]:
        sections: dict[str, list[str]] = {"summary": []}
        current = "summary"
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            normalized_header = line.rstrip(":").lower()
            new_section = self._match_section(normalized_header)
            if new_section:
                current = new_section
                sections.setdefault(current, [])
                continue
            sections.setdefault(current, []).append(line)
        return sections

    def _match_section(self, header: str) -> str | None:
        if header in self.aliases.responsibilities:
            return "responsibilities"
        if header in self.aliases.requirements:
            return "requirements"
        if header in self.aliases.nice_to_have:
            return "nice_to_have"
        return None

    @staticmethod
    def _normalize_items(lines: Iterable[str]) -> list[str]:
        normalized: list[str] = []
        for line in lines:
            cleaned = line.lstrip("-*• \t").strip()
            if not cleaned:
                continue
            normalized.append(cleaned)
        return normalized
