# Requires pdfplumber (pip install pdfplumber)

import argparse
import json
import os
import sys
import textwrap
import urllib.error
import urllib.request
from typing import Optional
from xml.etree import ElementTree as ET

import pdfplumber

DEFAULT_ENDPOINT = "https://api.openai.com/v1/chat/completions"
DEFAULT_MODEL = "gpt-4o-mini"


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
        1. Skills section (grouped by category when possible).
        2. Work experience entries with position, company, dates, location, and bullet descriptions.
        3. Project entries with name, optional context, and descriptions.
        4. Education entries (degree, institution, dates, location) plus any explicit coursework.
        5. Any remaining noteworthy lines (place under <other>).

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
              <dates>...</dates>
              <location>...</location>
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
              <dates>...</dates>
              <location>...</location>
              <courses>
                <course>...</course>
              </courses>
            </entry>
          </education>
          <other>
            <line>...</line>
          </other>
        </resume>

        Always include every top-level section (even if empty) and escape XML special characters.
        """
    ).strip()
    resume_block = f"\n\nRésumé text:\n{resume_text}"
    return instruction + resume_block


def call_llm(
    api_key: str,
    model: str,
    endpoint: str,
    prompt: str,
    max_tokens: int = 2000,
) -> str:
    """
    Calls an OpenAI-compatible chat completion endpoint and returns the assistant text.
    """
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You convert resumes into structured XML."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens": max_tokens,
    }
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request) as response:
            result = json.load(response)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"LLM request failed: {exc.code} {exc.reason}\n{detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Failed to reach LLM endpoint: {exc}") from exc

    try:
        return result["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as exc:
        raise RuntimeError(f"Unexpected LLM response format: {result}") from exc


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
        "--api-key",
        help="API key for the OpenAI-compatible endpoint. "
        "Defaults to LLM_API_KEY or OPENAI_API_KEY environment variables.",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Model name to request (default: {DEFAULT_MODEL}).",
    )
    parser.add_argument(
        "--endpoint",
        default=DEFAULT_ENDPOINT,
        help=f"Chat completion endpoint URL (default: {DEFAULT_ENDPOINT}).",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=2000,
        help="Maximum number of tokens to request from the LLM (default: 2000).",
    )
    args = parser.parse_args(argv)

    api_key = args.api_key or os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        parser.error("An API key is required via --api-key or the LLM_API_KEY/OPENAI_API_KEY env var.")

    resume_text = extract_text_from_pdf(args.input_pdf_path)
    prompt = build_llm_prompt(resume_text)
    llm_output = call_llm(api_key, args.model, args.endpoint, prompt, args.max_tokens).strip()

    try:
        root = ET.fromstring(llm_output)
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

