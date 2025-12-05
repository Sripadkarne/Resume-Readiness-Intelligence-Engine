"""Functional résumé parsing helpers.

Example
-------
>>> profile = parse_resume_pdf("backend/Agents/resume_parsing/resume_pdf/Resume_ASDD_CSxCU.pdf")
>>> profile.skills[0].name
'Machine Learning'
"""

from __future__ import annotations

import textwrap
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree as ET

import pdfplumber
from langchain_groq import ChatGroq

from ..config import settings
from ..models import (
    EducationEntry,
    ExperienceEntry,
    ProjectEntry,
    ResumeProfile,
    SkillCategory,
)


def parse_resume_pdf(
    pdf_path: str | Path,
    *,
    llm_client: ChatGroq | None = None,
    model: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> ResumeProfile:
    """Convert a résumé PDF into a :class:`ResumeProfile`."""

    raw_text = _extract_text_from_pdf(Path(pdf_path))
    return parse_resume_text(
        raw_text,
        llm_client=llm_client,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )


def parse_resume_text(
    resume_text: str,
    *,
    llm_client: ChatGroq | None = None,
    model: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> ResumeProfile:
    """Run parsing on already extracted plain text (useful for tests)."""

    prompt = _build_llm_prompt(resume_text)
    xml_payload = _invoke_llm(
        prompt,
        llm_client=llm_client,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return _xml_to_profile(xml_payload, resume_text)


# ------------------------------------------------------------------
# Internals
# ------------------------------------------------------------------

def _extract_text_from_pdf(pdf_path: Path) -> str:
    text_chunks: list[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text_chunks.append(page.extract_text() or "")
    normalized_lines = [" ".join(line.split()) for line in "\n\n".join(text_chunks).splitlines()]
    condensed = "\n".join(line for line in normalized_lines if line)
    return condensed.strip()


def _build_llm_prompt(resume_text: str) -> str:
    instruction = textwrap.dedent(
        """
        You are a résumé parsing assistant. Given the raw résumé text below, extract:
        1. Skills grouped by category (only technical skills, tools, frameworks, and coursework).
        2. Work experiences (position, company, bullet descriptions). Omit dates and locations.
        3. Project entries with name, optional context, and bullet descriptions.
        4. Education entries with degree, institution, and explicit coursework.
        5. Any additional noteworthy bullet points under an <other> section.

        Return well-formed XML using this schema:
        <resume>
          <skills>
            <category name="Category">
              <skill>Example</skill>
            </category>
          </skills>
          <experience>
            <job>
              <position>...</position>
              <company>...</company>
              <description>
                <bullet>...</bullet>
              </description>
            </job>
          </experience>
          <projects>
            <project>
              <name>...</name>
              <context>...</context>
              <description>
                <bullet>...</bullet>
              </description>
            </project>
          </projects>
          <education>
            <entry>
              <degree>...</degree>
              <institution>...</institution>
              <courses>
                <course>...</course>
              </courses>
            </entry>
          </education>
          <other>
            <line>...</line>
          </other>
        </resume>

        Escape XML entities, never add <dates> or <locations>, and avoid personally identifiable information.
        """
    ).strip()
    return f"{instruction}\n\nRésumé text:\n{resume_text.strip()}"


def _invoke_llm(
    prompt: str,
    *,
    llm_client: ChatGroq | None,
    model: str | None,
    temperature: float | None,
    max_tokens: int | None,
) -> str:
    client = _resolve_llm(
        llm_client,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    messages = [
        ("system", "You convert resumes into structured XML that matches the requested schema exactly."),
        ("user", prompt),
    ]
    response = client.invoke(messages)
    return _extract_xml_fragment(response.content or "")


def _resolve_llm(
    llm_client: ChatGroq | None,
    *,
    model: str | None,
    temperature: float | None,
    max_tokens: int | None,
) -> ChatGroq:
    if llm_client:
        return llm_client
    return ChatGroq(
        model=model or settings.resume_parser_model,
        temperature=settings.resume_parser_temperature if temperature is None else temperature,
        max_tokens=max_tokens or settings.resume_parser_max_tokens,
        timeout=None,
        max_retries=2,
    )


def _extract_xml_fragment(payload: str) -> str:
    cleaned = payload.strip()
    if "```" in cleaned:
        start = cleaned.find("```") + 3
        candidate = cleaned[start:]
        if candidate.lower().startswith("xml"):
            candidate = candidate[3:]
        end = candidate.find("```")
        cleaned = candidate[:end].strip() if end != -1 else candidate.strip()
    if "<resume" in cleaned and "</resume>" in cleaned:
        begin = cleaned.find("<resume")
        finish = cleaned.rfind("</resume>") + len("</resume>")
        cleaned = cleaned[begin:finish]
    return cleaned


def _xml_to_profile(xml_payload: str, raw_text: str) -> ResumeProfile:
    try:
        root = ET.fromstring(xml_payload)
    except ET.ParseError as exc:  # pragma: no cover
        raise RuntimeError(f"LLM output is not valid XML:\n{xml_payload}") from exc

    skill_categories = [
        SkillCategory(
            name=(category.get("name") or "Uncategorized").strip(),
            skills=_text_list(category.findall("skill")),
        )
        for category in root.findall("./skills/category")
    ]

    experiences = [
        ExperienceEntry(
            position=(job.findtext("position") or "").strip(),
            company=(job.findtext("company") or "").strip() or None,
            bullets=_text_list(job.findall("description/bullet")),
        )
        for job in root.findall("./experience/job")
    ]

    projects = [
        ProjectEntry(
            name=(proj.findtext("name") or "").strip(),
            context=(proj.findtext("context") or "").strip() or None,
            bullets=_text_list(proj.findall("description/bullet")),
        )
        for proj in root.findall("./projects/project")
    ]

    education_entries = [
        EducationEntry(
            degree=(entry.findtext("degree") or "").strip(),
            institution=(entry.findtext("institution") or "").strip(),
            courses=_text_list(entry.findall("courses/course")),
        )
        for entry in root.findall("./education/entry")
    ]

    other_lines = _text_list(root.findall("./other/line"))

    return ResumeProfile(
        raw_text=raw_text,
        skills=skill_categories,
        experience=experiences,
        projects=projects,
        education=education_entries,
        other=other_lines,
    )


def _text_list(elements: Iterable[ET.Element]) -> list[str]:
    cleaned: list[str] = []
    for elem in elements:
        text = (elem.text or "").strip()
        if text:
            cleaned.append(text)
    return cleaned


__all__ = ["parse_resume_pdf", "parse_resume_text"]
