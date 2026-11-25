"""
Day 01 - Task 1: Sweet Crumbs Home Bakery Assistant
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
SYSTEM_PROMPT = """You are the assistant for Sweet Crumbs Home Bakery.
Facts: we bake to order; orders need 24 hours' notice; all cakes have eggless versions.
Rules: never promise delivery times; if you do not know, say so.
Format: reply politely in under 60 words."""


def init_llm(model: str = "openai/gpt-oss-120b", temperature: float = 0.0) -> ChatGroq:
    """Initialize LangChain ChatGroq client."""
    get_api_key()
    return ChatGroq(
        model=model,
        temperature=temperature
    )


def ask_bakery_assistant(llm: ChatGroq, question: str) -> str:
    """Query the bakery assistant with a customer question."""
    messages = [
        ("system", SYSTEM_PROMPT),
        ("human", question)
    ]
    response = llm.invoke(messages)
    return response.content


def main():
    print("=== Sweet Crumbs Home Bakery Assistant (Day 1) ===")
    try:
        llm = init_llm()
    except Exception as e:
        print(f"Initialization error: {e}")
        return

    sample_queries = [
        "Can I get my order tomorrow?",
        "Do you have eggless chocolate cake?",
        "Can you deliver at 5:00 PM sharp?"
    ]

    for query in sample_queries:
        print(f"\nCustomer: {query}")
        answer = ask_bakery_assistant(llm, query)
        print(f"Assistant: {answer}")


if __name__ == "__main__":
    main()
