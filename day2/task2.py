import json
import functools

from openai import RateLimitError, AuthenticationError, APIConnectionError

MODEL = "openai/gpt-oss-20b"

CARS = {
    "tata nexon": {
        "price": "₹8–15 lakh",
        "fuel": ["Petrol", "Diesel", "Electric"],
        "type": "SUV"
    },
    "hyundai creta": {
        "price": "₹11–20 lakh",
        "fuel": ["Petrol", "Diesel"],
        "type": "SUV"
    },
    "maruti suzuki swift": {
        "price": "₹6–9 lakh",
        "fuel": ["Petrol"],
        "type": "Hatchback"
    },
    "mahindra thar": {
        "price": "₹11–18 lakh",
        "fuel": ["Petrol", "Diesel"],
        "type": "SUV"
    }
}

SYSTEM = f"""
ROLE:
You are a friendly and professional AI assistant
for a car showroom.

FACTS:
Available car catalogue:
{json.dumps(CARS)}

RULES:
1. Help customers explore available cars.
2. Explain car features and specifications.
3. Recommend cars based on customer requirements.
4. Help customers compare different models.
5. Never invent prices or specifications.
6. If information is unavailable, ask the customer
   to confirm with the showroom.
7. Remember the customer's name and requirements
   during the conversation.

FORMAT:
Keep responses short, clear and friendly.
Respond in English or Telugu based on the customer.
"""

def log_call(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        print(f"[LOG] {func.__name__}{args} -> {result!r}")
        return result
    return wrapper


@log_call
def get_car_details(car_name: str) -> dict:
    """Return the available details of a car in the showroom."""
    return CARS[car_name.lower().strip()]


@log_call
def get_car_price(car_name: str) -> str:
    """Return the listed price range of a showroom car."""
    return CARS[car_name.lower().strip()]["price"]


history = [
    {"role": "system", "content": SYSTEM}
]

MAX_TURNS = 8


def chat(user_text: str) -> str:
    history.append({
        "role": "user",
        "content": user_text
    })

    recent = [history[0]] + history[1:][-MAX_TURNS:]

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=recent,
            temperature=0.3
        )

        reply = response.choices[0].message.content

    except RateLimitError:
        reply = "We are currently busy. Please try again in a minute."

    except AuthenticationError:
        reply = "There is an API authentication problem. Please check the API key."

    except APIConnectionError:
        reply = "I cannot connect to the server right now. Please try again."

    history.append({
        "role": "assistant",
        "content": reply
    })

    return reply


print("Car Showroom Assistant")
print("Type 'exit' or 'bye' to stop.\n")

while True:
    user_text = input("You: ")

    if user_text.lower().strip() in ("bye", "exit", "quit"):
        print("Bot: Thank you for visiting our showroom!")
        break

    print("Bot:", chat(user_text))
