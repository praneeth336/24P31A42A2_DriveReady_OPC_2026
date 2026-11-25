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
    from google.colab import userdata
    agent1 = userdata.get("agent1") or userdata.get("GROQ_API_KEY")
except Exception:
    agent1 = os.environ.get("agent1") or os.environ.get("GROQ_API_KEY")

from openai import OpenAI, RateLimitError, APIConnectionError, AuthenticationError

client = OpenAI(
    api_key=agent1 or os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

MODEL = "openai/gpt-oss-120b"
MENU = {"plum cake": 500, "chocolate cake": 650, "cupcake": 80}
MAX_TURNS = 8

SYSTEM = f"""ROLE:   You are the friendly assistant for Sweet Crumbs Home Bakery.
FACTS:  Menu with prices in rupees: {json.dumps(MENU)}
        Orders need 24 hours' notice. All cakes have eggless versions.
RULES:  Never promise a delivery time. If it isn't in FACTS, say "I'll check with the owner."
        Remember the customer's name and order during the chat.
FORMAT: Under 50 words, friendly, English or Telugu matching the customer."""

def log_call(func):
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

history = [{"role": "system", "content": SYSTEM}]

def chat(user_text: str) -> str:
    history.append({"role": "user", "content": user_text})
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

if __name__ == "__main__":
    print("=== Pricing Tool Evaluation ===")
    print("Total for 6 cupcakes: Rs", get_price("cupcake", 6))
    print("\n=== Multi-Turn Chatbot Evaluation ===")
    eval_prompts = [
        "Hi, my name is Ravi.",
        "Can I get 2 eggless plum cakes tomorrow?",
        "What is my name and what did I order?",
        "Can you deliver in 2 hours?",
        "cupcakes unnaya?"
    ]
    for prompt in eval_prompts:
        print(f"User: {prompt}")
        print(f"Bot:  {chat(prompt)}\n")
