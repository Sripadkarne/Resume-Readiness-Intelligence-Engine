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

* AI Engineer candidates

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

* Curated articles, videos, PDFs, and tutorials

The engine retrieves explanations, examples, and runnable insights—not generic fluff.

**3. Personalized Study Plans**

For every knowledge gap, the system generates:

* Sequenced study modules

* Videos + articles + textbook excerpts

* Hands-on exercises

* Timelines and difficulty progression

**4. Practice Question Generator**

We use agentic AI to produce:

* Targeted practice questions

* Increasing difficulty levels

* Answer explanations based on the RAG knowledge base

## **High-Level Architecture**

**Frontend:**
Built using Lovable (React-like UI).
Communicates with backend through REST API calls.

**Backend (GCP):**

* Cloud Run – hosts API server (FastAPI / Python)

* Vertex AI – embeddings, RAG retrieval, LLM generation

* Cloud Storage – raw documents for ingestion

* Firestore – user sessions, progress, study plans

* Cloud Functions (optional) – lightweight utilities

**RAG Pipeline:**

* Document ingestion

* Chunking & preprocessing

* Embedding generation

* Storage in vector DB (e.g., Vertex Matching Engine or self-hosted)

* Retrieval + reasoning layer

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
│── frontend/
│   ├── lovable/              # Optional Lovable export
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
Agent 1 [Skill Extractor Agent]
Input: Resume, Job Description
Output: List of Skills For Each

Goes to:


Agent 2[Skill Gap Agent]
Input: List of Skills from Each Document
Output: List of Skill Gaps

Goes to:

Agent 3[RAG Retrieval Agent]
Input: List of Skill Gaps
Output: Retrieved Relevant Info


Goes to:


Agent 4[Study Plan Generator Agent] [Will Have CoT & Deep Thinking for robust answers]
Input: Retrieved Relevant Info + [Relevant Context From Resume + Job Description]
Output: Personalized study plan with curated, high quality resources

 ```



## **Technical Specifications**

### **RAG**

In this Repo, and for our first steps, we can create the script to take in text and output the Vector DB. We can use non-GCP native tools(ie Transformers, Pinecone) to create the vector DB. When the user(ie the Professor) runs our final demo script, the Vector DB will either be downloaded by the Professor from GCP or we can upload it to Hugging Face Hub for easy access[Pranav & Alex, you guys figure this out]  

 * It looks like you should be able to create a vector DB locally without GCP, so finalize documents to use and create the script to create vector DB(looks like Pinecone, FAISS, or ChromaDB are good options) 
















