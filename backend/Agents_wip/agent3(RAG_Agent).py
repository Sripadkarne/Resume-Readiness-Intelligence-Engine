import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq  
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

load_dotenv()
GROQ_API_KEY = os.getenv("API_KEY")
GROQ_MODEL_NAME = "llama-3.1-8b-instant" 
CHROMA_DIR = '/Users/pranavkandula/Desktop/School/Fall 2025/AI-Engineering/Final_Project/Resume-Readiness-Intelligence-Engine/VectorDB'
COLLECTION_NAME = "RAG_DB_Learning_Resources"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

# Vector Store (Your existing Chroma database)
vectorstore = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
    persist_directory=CHROMA_DIR
)
retriever = vectorstore.as_retriever(k=3) # Retrieve the top 3 relevant chunks

# LLM (The native LangChain wrapper for Groq)
llm = ChatGroq(model=GROQ_MODEL_NAME, temperature=0.1, groq_api_key=GROQ_API_KEY)

def format_docs(docs: list[Document]) -> str:
    """Concatenates retrieved documents into a single context string."""
    return "\n\n---\n\n".join(doc.page_content for doc in docs)

# 3. AGENT 3 CUSTOM PROMPT TEMPLATE (Same great prompt)
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
# 
rag_chain = (
    # Step 1: Prepare the inputs
    # 'context': Runs the retriever, then formats the output documents.
    # 'question': Passes the user's input (skill gap summary) through unchanged.
    {"context": retriever | format_docs, 
     "question": RunnablePassthrough()}
    # Step 2: Combine inputs into the ChatPromptTemplate
    | prompt
    # Step 3: Pass the prompt to the ChatGroq LLM
    | llm
    # Step 4: Convert the LLM's object output to a simple string
    | StrOutputParser()
)

# --- EXAMPLE USAGE ---
if __name__ == "__main__":
    # Example input from Agent 2
    skill_gap_input = "User is a beginner in GGPlot but requires intermediate skills. Also say where you pulled the resources from"
    
    print(f"**Agent 3 Input (Skill Gap):** {skill_gap_input}\n")
    
    # Run the chain
    # The skill_gap_input is passed as the 'question' via RunnablePassthrough()
    final_output = rag_chain.invoke(skill_gap_input)
    
    print("\n==============================================")
    print("🤖 Agent 3 (Grok RAG) Final Output:")
    print("==============================================")
    print(final_output)
    print("==============================================\n")