"""
Day 1 - Task 1: Sweet Crumbs Home Bakery Assistant
Demonstrates:
- Setting up ChatGroq with LangChain
- Designing constrained system prompts (Role, Facts, Rules, Format)
- Invoking the LLM to provide polite, rule-compliant responses
"""

import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from langchain_groq import ChatGroq
except ImportError:
    print("Error: langchain_groq not installed. Run: pip install langchain-groq")
    sys.exit(1)


def get_api_key() -> str:
    """Retrieve Groq API key from environment variable or Google Colab userdata."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        try:
            from google.colab import userdata
            api_key = userdata.get("GROQ_API_KEY")
            if api_key:
                os.environ["GROQ_API_KEY"] = api_key
        except Exception:
            pass
    if not api_key:
        raise ValueError("GROQ_API_KEY not found. Please set it in your environment or .env file.")
    return api_key


# System Prompt Defining Persona, Facts, Rules, and Output Formatting
SYSTEM = """You are the assistant for Sweet Crumbs Home Bakery.
Facts: we bake to order; orders need 24 hours' notice; all cakes have eggless versions.
Rules: never promise delivery times; if you do not know, say so.
Format: reply politely in under 60 words."""


def ask(llm: ChatGroq, question: str) -> str:
    """Query the bakery assistant with a customer question."""
    messages = [
        ("system", SYSTEM),
        ("human", question)
    ]
    response = llm.invoke(messages)
    return response.content


def main():
    print("=== Sweet Crumbs Home Bakery Assistant (Day 1 - Task 1) ===")
    try:
        get_api_key()
        llm = ChatGroq(
            model="openai/gpt-oss-120b",
            temperature=0
        )
    except Exception as e:
        print(f"Initialization error: {e}")
        return

    sample_queries = [
        "can i get my order tommorrow",
        "Do you make eggless cakes?",
        "Can you deliver at 6 PM today?"
    ]

    for query in sample_queries:
        print(f"\nUser: {query}")
        answer = ask(llm, query)
        print(f"Assistant: {answer}")


if __name__ == "__main__":
    main()
