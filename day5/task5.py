!pip install -qU langchain langchain-groq langgraph chromadb

import os
from google.colab import userdata

import chromadb
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_groq import ChatGroq

# ==========================================
# 1. SETUP & MODEL
# ==========================================

api_key = userdata.get("agent1") or userdata.get("GROQ_API_KEY")
if not api_key:
    raise ValueError("Groq API key not found in Colab Secrets.")
os.environ["GROQ_API_KEY"] = api_key

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0.2,
    max_retries=3
)

# ==========================================
# 2. CHROMADB KNOWLEDGE BASE (RAG)
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
showroom_faq = chroma_client.get_or_create_collection(name="car_showroom_faq")

showroom_faq.upsert(
    ids=list(SHOWROOM_FAQS.keys()),
    documents=list(SHOWROOM_FAQS.values())
)

print("Knowledge stored:", showroom_faq.count(), "facts")

# ==========================================
# 3. TOOLS
# ==========================================

CARS = {
    "tata nexon": {"price": "₹8–15 lakh", "fuel": ["Petrol", "Diesel", "Electric"], "type": "SUV"},
    "hyundai creta": {"price": "₹11–20 lakh", "fuel": ["Petrol", "Diesel"], "type": "SUV"},
    "maruti suzuki swift": {"price": "₹6–9 lakh", "fuel": ["Petrol"], "type": "Hatchback"},
    "mahindra thar": {"price": "₹11–18 lakh", "fuel": ["Petrol", "Diesel"], "type": "SUV"}
}

@tool
def get_car_details(car_name: str) -> str:
    """Get the available specifications and fuel types of a showroom car."""
    car = CARS.get(car_name.lower().strip())
    if not car:
        return f"{car_name} is not in our catalogue. Available: {', '.join(CARS.keys())}"
    return f"Type: {car['type']}, Price: {car['price']}, Fuel: {', '.join(car['fuel'])}"

@tool
def get_car_price(car_name: str) -> str:
    """Get the listed price range of a showroom car."""
    car = CARS.get(car_name.lower().strip())
    if not car:
        return f"{car_name} is not available in our catalogue."
    return f"Listed price range: {car['price']}"

@tool
def search_showroom_faq(question: str) -> str:
    """Search showroom policies about test drives, booking, finance, EMI, exchange,
    insurance, registration, warranty, service, delivery, discounts, availability, colours and documents.
    """
    results = showroom_faq.query(query_texts=[question], n_results=3)
    documents = results["documents"][0]
    if not documents:
        return "No matching showroom information was found."
    return "\n".join(documents)

# ==========================================
# 4. AGENT & MEMORY (CHECKPOINTER)
# ==========================================

SYSTEM = """
ROLE:
You are a helpful AI assistant for a car showroom.

RULES:
1. Use get_car_details for vehicle specifications.
2. Use get_car_price for vehicle prices.
3. Use search_showroom_faq for showroom policies.
4. Never invent prices, specifications or showroom policies.
5. If the FAQ does not contain the answer, say:
   "I don't have that information. Please check with the showroom team."
6. Remember details shared earlier in the same conversation.
7. Do not share one customer's conversation with another customer.

FORMAT:
Give clear, concise and friendly answers.
"""

memory = InMemorySaver()

car_agent = create_agent(
    model=llm,
    tools=[
        get_car_details,
        get_car_price,
        search_showroom_faq
    ],
    system_prompt=SYSTEM,
    checkpointer=memory
)

def chat(thread_id: str, message: str) -> str:
    config = {"configurable": {"thread_id": thread_id}}
    try:
        result = car_agent.invoke(
            {"messages": [{"role": "user", "content": message}]},
            config
        )
        return result["messages"][-1].content
    except Exception as e:
        print("Agent error:", e)
        return "Sorry, something went wrong."

# ==========================================
# 5. DEMO: MULTI-CUSTOMER THREADS
# ==========================================

print("CUSTOMER 1 (thread: customer_101)")
print(chat("customer_101", "Hi, my name is Ravi. I am interested in Tata Nexon."))
print(chat("customer_101", "Can I request a test drive?"))
print(chat("customer_101", "What is my name and which car am I interested in?"))

print("\nCUSTOMER 2 (thread: customer_202)")
print(chat("customer_202", "My name is Sravani. I am interested in Hyundai Creta."))
print(chat("customer_202", "Can I exchange my old car?"))
print(chat("customer_202", "What is my name and which car am I interested in?"))

print("\nUNSUPPORTED QUESTION (thread: customer_303)")
print(chat("customer_303", "Does your showroom provide free home delivery anywhere in India?"))

# ==========================================
# 6. EVALUATION TEST SUITE
# ==========================================

TEST_CASES = [
    {"question": "Can I request a test drive?", "expected": ["test drive"]},
    {"question": "Can I get a vehicle loan?", "expected": ["finance", "lender"]},
    {"question": "Can I exchange my old vehicle?", "expected": ["exchange"]},
    {"question": "Does the vehicle have a warranty?", "expected": ["warranty"]},
    {"question": "Do you provide free home delivery anywhere in India?", "expected": ["don't have", "do not have", "check with the showroom"]}
]

passed = 0
for i, test in enumerate(TEST_CASES, start=1):
    response = chat(f"test_customer_{i}", test["question"])
    response_lower = response.lower()
    success = any(keyword in response_lower for keyword in test["expected"])
    if success:
        passed += 1
    print(f"\nTest {i}: {'PASS' if success else 'FAIL'}")
    print("Question:", test["question"])
    print("Response:", response)

pass_rate = (passed / len(TEST_CASES)) * 100
print("\n========== TEST SUMMARY ==========")
print(f"Total: {len(TEST_CASES)} | Passed: {passed} | Pass rate: {pass_rate:.1f}%")
