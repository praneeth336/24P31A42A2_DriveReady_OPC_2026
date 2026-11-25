import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from google.colab import userdata
    api_key = userdata.get("GROQ_API_KEY") or userdata.get("agent1")
    if api_key:
        os.environ["GROQ_API_KEY"] = api_key
except Exception:
    pass

from langchain_groq import ChatGroq

SYSTEM = """You are the assistant for Sweet Crumbs Home Bakery.
Facts: we bake to order; orders need 24 hours' notice; all cakes have eggless versions.
Rules: never promise delivery times; if you do not know, say so.
Format: reply politely in under 60 words."""

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    api_key=os.environ.get("GROQ_API_KEY")
)

def ask(question: str) -> str:
    return llm.invoke([("system", SYSTEM), ("human", question)]).content

if __name__ == "__main__":
    evaluation_queries = [
        "can i get my order tommorrow",
        "Do you make eggless cakes?",
        "Can you deliver at 6 PM today?"
    ]
    for q in evaluation_queries:
        print(f"User: {q}")
        print(f"Bot:  {ask(q)}\n")
