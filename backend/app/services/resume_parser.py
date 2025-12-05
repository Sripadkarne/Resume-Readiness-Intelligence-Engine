"""Functional résumé parsing helpers returning XML strings.

Example
-------
>>> xml_string = parse_resume_pdf("backend/Agents_wip/resume_parsing/resume_pdf/Resume_ASDD_CSxCU.pdf")
>>> xml_string.startswith("<?xml")
True
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pdfplumber
from langchain_groq import ChatGroq

from ..config import settings
from ..utils import extract_xml_fragment


def parse_resume_pdf(
    pdf_path: str | Path,
    *,
    llm_client: ChatGroq | None = None,
    model: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> str:
    """Convert a résumé PDF into an XML string."""

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
) -> str:
    """Run parsing on already extracted plain text (useful for tests)."""

    prompt = _build_llm_prompt(resume_text)
    xml_payload = _invoke_llm(
        prompt,
        llm_client=llm_client,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return xml_payload


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
        5. Do not include any personally identifiable information (names, emails, phone numbers, addresses).
        6. Omit any skill that is not technical or related to data science positions. Do not include language or soft skills.
        7. Any additional noteworthy bullet points under an <other> section.

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
    return extract_xml_fragment(response.content or "", "resume")


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


__all__ = ["parse_resume_pdf", "parse_resume_text"]
