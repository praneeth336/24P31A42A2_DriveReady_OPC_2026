# Day 4 · Tools, Structured Output, and Google Sheets

## Overview
Day 4 transforms the AI Car Showroom Assistant from a pure text generator into an **action-capable agent equipped with tools ("hands")**:
- **Live Lookups**: Queries official car specifications, fuel types, and price ranges.
- **Data Validation with Pydantic**: Translates unstructured, messy customer messages into strictly typed, schema-validated enquiry objects.
- **External Persistence**: Automatically logs confirmed customer leads into a live Google Sheet using `gspread`.
- **Error Resilience**: Manages rate limits (HTTP 429), retries, and defensive tool error handling.

---

## Conceptual Deep Dive & Core Topics

### 1. Why Agents Need Tools (Hands for the Brain)
- **The LLM Limitation**: A language model alone only produces tokens based on pre-trained weights and the current prompt context. It cannot check real-time inventory, read external databases, calculate exact arithmetic reliably, or persist transactions.
- **The Solution**: Tools are standard Python functions that the model is permitted to request. The model decides **when** to call a tool and **what inputs** to provide, while your Python runtime executes the function deterministically and safely.

### 2. How Function Calling Works (The Waiter & The Kitchen Analogy)
> **The Model Never Runs Your Code!**
- **Analogy**:
  - **The Customer**: The user asking a question.
  - **The Waiter (LLM)**: Takes the order, decides which kitchen station is needed, and writes an order ticket (tool call request).
  - **The Kitchen (Host Python Runtime)**: Executes the cooking/computation (runs the actual Python function).
  - **The Plate (Tool Message)**: Returns the prepared dish (result) to the waiter to present to the customer.

```
┌────────────────┐                     ┌────────────────────┐
│ User Message   │ ──────────────────> │ Model              │
└────────────────┘                     │ Decides to call    │
                                       │ get_car_price()    │
                                       └─────────┬──────────┘
                                                 │ Tool Call Request
                                                 ▼
┌────────────────┐                     ┌────────────────────┐
│ Final Response │ <────────────────── │ Python Environment │
│ to User        │  Model summarizes   │ Executes function  │
└────────────────┘  the tool result    │ & returns result   │
                                       └────────────────────┘
```

#### Step-by-Step Execution Lifecycle:
1. **Schema Injection**: Along with the chat history, your program sends JSON schemas describing each available tool (name, purpose description, and parameter types).
2. **Model Decision**: If the model needs external data or an action, its output is an assistant message containing a `tool_calls` request (e.g. `get_car_price(car_name="tata nexon")`).
3. **Execution**: Your local Python runtime intercepts this request, runs the matching Python function with the provided arguments, and captures the return value.
4. **Tool Message Feedback**: The output is appended to the message list with role `"tool"` and the corresponding `tool_call_id`.
5. **Final Generation**: The model reads its prior request and the tool message, then crafts a polished, human-friendly response for the user.

---

### 3. Writing Good Tools with `@tool` (Labelled Kitchen Drawers)
LangChain's `@tool` decorator inspects Python functions to generate the schema that the LLM reads. For an agent to choose correctly, tools must follow three strict rules:

| Rule | Why It Matters | Example |
| :--- | :--- | :--- |
| **`snake_case` Name** | The first identifier the model evaluates. | `get_car_price` (Clear) vs `tool_1` (Vague) |
| **Strict Type Hints** | Generates the JSON Schema parameter validation rules. | `car_name: str`, `budget: str` |
| **Detailed Docstring** | Tells the model **what** the tool does, **when** to call it, and gives input examples. | `"Get the listed price range of a showroom car."` |
| **Defensive Returns** | Return helpful diagnostic error strings rather than raising uncaught exceptions that crash the agent loop. | Return `"Car not found. Available: ..."` instead of throwing `KeyError`. |

---

### 4. The Agent Loop: `create_agent` (Delivery Tracking Timeline)
`create_agent(model=..., tools=[...], system_prompt=...)` orchestrates the **Think → Act → Observe** loop:
1. **Think**: Evaluates user input against available tools and system instructions.
2. **Act**: Emits tool calls if external data or persistence is required.
3. **Observe**: Receives the tool outputs back into the conversation context.
4. **Loop / Conclude**: Repeats if multiple steps are needed (e.g., checking price, then checking fuel options), or formulates the final answer once all facts are collected.

The execution trace contains the full sequence of messages:
`[UserMessage -> AIMessage(tool_calls) -> ToolMessage(result) -> AIMessage(final_answer)]`.

