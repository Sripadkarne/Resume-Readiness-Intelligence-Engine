# Requires pdfplumber (pip install pdfplumber)
# Requires langchain-groq (pip install langchain-groq)

import argparse
import os
import sys
import textwrap
from typing import Optional
from xml.etree import ElementTree as ET

import pdfplumber
from langchain_groq import ChatGroq

DEFAULT_MODEL = "llama-3.1-8b-instant"


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts raw text from the PDF and lightly normalizes whitespace.
    """
    text_chunks = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_chunks.append(page_text)
    combined = "\n\n".join(text_chunks)
    normalized_lines = []
    for raw_line in combined.splitlines():
        squashed = " ".join(raw_line.split())
        normalized_lines.append(squashed)
    normalized = "\n".join(line for line in normalized_lines if line)
    return normalized.strip()


def build_llm_prompt(resume_text: str) -> str:
    """
    Creates the instruction prompt for the LLM, requesting structured XML output.
    """
    instruction = textwrap.dedent(
        """
        You are a résumé parsing assistant. Given the raw résumé text below, extract:
        1. Skills section (grouped by category when possible). Only include technical skills/tools/frameworks; drop human language proficiency entries.
        2. Work experience entries with position, company, and bullet descriptions (omit any dates or locations entirely).
        3. Project entries with name, optional context, and descriptions.
        4. Education entries (degree, institution) plus any explicit coursework. Omit dates and location
        5. Any remaining noteworthy lines (place under <other>), excluding personal identifiers.

        Output well-formed XML that matches this structure exactly:

        <resume>
          <skills>
            <category name="Category Name">
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

        Always include every top-level section (even if empty) and escape XML special characters. Do not introduce <dates> or <location> elements anywhere, avoid language-only skill categories, and never output names, phone numbers, emails, or addresses.
        """
    ).strip()
    resume_block = f"\n\nRésumé text:\n{resume_text}"
    return instruction + resume_block


def call_llm(llm: ChatGroq, prompt: str) -> str:
    """
    Calls the Groq-hosted LLM using the same structure as backend/Agents/skillextractor.py.
    """
    messages = [
        (
            "system",
            "You convert resumes into structured XML that matches the requested schema exactly.",
        ),
        ("user", prompt),
    ]
    response = llm.invoke(messages)
    return response.content.strip()


def _indent(elem: ET.Element, level: int = 0) -> None:
    """
    Pretty-print helper for ElementTree output.
    """
    indent_unit = "  "
    indent_text = "\n" + level * indent_unit
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = indent_text + indent_unit
        for child in elem:
            _indent(child, level + 1)
            if not child.tail or not child.tail.strip():
                child.tail = indent_text + indent_unit
        if not elem.tail or not elem.tail.strip():
            elem.tail = indent_text
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = indent_text


def summarize_xml(root: ET.Element) -> str:
    """
    Derives a simple textual summary from the generated XML.
    """
    def count(path: str) -> int:
        return len(root.findall(path))

    categories = count("./skills/category")
    experiences = count("./experience/job")
    projects = count("./projects/project")
    education_entries = count("./education/entry")
    return (
        f"skill categories: {categories}, experiences: {experiences}, "
        f"projects: {projects}, education entries: {education_entries}"
    )


def extract_xml_fragment(text: str) -> str:
    """
    Strip markdown/code fences or prose surrounding the XML payload.
    """
    cleaned = text.strip()
    if "```" in cleaned:
        fence_start = cleaned.find("```")
        after_fence = cleaned[fence_start + 3 :]
        if after_fence.lower().startswith("xml"):
            after_fence = after_fence[3:]
        fence_end = after_fence.find("```")
        if fence_end != -1:
            cleaned = after_fence[:fence_end].strip()
        else:
            cleaned = after_fence.strip()
    if "<resume" in cleaned and "</resume>" in cleaned:
        start = cleaned.find("<resume")
        end = cleaned.rfind("</resume>") + len("</resume>")
        cleaned = cleaned[start:end]
    return cleaned.strip()


def main(argv: Optional[list[str]] = None) -> None:
    parser = argparse.ArgumentParser(
        description="Convert a résumé PDF into structured XML using an LLM.",
    )
    parser.add_argument("input_pdf_path", help="Path to the PDF résumé.")
    parser.add_argument(
        "output_xml_path",
        nargs="?",
        default="resume_parsed.xml",
        help="Where to write the XML output (default: resume_parsed.xml).",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Model name to request (default: {DEFAULT_MODEL}).",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=2000,
        help="Maximum number of tokens to request from the LLM (default: 2000).",
    )
    parser.add_argument(
        "--api-key",
        help="Optional GROQ_API_KEY override; otherwise the environment variable must be set.",
    )
    args = parser.parse_args(argv)

    if args.api_key:
        os.environ["GROQ_API_KEY"] = args.api_key
    if "GROQ_API_KEY" not in os.environ or not os.environ["GROQ_API_KEY"]:
        parser.error("Set GROQ_API_KEY in the environment or pass --api-key.")

    llm = ChatGroq(
        model=args.model,
        temperature=0,
        max_tokens=args.max_tokens,
        timeout=None,
        max_retries=2,
    )

    resume_text = extract_text_from_pdf(args.input_pdf_path)
    prompt = build_llm_prompt(resume_text)
    llm_output = call_llm(llm, prompt)
    xml_payload = extract_xml_fragment(llm_output)

    try:
        root = ET.fromstring(xml_payload)
    except ET.ParseError as exc:
        raise RuntimeError(f"LLM output is not valid XML:\n{llm_output}") from exc

    _indent(root)
    tree = ET.ElementTree(root)
    tree.write(args.output_xml_path, encoding="utf-8", xml_declaration=True)
    print(f"Wrote {args.output_xml_path} ({summarize_xml(root)})")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
