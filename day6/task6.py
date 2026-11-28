!pip install -qU langchain langchain-groq langgraph langchain-core

# ==============================================================================
# DAY 6: WORKFLOWS, PLANNING AND LANGGRAPH
# 
# Key Architectural Concepts:
# 1. State Definition: TypedDict (BakeryState) acting as the shared "job card".
# 2. Structured Intent Classification: Pydantic model with Literal choices.
# 3. Dedicated Agent Specialists:
#    - FAQ Agent: Handles policies, prices, and timings with focused tools.
#    - Order Agent: Handles customer ordering with pricing and logging tools.
# 4. LangGraph Workflow:
#    - START -> classify node -> conditional edges (route function) -> {order, faq, other} -> END.
# 5. Dual Classifier Demo:
#    - Structured output classifier (llm.with_structured_output).
#    - Pure prompt text-based classifier for fallback analysis.
# 6. Stream Execution & Mermaid Graph Visualization.
# ==============================================================================

import os
from typing import Literal
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from google.colab import userdata

from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langchain.agents import create_agent
from IPython.display import Image, display

# ==============================================================================
# 1. SETUP & MODEL INITIALIZATION
# ==============================================================================

# Fetch Groq API Key from Google Colab Secrets
os.environ["GROQ_API_KEY"] = userdata.get("agent1") or userdata.get("agent") or userdata.get("GROQ_API_KEY") or ""

if not os.environ["GROQ_API_KEY"]:
    raise ValueError("Groq API key not found in Colab Secrets (agent1 / GROQ_API_KEY).")

# Initialize ChatGroq LLM
llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0.3
)

# ==============================================================================
# 2. STATE DEFINITION & STRUCTURED CLASSIFIER
# ==============================================================================

# Shared state schema (job card) that travels between graph nodes
class BakeryState(TypedDict):
    message: str   # The incoming customer query
    intent: str    # Populated by the classifier node ("order", "faq", or "other")
    reply: str     # Populated by the downstream handler node

# Pydantic schema enforcing structured intent extraction
class Intent(BaseModel):
    intent: Literal["order", "faq", "other"] = Field(
        description=(
            "order: customer wants to place a cake order; "
            "faq: customer asks about prices, timings or policies; "
            "other: greetings or unrelated messages"
        )
    )

# Structured classifier using tool-calling schema
classifier = llm.with_structured_output(Intent)

print("State schema and structured classifier initialized!")

# ==============================================================================
# 3. SPECIALIST AGENT TOOLS & AGENT DEFINITIONS
# ==============================================================================

@tool
def search_faq(query: str) -> str:
    """Search for bakery FAQ policies."""
    return "Delivery is within 5 km for Rs 50, free above Rs 1,000. Orders need 24h notice."

@tool
def get_price(cake_name: str) -> str:
    """Get the price for a specific cake item."""
    prices = {
        "plum cake": "Rs 500",
        "chocolate cake": "Rs 650",
        "cupcake": "Rs 80 each"
    }
    return prices.get(cake_name.lower().strip(), "Price: Contact Sweet Crumbs.")

@tool
def is_open() -> str:
    """Check the bakery's opening hours."""
    return "Sweet Crumbs is open Monday to Saturday 9 AM to 8 PM, Sunday 10 AM to 6 PM."

@tool
def log_order(name: str, item: str, quantity: int, pickup_date: str) -> str:
    """Save a confirmed cake order details."""
    return f"Order saved successfully for {name}: {quantity} x {item} on {pickup_date}!"

# Prompt for the FAQ Specialist Agent (Answers questions, cannot save orders)
FAQ_PROMPT = """
You are the FAQ assistant for Sweet Crumbs Home Bakery.

Use search_faq for bakery policies.
Use get_price for cake prices.
Use is_open for opening hours.

Never invent information.
If information is unavailable, say:
I'll check with the owner.
Keep answers concise.
"""

# Prompt for the Order Specialist Agent (Takes orders, calculates totals)
ORDER_PROMPT = """
You are the order assistant for Sweet Crumbs Home Bakery.

Use get_price to calculate prices.

Before saving an order, collect:
1. Customer name
2. Cake item
3. Quantity
4. Pickup date

Do not save incomplete orders.
Use log_order only after collecting all required details.
Confirm the order after successful saving.
"""