---

### 5. Rate Limits & Defensive Handling (The Toll Plaza)
- **Error 429 (Too Many Requests)**: Free-tier APIs enforce strict limits on Requests Per Minute (RPM) and Tokens Per Minute (TPM). Because agents make multiple internal model calls per turn (tool selection, reasoning, summarization), they consume quotas faster than standard chat completions.
- **Handling Strategies**:
  1. **Automatic Retries**: Set `max_retries=3` in `ChatGroq` so transient network spikes or temporary throttles back off exponentially.
  2. **Defensive Validation**: Keep system prompts concise and structured to conserve prompt tokens.
  3. **Graceful Exception Handling**: Wrap agent invocations in `try...except` blocks with user-friendly fallback messages.

---

### 6. Structured Output with Pydantic (Deposit Slip Analogy)
Prompting an LLM for free-form JSON often results in syntax errors, missing fields, or hallucinated values.
- **Analogy**: A bank deposit slip. Instead of handing the teller an informal handwritten note, you must write within strict, labeled boxes (Account, Amount, Date). If a box is invalid or missing, the form is rejected immediately.
- **Pydantic Model (`CarEnquiry`)**:
  - `Field(description="...")`: Provides inline guidance to the LLM during extraction.
  - `Literal[...]`: Restricts categorical options (e.g., car names, fuel types) to exact allowed sets.
  - `llm.with_structured_output(CarEnquiry)`: Forces the LLM to output conforming JSON matching the schema, which Pydantic then parses into a type-safe Python object.

---

### 7. Saving to Google Sheets (`gspread` as a Self-Filling Register)
Google Sheets acts as a zero-setup, accessible tabular database that business owners can review directly from mobile or desktop:
- **`auth.authenticate_user()`**: Authorizes the Google Colab session.
- **`gspread.authorize(creds)`**: Connects to the user's Google Drive.
- **`gc.open("Car Showroom Enquiries")`**: Opens an existing spreadsheet or creates a new one with header columns (`name`, `car`, `budget`, `fuel_preference`, `purchase_timeline`).
- **`ws.append_row([...])`**: Appends the validated enquiry record atomically as a new row.

---

### 8. Putting It Together: The `log_enquiry` Tool (Careful Billing Clerk)
The `log_enquiry` tool combines validation, catalog cross-checking, and persistence into a single atomic operation:
1. **Schema Validation**: Parses inputs through `CarEnquiry(name=..., car=..., budget=..., fuel_preference=..., purchase_timeline=...)`.
2. **Business Logic Verification**: Verifies whether the selected fuel type is actually offered for that specific vehicle in `CARS` (e.g. rejecting "Diesel" for a Maruti Suzuki Swift).
3. **Storage**: Appends the confirmed lead to the Google Sheet.
4. **Safety & Confirmation**: The system prompt strictly prohibits calling `log_enquiry` until the customer has explicitly confirmed all details.

---

## Day 4 in One Table

| Idea | One-Line Summary | Real-World Analogy |
| :--- | :--- | :--- |
| **Tools** | Functions for live facts, calculations, and external actions | Phone and cash register for an exam student |
| **Function Calling** | Model requests a call; your code runs it; result returned as a message | Waiter taking order to the kitchen |
| **Good Tools** | `snake_case` name, type hints, docstring with "when to use" | Labelled kitchen drawers |
| **`create_agent`** | Combines Model + Tools + System Prompt into an automated loop | Delivery tracking timeline |
| **Rate Limits** | HTTP 429 = slow down; handle with retries and concise prompts | Toll plaza with rate-metered gates |
| **Pydantic** | Typed fields and strict validation rules rejecting bad data | Bank deposit slip checked at the counter |
| **Google Sheets** | `append_row` adds a structured record atomically | A business register that fills itself |
| **`log_enquiry`** | Validates → checks catalog → appends row → confirms | Careful billing clerk verifying before invoicing |

---

## Implementation Architecture (`task4.py`)

### 1. Showroom Catalogue (`CARS`)
```python
CARS = {
    "tata nexon": {"price": "₹8–15 lakh", "fuel": ["Petrol", "Diesel", "Electric"], "type": "SUV"},
    "hyundai creta": {"price": "₹11–20 lakh", "fuel": ["Petrol", "Diesel"], "type": "SUV"},
    "maruti suzuki swift": {"price": "₹6–9 lakh", "fuel": ["Petrol"], "type": "Hatchback"},
    "mahindra thar": {"price": "₹11–18 lakh", "fuel": ["Petrol", "Diesel"], "type": "SUV"}
}
```

