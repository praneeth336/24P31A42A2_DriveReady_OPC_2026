!pip install -qU langchain langchain-groq langgraph chromadb gspread

import os
import json
from typing import Literal
from pydantic import BaseModel, Field

from google.colab import userdata, auth
from langchain_groq import ChatGroq
from langchain.tools import tool
import chromadb
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent

# ==========================================
# 1. SETUP & AUTHENTICATION
# ==========================================

api_key = userdata.get("agent1") or userdata.get("GROQ_API_KEY")

if not api_key:
    raise ValueError("Groq API key not found in Colab Secrets.")

os.environ["GROQ_API_KEY"] = api_key

MODEL = "openai/gpt-oss-20b"

llm = ChatGroq(
    model=MODEL,
    temperature=0.2,
    max_retries=3
)

# Google Sheets authentication
auth.authenticate_user()

import gspread
from google.auth import default

creds, _ = default()
gc = gspread.authorize(creds)

try:
    sh = gc.open("Car Showroom Enquiries")
except gspread.SpreadsheetNotFound:
    sh = gc.create("Car Showroom Enquiries")

ws = sh.sheet1

if not ws.row_values(1):
    ws.append_row([
        "name",
        "car",
        "budget",
        "fuel_preference",
        "purchase_timeline"
    ])

print("Google Sheet ready:", sh.url)

# ==========================================
# 2. CAR SHOWROOM DATABASE & MODELS
# ==========================================

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

class CarEnquiry(BaseModel):
    """A customer enquiry collected by the showroom assistant."""
    name: str = Field(description="Customer's name")
    car: Literal[
        "tata nexon",
        "hyundai creta",
        "maruti suzuki swift",
        "mahindra thar"
    ] = Field(description="Selected car from the showroom catalogue")
    budget: str = Field(description="Customer's preferred budget")
    fuel_preference: Literal[
        "Petrol",
        "Diesel",
        "Electric",
        "Not sure"
    ] = Field(description="Customer's preferred fuel type")
    purchase_timeline: str = Field(description="When the customer plans to purchase the car")

# ==========================================
# 3. KNOWLEDGE BASE & CHROMADB VECTOR STORE
# ==========================================

SHOWROOM_FAQS = {
    "test_drive": "Customers can request a test drive by contacting the showroom and providing their preferred date and time.",
    "booking": "Customers can reserve a vehicle by contacting the showroom sales team.",
    "booking_amount": "The booking amount depends on the selected vehicle and current showroom policy. Confirm the exact amount with the sales team.",
    "finance": "Vehicle finance options are available subject to lender approval and customer eligibility.",
    "emi": "EMI depends on the vehicle price, down payment, interest rate and loan tenure.",
    "exchange": "Customers can enquire about exchanging their existing vehicle. The exchange value depends on vehicle inspection.",
    "insurance": "Vehicle insurance options can be discussed with the showroom sales team.",
    "registration": "Vehicle registration charges depend on the applicable location and vehicle category.",
    "warranty": "Warranty coverage depends on the vehicle manufacturer and model. Refer to the official warranty terms.",
    "service": "Vehicle servicing should follow the manufacturer's recommended service schedule.",
    "delivery": "Vehicle delivery dates depend on vehicle availability and completion of the required documentation.",
    "discounts": "Available discounts and offers must be confirmed with the showroom sales team.",
    "availability": "Vehicle availability can change. Customers should confirm current stock with the showroom.",
    "colours": "Available colours depend on the model, variant and current stock.",
    "documents": "Customers may need identity proof, address proof and other documents required by the lender or registration authority.",
    "cancellation": "Booking cancellation and refund conditions depend on the showroom's booking terms. Confirm them before booking."
}

chroma_client = chromadb.Client()

showroom_faq = chroma_client.get_or_create_collection(
    name="car_showroom_faq"
)

showroom_faq.upsert(
    ids=list(SHOWROOM_FAQS.keys()),
    documents=list(SHOWROOM_FAQS.values())
)

print("Knowledge stored:", showroom_faq.count(), "facts")

# ==========================================
# 4. AGENT TOOLS
# ==========================================

@tool
def get_car_details(car_name: str) -> str:
    """Get the available details of a showroom car.

    Args:
        car_name: Name of the car, e.g. Tata Nexon or Hyundai Creta.
    """
    car = CARS.get(car_name.lower().strip())
    if car is None:
        return (
            f"{car_name} is not available in our catalogue. "
            f"Available cars: {', '.join(CARS.keys())}"
        )
    return json.dumps(car, ensure_ascii=False)

@tool
def get_car_price(car_name: str) -> str:
    """Get the listed price range of a showroom car.

    Args:
        car_name: Name of the car whose price is requested.
    """
    car = CARS.get(car_name.lower().strip())
    if car is None:
        return f"{car_name} is not available in our showroom catalogue."
    return f"Listed price range: {car['price']}"

