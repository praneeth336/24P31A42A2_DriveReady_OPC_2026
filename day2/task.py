"""
Day 2 - Task: Sweet Crumbs Chatbot with Memory and Python Agent Fundamentals
Topic: Prompts, Memory, and Python for AI Agents
Demonstrates:
- API Key configuration using Groq key named 'agent1'
- System Prompt Engineering (Role, Facts, Rules, Format)
- Python for Agents:
    1. Menu Data as Dictionary with safe fallback
    2. Function contracts with type hints and docstrings
    3. @log_call decorator for execution inspection
    4. Sliding window conversational memory (MAX_TURNS = 8)
    5. Defensive error handling (RateLimitError, APIConnectionError)
    6. Multilingual support (English & Telugu)
"""

import functools
import json
import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from openai import OpenAI, RateLimitError, APIConnectionError, AuthenticationError
except ImportError:
    print("Error: openai library not installed. Run: pip install openai")
    sys.exit(1)


# Groq API key named 'agent1' - securely loaded from environment or Colab secrets
agent1 = os.environ.get("agent1") or os.environ.get("GROQ_API_KEY")
if not agent1:
    try:
        from google.colab import userdata
        agent1 = userdata.get("agent1") or userdata.get("GROQ_API_KEY")
    except Exception:
        pass

if not agent1:
    # If not set in environment, check fallback
    agent1 = os.getenv("GROQ_API_KEY", "YOUR_GROQ_API_KEY_HERE")

# Initialize OpenAI client pointing to Groq's API endpoint
client = OpenAI(
    api_key=agent1,
    base_url="https://api.groq.com/openai/v1"
)

MODEL = "openai/gpt-oss-120b"
MENU = {"plum cake": 500, "chocolate cake": 650, "cupcake": 80}
MAX_TURNS = 8

# System Prompt incorporating Role, Facts, Rules, and Format
SYSTEM = f"""ROLE:   You are the friendly assistant for Sweet Crumbs Home Bakery.
FACTS:  Menu with prices in rupees: {json.dumps(MENU)}
        Orders need 24 hours' notice. All cakes have eggless versions.
RULES:  Never promise a delivery time. If it isn't in FACTS, say "I'll check with the owner."
        Remember the customer's name and order during the chat.
FORMAT: Under 50 words, friendly, English or Telugu matching the customer."""


def log_call(func):
    """Decorator to log function execution, arguments, and return values."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        print(f"   [log] {func.__name__}{args} -> {result!r}")
        return result
    return wrapper


@log_call
def get_price(item: str, qty: int = 1) -> int:
    """Return the total price in rupees for qty of an item on the menu."""
    return MENU[item.lower().strip()] * qty


# In-memory conversation history initialized with the system prompt
history = [{"role": "system", "content": SYSTEM}]


def chat(user_text: str) -> str:
    """
    Process user input, maintain sliding context history, and return model response.
    """
    history.append({"role": "user", "content": user_text})
    
    # Sliding window: preserve system prompt + last MAX_TURNS messages
    recent = [history[0]] + history[1:][-MAX_TURNS:]
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=recent,
            temperature=0.3
        )
        reply = response.choices[0].message.content
    except RateLimitError:
        reply = "We're a little busy. Please try again in a minute."
    except AuthenticationError:
        reply = "Setup problem: please tell the owner the API key isn't working."
    except APIConnectionError:
        reply = "I can't reach the server right now. Please try again shortly."
    except Exception as e:
        reply = f"An unexpected error occurred: {e}"

    history.append({"role": "assistant", "content": reply})
    return reply


# Alias for agent call
agent1_chat = chat


def main():
    print("=== Sweet Crumbs Bakery Chatbot - Day 2 ===")
    print("Powered by Groq API Key (agent1)\n")
    
    # 1. Test pricing function with @log_call decorator
    print("Testing get_price tool:")
    print("Total for 6 cupcakes: Rs", get_price("cupcake", 6))
    print()

    # 2. Interactive Chat Loop
    print("Starting chat session (Type 'bye', 'exit', or 'quit' to end):\n")
    while True:
        try:
            text = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nBot: Thank you for visiting Sweet Crumbs!")
            break

        if not text:
            continue
        if text.lower() in ("bye", "exit", "quit"):
            print("Bot: Thank you for visiting Sweet Crumbs!")
            break

        print("Bot:", chat(text))


if __name__ == "__main__":
    main()
