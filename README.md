# Resume Readiness Intelligence Engine

AI assistant that analyzes a résumé and job description, detects skill gaps, retrieves learning resources, and generates a 4-week study plan.

## Quickstart

Requirements: Python 3.11+ and a Groq API key.

1) Install deps  
   ```bash
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```
   (Or `make install`.)

2) Configure env (`.env` in repo root)  
   ```
   GROQ_API_KEY=your_key_here
   # Optional overrides: RAG_MODEL, RAG_PERSIST_DIR, RAG_COLLECTION_NAME, RAG_EMBEDDING_MODEL, RAG_TOP_K, RESUME_PARSER_MODEL, RESUME_PARSER_TEMPERATURE
   ```

3) Run backend  
   ```bash
   uvicorn backend.app.api.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   (Or `make run-backend`.)

4) Serve frontend  
   ```bash
   python -m http.server 3000 --directory frontend
   ```
   Visit `http://localhost:3000` and upload a résumé PDF + paste a job description.

## How it works (pipeline)

1) Résumé → XML (`resume_parser.py`)  
2) Job skills (LLM) → `<jobSkills>` XML (`job_skill_eval.py`)  
3) Résumé skills (LLM) → `<skillsEvaluation>` XML (`resume_skill_eval.py`)  
4) Skill gaps → `<skillGaps>` XML (`skill_gap_eval.py`)  
5) RAG study plan: retrieve from Chroma (`VectorDB/`), generate 4-week plan (`rag_agent.py`)  
6) API (`backend/app/api/main.py`) returns:
   - `study_plan` (markdown), `plan_structured` (weeks/tasks/resources), `plan_reasoning`
   - job/resume skills and gap XML

## API endpoints

- `GET /health` — uptime probe  
- `POST /analyze` — accepts JSON `{ resume_pdf_path, job_description }`  
- `POST /analyze-upload` — multipart form (`resume_pdf`, `job_description`) used by the frontend

<<<<<<< HEAD
## Frontend

Static HTML/CSS/JS (`frontend/index.html`), no build step. Fetches `POST /analyze-upload`. Views: Study Plan, Structured, Raw, Reasoning.

## Project structure

```
backend/app/api/              # FastAPI entrypoint
backend/app/workflow/         # Orchestrator wiring services
backend/app/services/         # Resume/job skill eval, skill gap, RAG agent
backend/app/utils/            # XML helpers
frontend/                     # Static UI
VectorDB/                     # Chroma persistence (local)
docs/                         # Brief, appendix, deliverables checklist
Makefile                      # install/run helpers
requirements.txt
```

## Deliverables
=======
**Planned expansion:**

* Software Engineering

* Finance

* Mechanical Engineering

**Additional technical and non-technical career paths**

* Both entry-level and senior candidates

## **MVP Features**

**1. Skill Gap Detection**

Users upload their resume or answer domain-specific questions.

* Our system:

  * Analyzes skills, tools, and domain knowledge

  * Compares them to real job requirements

  * Returns structured “knowledge gap” outputs

**2. RAG-Based Knowledge Retrieval**

The RAG database is built from credible sources:

* ML & Statistics textbooks

* Ace the Data Science Interview

* Applied DS/ML/AI resources

* Articles, videos, PDFs, and tutorials (Domain Specific)

The engine retrieves explanations, examples, and runnable insights—not generic fluff.

**3. Personalized Study Plans**

For every knowledge gap, the system generates:

* Sequenced study modules from videos, articles, and textbook excerpts

* Timelines and difficulty progression

## **High-Level Architecture**

**Frontend:**
Built using HTML and JavaScript.
Communicates with backend through Fast API calls.

**Backend:**

* Fast API, Python

* Inference - Groq

* Model - llama-3.1-8b-instant

**RAG Pipeline:**

* Textbook into markdown using Cloud GPUs

* Chunking & preprocessing by header

* Sentence transformer embedding (all-MiniLM-L6-v2)

* Storage in vector DB (ChromaDB)

* Langchain

* Retrieval (Precision(k=3)) + Generation 

Repository Structure (Proposed)

```
resumejobhelpai/
│── backend/
│   ├── main.py               
│   ├── rag/
│   │   ├── ingest.py
│   │   ├── chunking.py
│   │   ├── embed.py
│   │   ├── retrieve.py
│   ├── agents/
│   ├── Dockerfile
│   ├── requirements.txt
│
│── frontend              
│
│── docs/
│   ├── architecture.md
│   ├── api.md
│   ├── infra.md
│
└── README.md
```

Agentic Workflow 

```
Agent 1 [PDF converter]
Input: Resume
Output: XML of resume

Goes to:


Agent 2[Job description Skills]
Input: Job description
Output: Skill and proficiency requirements for the specific job

Goes to:

Agent 3[Resume Skills]
Input: XML of resume
Output: Skill and proficiency requirments with respect to the skills outlined from agent 2


Goes to:


Python function to get the gaps
Input: Skills 
Output: Gaps

Goes to:


Agent 4[RAG + Study Plan]
Input: Skill gaps
Output: Study plan to get proficient in the necessary skills


 ```


















>>>>>>> 180718058884418c4348910dd69b4a0700e895ef

- Working prototype (steps above; Makefile included)
- Product brief: `docs/product_brief.md`
- Technical appendix: `docs/technical_appendix.md`
- Deliverables checklist: `docs/deliverables.md`
- Add your deck and demo video to `docs/` or link them in `docs/deliverables.md`

## Notes

- Defaults use HuggingFace `all-MiniLM-L6-v2` embeddings with Chroma. Override paths/models via env vars if needed.
- `main` is protected; merge changes via PR.
