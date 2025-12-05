# Sample Skill Extractor Prompt

Use this template when calling an LLM to score skills extracted from the résumé and job description. Replace the bracketed placeholders before sending the request.

```
You are an assistant that scores data-science skills on a 1-5 scale.

Candidate Resume Context:
{{ resume_context }}

Target Job Requirements:
{{ job_context }}

Instructions:
1. Identify unique technical skills from both contexts (<= 3 words each).
2. Score each skill from 1 (limited exposure) to 5 (expert) based only on the résumé evidence.
3. Return JSON of `{ "skill": str, "score": int }` entries and drop commentary.
```

Store additional prompt variations in this folder. Name files descriptively, e.g., `study_plan_prompt.md`, `rag_query_prompt.md`.
