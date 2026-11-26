# Day 4 · Tools, Structured Output, and Google Sheets

## Overview
Day 4 equips the AI Car Showroom Assistant with **tools (hands)**: allowing it to fetch live vehicle specifications and prices, validate messy customer requests into strict schemas using **Pydantic**, and save confirmed customer leads directly into a live **Google Sheet** using `gspread`.

---

## Core Topics & Theoretical Foundations

### 1. Why Agents Need Tools
- A model alone only produces text based on training weights and immediate prompt context. It cannot check live inventory, query external databases, perform guaranteed exact arithmetic, or persist records.
- **Tools** are standard Python functions that the model is permitted to request. The model decides **when** to call a tool, while your program runs the function safely and deterministically.

### 2. How Function Calling Works (The Waiter & The Kitchen)
- The model **never executes Python code directly**.
- **The Flow**:
  1. Your program sends the conversation messages along with **JSON tool schemas** (name, description, parameters).
  2. The LLM evaluates the prompt and replies with a **tool call request** (e.g., `get_car_price(car_name="tata nexon")`).
  3. Your host code intercepts the request, runs the actual Python function, and appends the result as a `tool` message.
  4. The LLM receives the tool result and crafts the final user-facing response.

### 3. Writing Robust Tools with `@tool`
LangChain's `@tool` decorator converts regular Python functions into model-callable tools:
- **Descriptive Names**: Clear `snake_case` names (e.g., `get_car_details`, `log_enquiry`).
- **Type Annotations**: Explicit parameter types (`car_name: str`, `budget: str`) build the JSON parameter schema.
- **Detailed Docstrings**: Explains *what* the tool does, *when* the agent should invoke it, and input examples.
- **Defensive Returns**: Return helpful diagnostic error strings on invalid input instead of raising exceptions that crash the agent loop.

### 4. Pydantic Structured Output
Asking an LLM for free-form JSON often results in syntax errors or missing keys. **Pydantic** enforces strict data contracts:
- `Field(...)`: Provides parameter descriptions that guide LLM extraction.
- `Literal[...]`: Restricts categorical fields (e.g., car models, fuel types) to exact allowed values.
- `llm.with_structured_output(CarEnquiry)`: Forces the model to extract and return a validated Pydantic object directly.

### 5. Google Sheets Integration (`gspread`)
Connects the agent directly to Google Drive:
- `auth.authenticate_user()`: Authorizes Colab user credentials.
- `gspread.authorize(creds)`: Initializes the Sheets client.
- `ws.append_row([...])`: Appends validated enquiry records as clean table rows accessible on mobile or web.

---

## Implementation Architecture (`task4.py`)

### 1. Car Showroom Database (`CARS`)
Structured catalogue containing current vehicle specifications:
- **Tata Nexon**: ₹8–15 lakh | Petrol, Diesel, Electric | SUV
- **Hyundai Creta**: ₹11–20 lakh | Petrol, Diesel | SUV
- **Maruti Suzuki Swift**: ₹6–9 lakh | Petrol | Hatchback
- **Mahindra Thar**: ₹11–18 lakh | Petrol, Diesel | SUV

### 2. Pydantic Model (`CarEnquiry`)
```python
class CarEnquiry(BaseModel):
    name: str = Field(description="Customer's name")
    car: Literal["tata nexon", "hyundai creta", "maruti suzuki swift", "mahindra thar"]
    budget: str = Field(description="Customer's preferred budget")
    fuel_preference: Literal["Petrol", "Diesel", "Electric", "Not sure"]
    purchase_timeline: str = Field(description="When the customer plans to purchase the car")
```

### 3. Agent Tools
1. **`get_car_details(car_name: str)`**: Looks up full specifications, fuel variants, and body type.
2. **`get_car_price(car_name: str)`**: Returns the official showroom price range.
3. **`log_enquiry(...)`**: Validates enquiry parameters with `CarEnquiry`, cross-checks fuel availability against the vehicle catalogue, and appends the validated row to the Google Sheet.

### 4. 14-Rule System Prompt
Enforces domain guidelines:
- Mandatory tool usage for car details and pricing.
- Exploration, comparison, and budget-based recommendations.
- Collection of all 5 mandatory enquiry fields before saving.
- **Mandatory customer confirmation** prior to saving.
- Clear disclaimer: enquiries are logged; vehicle bookings/test drives are not completed by the bot.
- Multilingual responses in English or Telugu.

### 5. Interactive Chat & Structured Extraction Tests
- **Interactive Console**: Supports continuous chat with memory, `reset` command to clear context, and `exit`/`bye` to terminate.
- **Batch Extraction Tests**: Runs 5 messy, unstructured customer messages through `structured_llm = llm.with_structured_output(CarEnquiry)` to demonstrate automated lead parsing.

---

## File Structure
```
day4/
├── task4.py     # Complete Day 4 implementation (Tools, Sheets, Agent, Structured Output)
└── readme.md    # Documentation and conceptual guide
```

---

## Setup & Running in Google Colab

### 1. Install Dependencies
```bash
!pip install -qU langchain langchain-groq gspread
```

### 2. Configure Colab Secrets
In Google Colab, click the **Secrets (key icon)** tab on the left sidebar:
- Name: `agent1` (or `GROQ_API_KEY`)
- Value: *Your Groq API key*

### 3. Google Account Authentication
Running `task4.py` in Colab will prompt you to authorize your Google account so `gspread` can create/access the **"Car Showroom Enquiries"** spreadsheet in your Google Drive.

### 4. Run the Script
```bash
python task4.py
```

---

## Sample Outputs

### 1. Agent Conversation & Google Sheet Entry
```text
User: Hi, I'm Priya. What is the price of Hyundai Creta?
Bot: Hello Priya! The Hyundai Creta has a listed price range of ₹11–20 lakh. Would you like to know more about its fuel options or features?

User: I want to book an enquiry for Creta. Budget is 15 lakhs, diesel, planning to buy next month.
Bot: Great! Here are your enquiry details:
- Name: Priya
- Car: Hyundai Creta
- Budget: ₹15 lakh
- Fuel Preference: Diesel
- Purchase Timeline: Next month

Shall I go ahead and save this enquiry to our showroom system?

User: Yes, please save it.
Bot: Enquiry successfully saved for Priya. Selected car: hyundai creta. Our showroom team will reach out to you soon!
```

### 2. Structured Output Test Result (Pydantic Extraction)
```text
STRUCTURED OUTPUT TESTS

TEST 1
{'name': 'Ravi', 'car': 'tata nexon', 'budget': 'around 12 lakhs', 'fuel_preference': 'Petrol', 'purchase_timeline': 'next month'}

TEST 2
{'name': 'Arjun', 'car': 'hyundai creta', 'budget': 'approximately 15 lakh', 'fuel_preference': 'Diesel', 'purchase_timeline': 'January'}
```
