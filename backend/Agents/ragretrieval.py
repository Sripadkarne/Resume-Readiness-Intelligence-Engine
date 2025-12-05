


from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain.tools import tool

import os

API_KEY = os.environ["GROQ_API_KEY"]


model = ChatGroq(
    model = "llama-3.1-8b-instant",
    temperature=0,
    max_tokens=None,
 #   reasoning_format="parsed",
    timeout=None,
    max_retries=2,
)
