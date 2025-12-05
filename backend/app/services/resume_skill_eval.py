"""LLM-powered skill scoring based on parsed résumé data.

Example
-------
>>> from backend.app.services.resume_parser import parse_resume_pdf
>>> resume_xml = parse_resume_pdf("demo/resume_parsing/Resume_ASDD_CSxCU.pdf")
>>> skills = evaluate_resume_skills(resume_xml)
>>> skills["skills"][0]["level"]
2
"""

from __future__ import annotations

import textwrap
from typing import Iterable
from xml.etree import ElementTree as ET

from langchain_groq import ChatGroq

from ..config import settings


def evaluate_resume_skills(
    resume_xml: str,
    *,
    llm_client: ChatGroq | None = None,
    model: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> dict:
    """Return a dictionary with skill names and mastery levels 0-3."""

    prompt = _build_prompt(resume_xml)
    xml_payload = _invoke_llm(
        prompt,
        llm_client=llm_client,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return _xml_to_skill_dict(xml_payload)


def _build_prompt(resume_xml: str) -> str:
    resume_data = _extract_resume_struct(resume_xml)
    # Provide a concrete reference so the model knows how to structure XML + scores.
    few_shot_context = textwrap.dedent(
        """
        <example>
          <context>
            Languages: Python, SQL, R
            Experience:
              * Data Science Intern — Built XGBoost and logistic regression churn models
              * ML Research Assistant — Implemented BERT NLP model and topic modeling pipelines
            Projects:
              * Music Genre Classifier — TensorFlow CNN with 88% accuracy
              * Price Optimization Engine — Ridge regression and random forest
            Tools: AWS, Databricks, Spark, Tableau
          </context>
          <skillsEvaluation>
            <skill><name>Machine Learning</name><level>3</level></skill>
            <skill><name>XGBoost</name><level>2</level></skill>
            <skill><name>Logistic Regression</name><level>2</level></skill>
            <skill><name>PyTorch</name><level>1</level></skill>
            <skill><name>TensorFlow</name><level>2</level></skill>
            <skill><name>Data Visualization</name><level>2</level></skill>
            <skill><name>SQL</name><level>2</level></skill>
            <skill><name>AWS</name><level>1</level></skill>
          </skillsEvaluation>
        </example>
        """
    ).strip()

    # Collect the resume content the LLM should consider.
    sections = [
        "Résumé skill categories:",
        _format_skill_section(resume_data.get("skills", [])),
        "\nRésumé experience bullets:",
        _format_nested_bullets(resume_data.get("experience", []), "position", "bullets"),
        "\nRésumé projects:",
        _format_nested_bullets(resume_data.get("projects", []), "name", "bullets"),
    ]
    context = "\n".join(section for section in sections if section).strip()
    instructions = textwrap.dedent(
        """
        You are evaluating the candidate's technical mastery for data science positions. Based on the résumé context,
        output an XML payload following this schema:

        <skillsEvaluation>
          <skill>
            <name>Skill Name</name>
            <level>0-3</level>
          </skill>
        </skillsEvaluation>

        Scoring rubric:
        - 0 = no evidence / not mentioned
        - 1 = basic exposure (single mention or coursework)
        - 2 = intermediate (used in projects or multiple bullets)
        - 3 = expert (deep experience, leadership, or repeated impact)

        List up to 25 distinct skills (max 3 words each). Avoid duplicates and non-technical traits.
        Return only XML, no commentary.
        """
    ).strip()
    return f"{instructions}\n\nFew-shot reference:\n{few_shot_context}\n\nRésumé context:\n{context}"


def _format_skill_section(skills: Iterable[dict]) -> str:
    lines: list[str] = []
    for category in skills or []:
        category_name = category.get("name") or "General"
        items = ", ".join(category.get("skills") or [])
        if items:
            lines.append(f"- {category_name}: {items}")
    return "\n".join(lines)


def _format_nested_bullets(items: Iterable[dict], title_key: str, bullets_key: str) -> str:
    lines: list[str] = []
    for item in items or []:
        title = item.get(title_key)
        if title:
            lines.append(f"* {title}")
        for bullet in item.get(bullets_key, []):
            lines.append(f"  - {bullet}")
    return "\n".join(lines)


def _invoke_llm(
    prompt: str,
    *,
    llm_client: ChatGroq | None,
    model: str | None,
    temperature: float | None,
    max_tokens: int | None,
) -> str:
    # Reuse user-provided client when available, otherwise bootstrap one from config.
    client = llm_client or ChatGroq(
        model=model or settings.resume_parser_model,
        temperature=settings.resume_parser_temperature if temperature is None else temperature,
        max_tokens=max_tokens or settings.resume_parser_max_tokens,
        timeout=None,
        max_retries=2,
    )
    messages = [
        ("system", "You score résumé skills and return XML exactly as specified."),
        ("user", prompt),
    ]
    response = client.invoke(messages)
    return _extract_xml_fragment(response.content or "")


def _extract_xml_fragment(payload: str) -> str:
    cleaned = payload.strip()
    if "```" in cleaned:
        start = cleaned.find("```") + 3
        candidate = cleaned[start:]
        if candidate.lower().startswith("xml"):
            candidate = candidate[3:]
        end = candidate.find("```")
        cleaned = candidate[:end].strip() if end != -1 else candidate.strip()
    if "<skillsEvaluation" in cleaned and "</skillsEvaluation>" in cleaned:
        begin = cleaned.find("<skillsEvaluation")
        finish = cleaned.rfind("</skillsEvaluation>") + len("</skillsEvaluation>")
        cleaned = cleaned[begin:finish]
    return cleaned


def _xml_to_skill_dict(xml_payload: str) -> dict:
    # Parse the structured response and clamp level values into 0-3.
    try:
        root = ET.fromstring(xml_payload)
    except ET.ParseError as exc:  # pragma: no cover
        raise RuntimeError(f"LLM output is not valid XML:\n{xml_payload}") from exc

    skills = []
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

    return {"skills": skills}


__all__ = ["evaluate_resume_skills"]


def _extract_resume_struct(resume_xml: str) -> dict:
    """Parse the résumé XML into a lightweight structure for prompting."""

    try:
        root = ET.fromstring(resume_xml)
    except ET.ParseError as exc:  # pragma: no cover
        raise RuntimeError("Provided resume XML is invalid.") from exc

    def text_list(elements: Iterable[ET.Element]) -> list[str]:
        return [(elem.text or "").strip() for elem in elements if (elem.text or "").strip()]

    skills = [
        {
            "name": (category.get("name") or "General").strip(),
            "skills": text_list(category.findall("skill")),
        }
        for category in root.findall("./skills/category")
    ]

    def parse_section(xpath: str, title_key: str, bullets_xpath: str) -> list[dict]:
        entries = []
        for node in root.findall(xpath):
            entries.append(
                {
                    title_key: (node.findtext(title_key) or "").strip(),
                    "bullets": text_list(node.findall(bullets_xpath)),
                }
            )
        return entries

    experience = parse_section("./experience/job", "position", "description/bullet")
    projects = parse_section("./projects/project", "name", "description/bullet")

    return {
        "skills": skills,
        "experience": experience,
        "projects": projects,
    }
