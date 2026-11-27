!pip install -qU langchain langchain-groq gspread

import os
from google.colab import userdata, auth

# Groq API key
api_key = userdata.get("agent1") or userdata.get("GROQ_API_KEY")

if not api_key:
    raise ValueError("Groq API key not found in Colab Secrets.")

os.environ["GROQ_API_KEY"] = api_key

from langchain_groq import ChatGroq

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

# Create or open the spreadsheet
try:
    sh = gc.open("Car Showroom Enquiries")
except gspread.SpreadsheetNotFound:
    sh = gc.create("Car Showroom Enquiries")

ws = sh.sheet1

# Add headers only if the sheet is empty
if not ws.row_values(1):
    ws.append_row([
        "name",
        "car",
        "budget",
        "fuel_preference",
        "purchase_timeline"
    ])

print("Google Sheet ready:", sh.url)

import json

from typing import Literal
from pydantic import BaseModel, Field
from langchain.tools import tool

# ==========================================
# 1. CAR SHOWROOM DATABASE
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

# ==========================================
# 2. PYDANTIC CUSTOMER ENQUIRY MODEL
# ==========================================

class CarEnquiry(BaseModel):
    """A customer enquiry collected by the showroom assistant."""

    name: str = Field(
        description="Customer's name"
    )

    car: Literal[
        "tata nexon",
        "hyundai creta",
        "maruti suzuki swift",
        "mahindra thar"
    ] = Field(
        description="Selected car from the showroom catalogue"
    )

    budget: str = Field(
        description="Customer's preferred budget"
    )

    fuel_preference: Literal[
        "Petrol",
        "Diesel",
        "Electric",
        "Not sure"
    ] = Field(
        description="Customer's preferred fuel type"
    )

    purchase_timeline: str = Field(
        description="When the customer plans to purchase the car"
    )

# ==========================================
# 3. TOOL 1: GET CAR DETAILS
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


# ==========================================
# 4. TOOL 2: GET CAR PRICE
# ==========================================

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


# ==========================================
# 5. TOOL 3: SAVE CUSTOMER ENQUIRY
# ==========================================

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

    # Check fuel preference against the selected car
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

from langchain.agents import create_agent

# ==========================================
# SYSTEM PROMPT
# ==========================================

SYSTEM = """
ROLE:
You are a friendly and professional AI Car Showroom Assistant.

FACTS:
Available car catalogue:
{catalogue}

RULES:

1. Help customers explore available cars.

2. Always use get_car_details when customers ask
   about car details, fuel types or vehicle types.

3. Always use get_car_price when customers ask
   about car prices.

4. Compare different cars using their actual
   catalogue information.

5. Recommend cars based on customer budget,
   vehicle type and fuel preference.

6. Never invent specifications, mileage,
   horsepower, features or prices.

7. If information is unavailable, politely ask
   the customer to confirm with the showroom.

8. Remember customer details during the conversation.

9. Collect the following information for an enquiry:
   - Customer name
   - Selected car
   - Budget
   - Fuel preference
   - Purchase timeline

10. Ask for missing information before saving.

11. Ask the customer for confirmation before
    saving their enquiry.

12. Use log_enquiry only after confirmation
    and successful validation.

13. Never claim that a test drive or vehicle booking
    has been completed. The tool only saves enquiries.

14. Respond in English or Telugu based on the customer.

FORMAT:
Keep responses short, clear and friendly.
"""

SYSTEM = SYSTEM.format(
    catalogue=json.dumps(CARS, indent=2, ensure_ascii=False)
)


# ==========================================
# CREATE AGENT
# ==========================================

agent = create_agent(
    model=llm,
    tools=[
        get_car_details,
        get_car_price,
        log_enquiry
    ],
    system_prompt=SYSTEM
)


# ==========================================
# CHAT MEMORY
# ==========================================

history = []


def chat(user_text: str) -> str:

    global history

    try:

        result = agent.invoke({
            "messages": history + [
                {
                    "role": "user",
                    "content": user_text
                }
            ]
        })

        history = result["messages"]

        return history[-1].content

    except Exception as e:

        print("Agent error:", e)

        return (
            "Sorry, I am unable to process your request "
            "right now. Please try again."
        )


# ==========================================
# INTERACTIVE CHAT
# ==========================================

print("Welcome to AI Car Showroom Assistant!")

print("Type 'exit' or 'bye' to stop.\n")

while True:

    user_text = input("You: ")

    if user_text.lower().strip() in ("exit", "bye", "quit"):

        print("Bot: Thank you for visiting our showroom!")

        break

    if user_text.lower().strip() == "reset":

        history = []

        print("Bot: Conversation restarted.")

        continue

    print("Bot:", chat(user_text))

# ==========================================
# STRUCTURED OUTPUT
# ==========================================

structured_llm = llm.with_structured_output(CarEnquiry)


# ==========================================
# TEST WITH MESSY CUSTOMER MESSAGES
# ==========================================

MESSAGES = [

    """
    Hi, I'm Ravi. I want a Tata Nexon.
    My budget is around 12 lakhs.
    Prefer petrol and planning to buy next month.
    """,

    """
    My name is Arjun. Interested in Hyundai Creta.
    Budget approximately 15 lakh.
    Diesel preferred. Planning to purchase in January.
    """,

    """
    Hello, I'm Priya. I need a Maruti Suzuki Swift.
    Budget is 8 lakhs, petrol is fine.
    I want to buy it within two months.
    """,

    """
    I'm Kiran. Looking for Mahindra Thar.
    My budget is 16 lakh.
    I prefer diesel and want to purchase soon.
    """,

    """
    Name: Sravani.
    Car: Tata Nexon.
    Budget: 10-12 lakhs.
    Fuel: Electric.
    Purchase: Next month.
    """
]


print("STRUCTURED OUTPUT TESTS")

for i, message in enumerate(MESSAGES, 1):

    try:

        result = structured_llm.invoke(
            "Extract the customer enquiry details:\n" + message
        )

        print(f"\nTEST {i}")
        print(result.model_dump())

    except Exception as e:

        print(f"TEST {i} ERROR:", e)
