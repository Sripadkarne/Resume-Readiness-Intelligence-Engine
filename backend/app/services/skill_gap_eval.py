"""Skill gap computation utilities that emit XML summaries."""

from __future__ import annotations

from typing import Iterable
from xml.etree import ElementTree as ET

SkillDict = dict[str, int | str]


def generate_skill_gap_xml(
    *,
    job_skills: Iterable[SkillDict],
    resume_skills: Iterable[SkillDict],
) -> str:
    """Return an XML payload describing the gap between required and current levels."""

    gaps = _calculate_skill_gaps(job_skills=job_skills, resume_skills=resume_skills)
    root = ET.Element("skillGaps")
    for gap in gaps:
        skill_el = ET.SubElement(root, "skill")
        ET.SubElement(skill_el, "name").text = gap["name"]
        ET.SubElement(skill_el, "currentLevel").text = str(gap["current_level"])
        ET.SubElement(skill_el, "gap").text = str(gap["gap"])
    return _serialize_xml(root)


def _calculate_skill_gaps(
    *,
    job_skills: Iterable[SkillDict],
    resume_skills: Iterable[SkillDict],
) -> list[dict[str, int | str]]:
    """Normalize skills, align them by name, and compute the required/current difference.

    Skill names are lower-cased so downstream consumers can compare strings directly.
    """

    resume_lookup: dict[str, int] = {}
    for skill in resume_skills or []:
        name = str(skill.get("name") or "").strip().lower()
        if not name:
            continue
        level = _safe_level(skill.get("level"))
        resume_lookup[name] = level

    gaps: list[dict[str, int | str]] = []
    for job_skill in job_skills or []:
        job_name = (job_skill.get("name") or "").strip().lower()
        if not job_name:
            continue
        required_level = _safe_level(job_skill.get("level"))
        current_level = resume_lookup.get(job_name, 0)
        gaps.append(
            {
                "name": job_name,
                "current_level": current_level,
                "gap": required_level - current_level,
            }
        )
    return gaps


def _safe_level(value: int | str | None) -> int:
    try:
        numeric = int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        numeric = 0
    return max(0, min(3, numeric))


def _serialize_xml(root: ET.Element) -> str:
    """Convert an ElementTree to a nicely formatted XML string."""

    _indent_xml(root)
    return ET.tostring(root, encoding="unicode")


def _indent_xml(elem: ET.Element, level: int = 0) -> None:
    padding = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = padding + "  "
        for child in elem:
            _indent_xml(child, level + 1)
        if not child.tail or not child.tail.strip():
            child.tail = padding
    if level and (not elem.tail or not elem.tail.strip()):
        elem.tail = padding
    elif not level and (not elem.tail or not elem.tail.strip()):
        elem.tail = "\n"


__all__ = ["generate_skill_gap_xml"]
