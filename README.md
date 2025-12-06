# Resume Readiness Intelligence Engine

Resume Readiness Intelligence Engine(RRIE) is a web-based application that uses agentic AI, RAG, and targeted learning pathways to help job seekers evaluate their readiness for specific roles and grow the knowledge they are missing. Unlike tools focused on “gaming” interviews, our mission is to enable real skill development through structured learning, curated resources, and personalized practice.

Developed by:

* Sripad Karne 
* Pranav Kandula 
* Alexandre Edouard Eleuthe Sepulveda de Dietrich

## **Problem Statement**

Job seekers, especially in Data Science, Machine Learning, and AI Engineering, often struggle to assess whether they are qualified for a role and to identify the skills they need to improve. Existing AI tools generate answers but don’t actually teach.

Our solution:

A Job Readiness Intelligence Engine that evaluates a user's current skills, detects knowledge gaps, and generates targeted study pathways using high-quality, credible resources. No shortcuts. True knowledge growth.

## **Intended Users**

**Primary users (MVP scope):**

* Data Science candidates

* Machine Learning Engineer candidates

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





















