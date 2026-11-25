import csv
import json
import os
import sys

try:
    from google.colab import userdata
    api_key = userdata.get("agent1") or userdata.get("GROQ_API_KEY")
    if api_key:
        os.environ["GROQ_API_KEY"] = api_key
except Exception:
    api_key = os.environ.get("agent1") or os.environ.get("GROQ_API_KEY")
    if api_key:
        os.environ["GROQ_API_KEY"] = api_key

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

CARS = {
    "tata nexon": {"price": "₹8–15 lakh", "fuel": ["Petrol", "Diesel", "Electric"], "type": "SUV"},
    "hyundai creta": {"price": "₹11–20 lakh", "fuel": ["Petrol", "Diesel"], "type": "SUV"},
    "maruti suzuki swift": {"price": "₹6–9 lakh", "fuel": ["Petrol"], "type": "Hatchback"},
    "mahindra thar": {"price": "₹11–18 lakh", "fuel": ["Petrol", "Diesel"], "type": "SUV"}
}

SYSTEM = f"""ROLE: You are a friendly and professional AI assistant for a car showroom.
FACTS: Available car catalogue:
{json.dumps(CARS)}
RULES:
1. Help customers explore available cars, compare models, and explain features.
2. Never invent prices or specifications not in FACTS.
3. If information is unavailable, politely ask the customer to confirm with the showroom.
4. Remember the customer's name and requirements during the chat.
FORMAT: Under 50 words, friendly, English or Telugu matching the customer."""

llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0.3)

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM),
    MessagesPlaceholder("history"),
    ("human", "{question}")
])

chain = prompt | llm | StrOutputParser()

history = []

def ask(question: str) -> str:
    answer = chain.invoke({"history": history, "question": question})
    history.extend([("human", question), ("ai", answer)])
    return answer

TEST_CASES = [
    {"question": "What is the price range of Tata Nexon?", "must_include": "8–15"},
    {"question": "Do you have an electric SUV?", "must_include": "nexon"},
    {"question": "How much is Maruti Suzuki Swift?", "must_include": "6–9"},
    {"question": "Do you have a BMW sedan?", "must_include": "confirm with the showroom"},
    {"question": "Which cars are available in diesel?", "must_include": "creta"}
]

def run_tests(tests=TEST_CASES) -> None:
    passed = 0
    for row in tests:
        answer = chain.invoke({"history": [], "question": row["question"]})
        ok = row["must_include"].lower() in answer.lower()
        passed += ok
        print("PASS" if ok else "FAIL", "|", row["question"], "→", answer[:70])
    print(f"\n{passed}/{len(tests)} passed ({passed / len(tests):.0%})")

if __name__ == "__main__":
    print("=== Multi-Turn Conversational Memory Test ===")
    print("User: Hi, I'm Rahul. I am looking for a compact SUV.")
    print("Bot: ", ask("Hi, I'm Rahul. I am looking for a compact SUV."))
    print("\nUser: What is my name and what car type did I ask for?")
    print("Bot: ", ask("What is my name and what car type did I ask for?"))

    print("\n=== Automated Showroom Evals (tests.csv) ===")
    run_tests()
