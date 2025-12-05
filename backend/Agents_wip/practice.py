from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain.tools import tool
import os

API_KEY = os.environ["GROQ_API_KEY"]

model = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
)

@tool
def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

system_prompt = """
You are a helpful assistant with access to tools.
Always use the tool when asked about weather.
"""

agent = create_agent(
    model=model,
    tools=[get_weather],
    system_prompt=system_prompt,
)

# CORRECT WAY
result = agent.invoke({"input": "what is the weather in sf"})

print(result["messages"][-1].content)
