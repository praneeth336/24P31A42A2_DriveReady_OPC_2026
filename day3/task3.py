
!pip install -qU langchain langchain-groq

import os
import csv
import json
import functools

from google.colab import userdata
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser


# ==================================================
# 1. YOUR BUSINESS: CAR SHOWROOM SYSTEM PROMPT
# ==================================================

os.environ["GROQ_API_KEY"] = userdata.get("agent1")

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

SYSTEM = """
ROLE:
You are a friendly and professional AI assistant
for a car showroom.

FACTS:
Available car catalogue: {car_catalogue}

RULES:
1. Help customers explore available cars.
2. Explain prices, fuel types and vehicle types.
3. Recommend cars based on customer requirements.
4. Compare available models.
5. Never invent prices or specifications.
6. If a car is unavailable, ask the customer to
   confirm with the showroom.
7. Remember the customer's name and requirements.
8. Respond in English or Telugu based on the customer.

{extra_rule}

FORMAT:
Keep responses short, clear and friendly.
"""


# ==================================================
# 2. CREATE LANGCHAIN CHAIN
# ==================================================

def create_chain(temperature, extra_rule=""):
    llm = ChatGroq(
        model=MODEL,
        temperature=temperature
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM),
        MessagesPlaceholder("history"),
        ("human", "{question}")
    ])

    prompt = prompt.partial(
        car_catalogue=json.dumps(CARS),
        extra_rule=extra_rule
    )

    return prompt | llm | StrOutputParser()


# ==================================================
# 3. YOUR TESTS: CREATE tests.csv
# ==================================================

TEST_CASES = [
    ["What is the price of Tata Nexon?", "8–15"],
    ["Tell me about Hyundai Creta.", "creta"],
    ["Which car is an electric SUV?", "nexon"],
    ["What is the price of Maruti Swift?", "6–9"],
    ["Tell me about Mahindra Thar.", "thar"],
    ["Which cars have diesel fuel?", "diesel"],
    ["Which car is a hatchback?", "swift"],
    ["Do you have a BMW?", "showroom"],
    ["What fuel types are available in Tata Nexon?", "electric"],
    ["What type of vehicle is Hyundai Creta?", "SUV"]
]

with open("tests.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["question", "must_include"])
    writer.writerows(TEST_CASES)

print("tests.csv created successfully.")


# ==================================================
# 4. RUN TESTS AND CALCULATE PASS RATE
# ==================================================

def run_tests(chain):
    passed = 0
    total = 0

    with open("tests.csv", "r", encoding="utf-8") as file:
        tests = csv.DictReader(file)

        for test in tests:
            total += 1

            try:
                answer = chain.invoke({
                    "history": [],
                    "question": test["question"]
                })

                expected = test["must_include"].lower()
                success = expected in answer.lower()

                if success:
                    passed += 1

                print(
                    "PASS" if success else "FAIL",
                    "|", test["question"],
                    "->", answer[:100]
                )

            except Exception as error:
                print("ERROR:", error)

    rate = (passed / total) * 100 if total else 0

    print(f"\nPass rate: {passed}/{total} = {rate:.0f}%")

    return rate


# ==================================================
# 5. BASELINE TEST
# ==================================================

print("\n========== BASELINE TEST ==========")

chain = create_chain(0.2)
baseline_rate = run_tests(chain)


# ==================================================
# 6. IMPROVE: CHANGE ONE PROMPT RULE
# ==================================================

print("\n========== IMPROVED PROMPT TEST ==========")

IMPROVEMENT = """
IMPORTANT:
When a requested car is not in the catalogue,
clearly include the exact phrase
'confirm with the showroom'.
"""

improved_chain = create_chain(
    temperature=0.2,
    extra_rule=IMPROVEMENT
)

improved_rate = run_tests(improved_chain)

print("\n========== IMPROVEMENT COMPARISON ==========")
print("Before improvement:", baseline_rate, "%")
print("After improvement:", improved_rate, "%")

if improved_rate > baseline_rate:
    print("Result: Pass rate increased.")
elif improved_rate < baseline_rate:
    print("Result: Pass rate decreased.")
else:
    print("Result: Pass rate remained the same.")


# ==================================================
# 7. SWITCH: TEMPERATURE = 1.0
# RUN TESTS TWICE
# ==================================================

print("\n========== TEMPERATURE 1.0 - RUN 1 ==========")

creative_chain = create_chain(
    temperature=1.0,
    extra_rule=IMPROVEMENT
)

temperature_run1 = run_tests(creative_chain)

print("\n========== TEMPERATURE 1.0 - RUN 2 ==========")

temperature_run2 = run_tests(creative_chain)

print("\n========== TEMPERATURE COMPARISON ==========")
print("Run 1:", temperature_run1, "%")
print("Run 2:", temperature_run2, "%")


# ==================================================
# 8. AGENT OR NOT?
# CLASSIFY THREE SHOWROOM JOBS
# ==================================================

JOBS = {
    "Calculate the total car price with a fixed discount":
        "Plain code",

    "Explain the features of Tata Nexon":
        "One LLM call",

    "Understand customer requirements, look up multiple cars,
     compare them and recommend a suitable car":
        "Agent"
}

print("\n========== AGENT OR NOT? ==========")

for job, category in JOBS.items():
    print(job, "->", category)


# ==================================================
# 9. INTERACTIVE CAR SHOWROOM CHAT
# ==================================================

print("\n========== CAR SHOWROOM ASSISTANT ==========")

history = []
chat_chain = create_chain(temperature=0.2, extra_rule=IMPROVEMENT)

while True:
    user_text = input("\nYou: ")

    if user_text.lower().strip() in ("exit", "bye", "quit"):
        print("Bot: Thank you for visiting our showroom!")
        break

    try:
        answer = chat_chain.invoke({
            "history": history,
            "question": user_text
        })

        history.extend([
            ("human", user_text),
            ("ai", answer)
        ])

        print("Bot:", answer)

    except Exception as error:
        print("Error:", error)