### 2. Pydantic Model (`CarEnquiry`)
```python
class CarEnquiry(BaseModel):
    name: str = Field(description="Customer's name")
    car: Literal["tata nexon", "hyundai creta", "maruti suzuki swift", "mahindra thar"] = Field(
        description="Selected car from the showroom catalogue"
    )
    budget: str = Field(description="Customer's preferred budget")
    fuel_preference: Literal["Petrol", "Diesel", "Electric", "Not sure"] = Field(
        description="Customer's preferred fuel type"
    )
    purchase_timeline: str = Field(description="When the customer plans to purchase the car")
```

### 3. Agent Tools
1. **`get_car_details(car_name: str)`**: Fetches body type, price range, and available fuel options from `CARS`.
2. **`get_car_price(car_name: str)`**: Returns the official listed price range.
3. **`log_enquiry(...)`**: Validates fields against `CarEnquiry`, checks fuel feasibility, and writes to Google Sheets via `ws.append_row`.

### 4. 14 System Prompt Guidelines
1. Help customers explore available cars.
2. Always use `get_car_details` when asked about car details, fuel types, or vehicle types.
3. Always use `get_car_price` when asked about car prices.
4. Compare different cars using actual catalogue data.
5. Recommend cars based on budget, vehicle type, and fuel preference.
6. Never invent specifications, mileage, horsepower, features, or prices.
7. If information is unavailable, politely direct the customer to showroom staff.
8. Remember customer details across conversational turns.
9. Collect all 5 mandatory enquiry fields: Name, Selected Car, Budget, Fuel Preference, Purchase Timeline.
10. Explicitly ask for missing information before saving.
11. **Always ask the customer for confirmation before logging the enquiry.**
12. Execute `log_enquiry` only after customer confirmation and validation.
13. Never claim a test drive or booking is completed—only enquiries are logged.
14. Support bilingual interaction in English and Telugu.

---

## File Structure
```
day4/
├── task4.py     # Complete Day 4 code (Tools, Agent, Google Sheets, Pydantic Structured Output)
└── readme.md    # In-depth conceptual guide, analogies, and architecture
```

---

## Setup & Running in Google Colab

### 1. Install Dependencies
```python
!pip install -qU langchain langchain-groq gspread
```

### 2. Configure Colab Secrets
In Google Colab, open the **Secrets (key icon)** panel:
- **Key**: `agent1` (or `GROQ_API_KEY`)
- **Value**: *Your Groq API key*

### 3. Google Account Authentication
Running `task4.py` in Colab initiates Google OAuth to allow `gspread` to create or update the `"Car Showroom Enquiries"` spreadsheet in your Google Drive:
```python
auth.authenticate_user()
```

### 4. Run the Script
```bash
python task4.py
```

---

## Sample Execution & Test Scenarios

### Scenario 1: Interactive Chat with Tool Invocations & Sheet Logging
```text
You: Hi, what is the price and fuel options for Tata Nexon?
Bot: The Tata Nexon is priced between ₹8–15 lakh and is available in Petrol, Diesel, and Electric options.

You: I want to book an enquiry. I am Suresh, budget 12 lakhs, prefer petrol, buying next week.
Bot: Thank you Suresh! Here is a summary of your enquiry:
- Name: Suresh
- Car: Tata Nexon
- Budget: ₹12 lakh
- Fuel Preference: Petrol
- Purchase Timeline: Next week

Would you like me to save this enquiry into our showroom system?

You: Yes, please save it.
Bot: Enquiry successfully saved for Suresh. Selected car: tata nexon. Our showroom team will contact you shortly!
```

### Scenario 2: Testing Batch Structured Output Extraction
`task4.py` includes a standalone evaluation suite running messy customer inputs through `llm.with_structured_output(CarEnquiry)`:

```text
==================================================
STRUCTURED OUTPUT TESTS
==================================================

TEST 1: "Hi, I'm Ravi. I want a Tata Nexon. My budget is around 12 lakhs. Prefer petrol and planning to buy next month."
-> Result: {'name': 'Ravi', 'car': 'tata nexon', 'budget': 'around 12 lakhs', 'fuel_preference': 'Petrol', 'purchase_timeline': 'next month'}

TEST 2: "Arjun here. Looking for Creta diesel within 15L, maybe in January."
-> Result: {'name': 'Arjun', 'car': 'hyundai creta', 'budget': 'approximately 15 lakh', 'fuel_preference': 'Diesel', 'purchase_timeline': 'January'}
```