# Create dedicated specialist agents with scoped tool permissions
faq_agent = create_agent(
    model=llm,
    tools=[search_faq, get_price, is_open],
    system_prompt=FAQ_PROMPT
)

order_agent = create_agent(
    model=llm,
    tools=[get_price, log_order],
    system_prompt=ORDER_PROMPT
)

print("Specialist agents (FAQ Agent and Order Agent) created successfully!")

# ==============================================================================
# 4. LANGGRAPH NODES & ROUTING LOGIC
# ==============================================================================

# Node 1: Classifier Node (updates only 'intent')
def classify(state: BakeryState) -> dict:
    result = classifier.invoke(state["message"])
    return {"intent": result.intent}

# Execution Helper for Agent Invocation
def ask_agent(agent, message: str) -> str:
    result = agent.invoke({
        "messages": [
            {"role": "user", "content": message}
        ]
    })
    return result["messages"][-1].content

# Node 2: FAQ Agent Node
def answer_faq(state: BakeryState) -> dict:
    response = ask_agent(faq_agent, state["message"])
    return {"reply": response}

# Node 3: Order Agent Node
def take_order(state: BakeryState) -> dict:
    response = ask_agent(order_agent, state["message"])
    return {"reply": response}

# Node 4: Other Node (Fallback for greetings & general queries)
def other(state: BakeryState) -> dict:
    return {
        "reply": (
            "Hello from Sweet Crumbs! "
            "I can help with cakes, prices, orders "
            "and bakery policies."
        )
    }

# Conditional Routing Function: reads intent from state
def route(state: BakeryState) -> str:
    return state["intent"]

# ==============================================================================
# 5. WORKFLOW GRAPH ASSEMBLY & COMPILATION
# ==============================================================================

builder = StateGraph(BakeryState)

# Add nodes to graph
builder.add_node("classify", classify)
builder.add_node("faq", answer_faq)
builder.add_node("order", take_order)
builder.add_node("other", other)

# Entrypoint edge
builder.add_edge(START, "classify")

# Conditional edges splitting the workflow
builder.add_conditional_edges(
    "classify",
    route,
    {
        "order": "order",
        "faq": "faq",
        "other": "other"
    }
)

# Connect specialist paths to END
builder.add_edge("faq", END)
builder.add_edge("order", END)
builder.add_edge("other", END)

# Compile graph
graph = builder.compile()

print("LangGraph workflow compiled successfully!")

# Visualize graph (Mermaid)
try:
    display(Image(graph.get_graph().draw_mermaid_png()))
except Exception:
    print("\nMermaid ASCII Graph:")
    print(graph.get_graph().draw_mermaid())

# ==============================================================================
# 6. STREAMING EXECUTION DEMO
# ==============================================================================

test_messages = [
    "What are your bakery opening hours?",
    "I want to order 2 eggless plum cakes.",
    "Hello, good morning!"
]

stream_log = []

for msg in test_messages:
    print("\n" + "=" * 50)
    print("CUSTOMER:", msg)
    print("=" * 50)

    for step in graph.stream(
        {"message": msg},
        stream_mode="updates"
    ):
        print("GRAPH UPDATE:", step)
        stream_log.append({
            "customer_message": msg,
            "graph_update": step
        })

print("\nAll workflow tests completed!")
print(f"Total graph step updates: {len(stream_log)}")

# ==============================================================================
# 7. ALTERNATIVE TEXT-BASED PROMPT CLASSIFIER
# ==============================================================================

def classify_message(message: str) -> str:
    """Prompt-based text classifier as an alternative to structured output."""
    response = llm.invoke([
        {
            "role": "system",
            "content": """
            Classify the customer message into exactly ONE category.

            order = customer wants to place or modify an order.
            faq = customer asks about prices, timings or bakery policies.
            other = greetings or unrelated messages.

            Return ONLY one word:
            order, faq, or other.
            """
        },
        {
            "role": "user",
            "content": message
        }
    ])

    intent = response.content.strip().lower()

    if "order" in intent:
        return "order"
    elif "faq" in intent:
        return "faq"
    else:
        return "other"

print("\nText-based classifier demo:")
for msg in test_messages:
    print(f"'{msg}' -> Intent: {classify_message(msg)}")
