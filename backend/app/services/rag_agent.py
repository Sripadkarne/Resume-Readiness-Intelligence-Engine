"""RAG agent wiring that mirrors other backend services."""

from __future__ import annotations

from pathlib import Path

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from backend.app.config import settings

GROQ_MODEL_NAME = settings.rag_model
COLLECTION_NAME = settings.rag_collection_name
EMBEDDING_MODEL_NAME = settings.rag_embedding_model
EMBEDDING_K = settings.rag_top_k
CHROMA_DIR = settings.rag_persist_dir or str(
    Path.home() / "Resume-Readiness-Intelligence-Engine" / "VectorDB"
)

embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

# Vector Store (Your existing Chroma database)
vectorstore = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
    persist_directory=CHROMA_DIR,
)
retriever = vectorstore.as_retriever(k=EMBEDDING_K)  # Retrieve the top k relevant chunks

# LLM (The native LangChain wrapper for Groq)
llm = ChatGroq(
    model=GROQ_MODEL_NAME,
    temperature=settings.rag_temperature,
    groq_api_key=settings.groq_api_key,
)


def format_docs(docs: list[Document]) -> str:
    """Concatenates retrieved documents into a single context string."""
    return "\n\n---\n\n".join(doc.page_content for doc in docs)


# 3. AGENT 3 CUSTOM PROMPT TEMPLATE (Same as retreival.py)
AGENT_3_PROMPT_TEMPLATE = """
Role:
You are an expert AI Career Coach and Tutor. Your task is to generate **curated, actionable notes** for the user to close a specific skill gap, using ONLY the provided learning materials.

Instructions:
1.  **Analyze the Gap:** The user's goal is to move from their current skill level to the required one (e.g., Beginner Python to Intermediate Python).
2.  **Use Context Only:** You have access only to the provided resources (textbooks, articles, notes) in the <Context> section.
3.  **Generate a Structured Plan:** Use the context to create a detailed, step-by-step learning path. Organize the response using clear markdown headings and bullet points.
4.  **No Extraneous Info:** Do not use outside knowledge or mention the "Context" or "Skill Gap Summary" in the final output.
5.  **Handling Gaps:** If the provided context is completely irrelevant or insufficient to close the gap, respond with: "I apologize, the available learning resources do not contain sufficient material to address this specific skill gap. Please ensure the VectorDB has relevant documents for this topic."

<Context>
{context}
</Context>

**Skill Gap Summary (The User's Need):**
{question}
"""

# 4. DEFINE THE PROMPT
prompt = ChatPromptTemplate.from_template(AGENT_3_PROMPT_TEMPLATE)

# 5. CONSTRUCT THE RAG CHAIN (LCEL)
rag_chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough(),
    }
    | prompt
    | llm
    | StrOutputParser()
)


def generate_study_plan(skill_gap_summary: str) -> str:
    """Invoke the RAG chain to create a study plan."""

    return rag_chain.invoke(skill_gap_summary)


if __name__ == "__main__":
    skill_gap_input = "User is a beginner in GGPlot but requires intermediate skills. Also say where you pulled the resources from"

    print(f"**Agent 3 Input (Skill Gap):** {skill_gap_input}\n")

    final_output = generate_study_plan(skill_gap_input)

    print("\n==============================================")
    print("🤖 Agent 3 (Grok RAG) Final Output:")
    print("==============================================")
    print(final_output)
    print("==============================================\n")
