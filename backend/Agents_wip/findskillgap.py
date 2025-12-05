
from langchain.tools import tool

from langchain_groq import ChatGroq
#from dotenv import load_dotenv

import os

API_KEY = os.environ["GROQ_API_KEY"]
LANGSMITH_API_KEY = os.environ["LANGSMITH_API_KEY"]


model = ChatGroq(
    model = "llama-3.1-8b-instant",
    temperature=0,
    max_tokens=None,
 #   reasoning_format="parsed",
    timeout=None,
    max_retries=2,
)
