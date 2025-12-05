"""Utilities for cleaning LLM payloads and parsing XML skill lists."""

from __future__ import annotations

from xml.etree import ElementTree as ET


def strip_code_fence(payload: str) -> str:
    """Remove triple-backtick fences, keeping the enclosed content."""

    cleaned = (payload or "").strip()
    fence = "```"
    if fence not in cleaned:
        return cleaned
    start = cleaned.find(fence) + len(fence)
    candidate = cleaned[start:]
    # Handle ```xml code fences without disrupting other languages.
    candidate_lower = candidate.lower()
    if candidate_lower.startswith("xml"):
        candidate = candidate[3:]
    end = candidate.find(fence)
    return candidate[:end].strip() if end != -1 else candidate.strip()


def extract_xml_fragment(payload: str, root_tag: str) -> str:
    """Return the substring that contains the requested XML root tag."""

    cleaned = strip_code_fence(payload)
    open_tag = f"<{root_tag}"
    close_tag = f"</{root_tag}>"
    if open_tag in cleaned and close_tag in cleaned:
        begin = cleaned.find(open_tag)
        finish = cleaned.rfind(close_tag) + len(close_tag)
        return cleaned[begin:finish]
    return cleaned


def parse_skill_entries(
    xml_payload: str,
    *,
    root_tag: str,
    error_prefix: str | None = None,
) -> list[dict[str, int]]:
    """Parse `<skill>` nodes underneath the provided root tag."""

    try:
        root = ET.fromstring(xml_payload)
    except ET.ParseError as exc:  # pragma: no cover
        prefix = error_prefix or "Skill XML"
        raise RuntimeError(f"{prefix} is not valid XML:\n{xml_payload}") from exc

    skills: list[dict[str, int]] = []
    for skill_node in root.findall("./skill"):
        name = (skill_node.findtext("name") or "").strip()
        level_text = (skill_node.findtext("level") or "0").strip()
        if not name:
            continue
        try:
            level = max(0, min(3, int(level_text)))
        except ValueError:
            level = 0
        skills.append({"name": name, "level": level})
    return skills
