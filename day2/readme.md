# Day 2 - Task 2: Multi-Turn Car Showroom Assistant with Catalog & Tools

## Overview
Day 2 builds upon the showroom assistant by introducing **structured data modeling**, **function tools with logging decorators**, **multi-turn conversational memory with a sliding window**, and **production error handling**.

---

## Key Components (`task2.py`)

### 1. Showroom Vehicle Catalog (`CARS`)
The vehicle inventory is represented as a structured Python dictionary containing prices, fuel options, and body types:
- **Tata Nexon**: ₹8–15 lakh | Petrol, Diesel, Electric | SUV
- **Hyundai Creta**: ₹11–20 lakh | Petrol, Diesel | SUV
- **Maruti Suzuki Swift**: ₹6–9 lakh | Petrol | Hatchback
- **Mahindra Thar**: ₹11–18 lakh | Petrol, Diesel | SUV

### 2. Four-Part System Prompt
- **ROLE**: Friendly and professional AI assistant for a car showroom.
- **FACTS**: Injected directly from `json.dumps(CARS)`.
- **RULES**: Explore cars, explain specs, recommend vehicles, compare models, never invent prices, check with showroom if unsure, remember customer name and preferences.
- **FORMAT**: Short, clear, friendly; English or Telugu matching the customer.

### 3. Tool Functions with `@log_call` Decorator
The `@log_call` decorator wraps functions using `functools.wraps` to inspect inputs and return values at runtime without altering core logic:
- `get_car_details(car_name: str) -> dict`: Returns the full dictionary specification for a model.
- `get_car_price(car_name: str) -> str`: Returns the listed price range for a model.

### 4. Sliding Context Window (`MAX_TURNS = 8`)
To maintain conversational continuity without overflowing model context or incurring excessive token costs:
```python
recent = [history[0]] + history[1:][-MAX_TURNS:]
```
This ensures the system prompt is always preserved while older turns roll off cleanly.

### 5. Defensive Error Handling (`try / except`)
Catches API exceptions gracefully and informs the user politely instead of crashing:
- `RateLimitError`: Advises the customer that the system is busy and to retry shortly.
- `AuthenticationError`: Flags API key configuration issues.
- `APIConnectionError`: Handles network connectivity drops.

---

## File Structure
```
day2/
├── task2.py     # Multi-turn showroom assistant with car catalogue, tools, and error handling
└── readme.md    # Documentation and explanation of concepts
```

---

## Setup & Running

### 1. Prerequisites
Ensure the OpenAI client SDK is installed:
```bash
pip install -q openai
```

### 2. API Key Configuration
In Google Colab, add your Groq API key in Colab Secrets as `agent1`.
If running locally, set the environment variable:
```bash
# Windows PowerShell
$env:agent1 = "your_groq_api_key_here"

# Linux / macOS
export agent1="your_groq_api_key_here"
```

### 3. Run the Chatbot
```bash
python task2.py
```

---

## Sample Conversation Output

```text
Car Showroom Assistant
Type 'exit' or 'bye' to stop.

You: Hi, my name is Priya. What SUVs do you have under 15 lakhs?
Bot: Hello Priya! Great to meet you. For SUVs under ₹15 lakh, we have the Tata Nexon (₹8–15 lakh), which comes in Petrol, Diesel, and Electric. The Mahindra Thar also starts at ₹11 lakh. Would you prefer an electric or petrol/diesel option?

You: Does the Nexon have an EV variant?
Bot: Yes, Priya! The Tata Nexon is available in an Electric variant along with Petrol and Diesel options. It is priced between ₹8–15 lakh depending on the variant.

You: Thar price entha?
Bot: మహీంద్రా థార్ ధర ₹11–18 లక్షల మధ్య ఉంటుంది. ఇది పెట్రోల్ మరియు డీజిల్ వేరియంట్లలో అందుబాటులో ఉంది.

You: exit
Bot: Thank you for visiting our showroom!
```
