"""LLM helper to summarize job-description skills as XML."""

from __future__ import annotations

import textwrap
from langchain_groq import ChatGroq

from ..config import settings
from ..utils import extract_xml_fragment, parse_skill_entries


def evaluate_job_skills(
    job_description_text: str,
    *,
    llm_client: ChatGroq | None = None,
    model: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> str:
    """Return an XML payload of required skills and levels for the given job description."""

    prompt = _build_prompt(job_description_text)
    return _invoke_llm(
        prompt,
        llm_client=llm_client,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )


def _build_prompt(job_text: str) -> str:
    few_shot = textwrap.dedent(
        """
        <example>
          <jobDescription>
            Data Science Intern at Spotify. Responsibilities include building churn models with XGBoost and logistic regression,
            developing PySpark ETL pipelines on Databricks, running A/B tests, and presenting dashboards in Tableau.
            Qualifications: Python, SQL, ML, Deep Learning, AWS, Spark, experimentation experience.
          </jobDescription>
          <jobSkills>
            <skill><name>Machine Learning</name><level>3</level></skill>
            <skill><name>XGBoost</name><level>3</level></skill>
            <skill><name>PySpark</name><level>3</level></skill>
            <skill><name>Databricks</name><level>2</level></skill>
            <skill><name>SQL</name><level>3</level></skill>
            <skill><name>A/B Testing</name><level>2</level></skill>
            <skill><name>Tableau</name><level>1</level></skill>
            <skill><name>AWS</name><level>1</level></skill>
          </jobSkills>
        </example>
        """
    ).strip()

    instructions = textwrap.dedent(
        """
        You analyze job descriptions for data science roles and output XML in this format:

        <jobSkills>
          <skill>
            <name>Skill Name</name>
            <level>0-3</level>
          </skill>
        </jobSkills>

        Interpret responsibility bullets and qualification lists to score each technical skill:
        - 0 = barely relevant / optional mention
        - 1 = nice to have / minor tool
        - 2 = important but not core
        - 3 = critical / repeatedly emphasized requirement

        Extract up to 25 unique skills (<=3 words each). Prioritize programming languages, ML tools, data platforms, and experimentation skills.
        Produce only XML with the schema above.
        """
    ).strip()

    return f"{instructions}\n\nFew-shot reference:\n{few_shot}\n\nJob description:\n{job_text.strip()}"


def _invoke_llm(
    prompt: str,
    *,
    llm_client: ChatGroq | None,
    model: str | None,
    temperature: float | None,
    max_tokens: int | None,
) -> str:
    client = llm_client or ChatGroq(
        model=model or settings.resume_parser_model,
        temperature=settings.resume_parser_temperature if temperature is None else temperature,
        max_tokens=max_tokens or settings.resume_parser_max_tokens,
        timeout=None,
        max_retries=2,
    )
    messages = [
        ("system", "You summarize job descriptions into XML skills with 0-3 priority levels."),
        ("user", prompt),
    ]
    response = client.invoke(messages)
    return extract_xml_fragment(response.content or "", "jobSkills")


def job_skills_to_dict(xml_payload: str) -> dict:
    """Parse the `<jobSkills>` XML into a `{ 'skills': [...] }` structure."""

    skills = parse_skill_entries(xml_payload, root_tag="jobSkills", error_prefix="Job skill XML")
    return {"skills": skills}


__all__ = ["evaluate_job_skills", "job_skills_to_dict"]