@tool
def log_enquiry(
    name: str,
    car: str,
    budget: str,
    fuel_preference: str,
    purchase_timeline: str
) -> str:
    """Save a confirmed customer enquiry to Google Sheets.

    Use only after collecting all required details and
    receiving the customer's confirmation to save the enquiry.
    """
    try:
        enquiry = CarEnquiry(
            name=name,
            car=car.lower().strip(),
            budget=budget,
            fuel_preference=fuel_preference,
            purchase_timeline=purchase_timeline
        )
    except Exception as e:
        return f"Could not save enquiry: {e}"

    available_fuels = CARS[enquiry.car]["fuel"]
    if (
        enquiry.fuel_preference != "Not sure"
        and enquiry.fuel_preference not in available_fuels
    ):
        return (
            f"{enquiry.fuel_preference} is not listed for "
            f"{enquiry.car}. Available fuel types: "
            f"{', '.join(available_fuels)}."
        )

    ws.append_row([
        enquiry.name,
        enquiry.car,
        enquiry.budget,
        enquiry.fuel_preference,
        enquiry.purchase_timeline
    ])

    return (
        f"Enquiry successfully saved for {enquiry.name}. "
        f"Selected car: {enquiry.car}."
    )

@tool
def search_showroom_faq(question: str) -> str:
    """Search showroom policies about test drives, booking, finance,
    EMI, exchange, insurance, registration, warranty, service,
    delivery, discounts, availability, colours and documents.
    Use this tool for showroom policy questions.
    """
    results = showroom_faq.query(
        query_texts=[question],
        n_results=3
    )
    documents = results["documents"][0]
    if not documents:
        return "No matching showroom information was found."
    return "\n".join(documents)

# Test search tool invocation
print("FAQ Tool test result:")
print(search_showroom_faq.invoke({
    "question": "Can I exchange my old car?"
}))

# ==========================================
# 5. AGENT CREATION WITH CHECKPOINTER (MEMORY)
# ==========================================

SYSTEM = """
ROLE:
You are a helpful AI assistant for a car showroom.

RULES:
1. Use get_car_details for vehicle specifications.
2. Use get_car_price for vehicle prices.
3. Use search_showroom_faq for showroom policies.
4. Use log_enquiry when a customer is ready to submit an enquiry.
5. Never invent prices, specifications or showroom policies.
6. If the FAQ does not contain the answer, say:
   "I don't have that information. Please check with the showroom team."
7. Remember details shared earlier in the same conversation.
8. Do not share one customer's conversation with another customer.

FORMAT:
Give clear, concise and friendly answers.
"""

memory = InMemorySaver()

car_agent = create_agent(
    model=llm,
    tools=[
        get_car_details,
        get_car_price,
        log_enquiry,
        search_showroom_faq
    ],
    system_prompt=SYSTEM,
    checkpointer=memory
)

print("Car showroom agent created successfully!")

# ==========================================
# 6. MULTI-TENANT CHAT INTERFACE
# ==========================================

def chat(thread_id: str, message: str) -> str:
    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }
    try:
        result = car_agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": message
                    }
                ]
            },
            config
        )
        return result["messages"][-1].content
    except Exception as e:
        print("Agent error:", e)
        return "Sorry, something went wrong."

# ==========================================
# 7. MULTI-CUSTOMER CONVERSATION DEMO
# ==========================================

# Customer 1
print("\nCUSTOMER 1")
print(chat("customer_101", "Hi, my name is Ravi. I am interested in Tata Nexon."))
print(chat("customer_101", "Can I request a test drive?"))
print(chat("customer_101", "What is my name and which car am I interested in?"))

# Customer 2
print("\nCUSTOMER 2")
print(chat("customer_202", "My name is Sravani. I am interested in Hyundai Creta."))
print(chat("customer_202", "Can I exchange my old car?"))
print(chat("customer_202", "What is my name and which car am I interested in?"))

# Unsupported question
print("\nUNSUPPORTED QUESTION")
print(chat("customer_303", "Does your showroom provide free home delivery anywhere in India?"))

# ==========================================
# 8. AUTOMATED REGRESSION EVALUATION SUITE
# ==========================================

TEST_CASES = [
    {
        "question": "Can I request a test drive?",
        "expected": ["test drive"]
    },
    {
        "question": "Can I get a vehicle loan?",
        "expected": ["finance", "lender"]
    },
    {
        "question": "Can I exchange my old vehicle?",
        "expected": ["exchange"]
    },
    {
        "question": "Does the vehicle have a warranty?",
        "expected": ["warranty"]
    },
    {
        "question": "Do you provide free home delivery anywhere in India?",
        "expected": ["don't have", "do not have", "check with the showroom"]
    }
]

passed = 0

for i, test in enumerate(TEST_CASES, start=1):
    response = chat(
        f"test_customer_{i}",
        test["question"]
    )
    response_lower = response.lower()
    success = any(
        keyword in response_lower
        for keyword in test["expected"]
    )
    if success:
        passed += 1

    print(f"\nTest {i}: {'PASS' if success else 'FAIL'}")
    print("Question:", test["question"])
    print("Response:", response)

total = len(TEST_CASES)
pass_rate = (passed / total) * 100

print("\n========== TEST SUMMARY ==========")
print("Total tests:", total)
print("Passed:", passed)
print("Failed:", total - passed)
print(f"Pass rate: {pass_rate:.2f}%")

if pass_rate >= 80:
    print("Target achieved! Day 5 testing passed.")
else:
    print("Target not achieved. Review failed tests and improve the agent.")
