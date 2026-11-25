# Day 2 · Prompts, Memory, and the Python Agents Need

## Overview
Day 2 focuses on controlling language model output through prompt engineering, managing conversation history (memory), and mastering the core Python primitives required for building autonomous agents.

---

## Key Topics Covered

### 1. Messages and Roles
Every API call sends a structured list of messages:
- **`system`**: Developer instructions (the customer never sees this).
- **`user`**: Input query from the customer.
- **`assistant`**: Previous model responses.
The model reads the full script from top to bottom and predicts the next assistant reply.

### 2. The 4-Part System Prompt
A robust system prompt functions like an employee job description:
- **Role**: Persona definition (*"Assistant for Sweet Crumbs Home Bakery"*).
- **Facts**: Essential ground truth (*Menu prices, 24-hour notice, eggless options*).
- **Rules**: Guardrails and constraints (*Never promise delivery times, check with owner if unsure*).
- **Format**: Tone and length limits (*Under 50 words, friendly, English or Telugu matching customer*).

### 3. Memory by Hand (Sliding Context Window)
LLM APIs are stateless. To enable multi-turn memory:
- User questions and assistant answers are appended to `history`.
- To avoid context window explosion and unnecessary token usage, a sliding window is applied:
  ```python
  recent = [history[0]] + history[1:][-MAX_TURNS:]
  ```

### 4. Python for Agents
1. **Dictionaries & JSON**: Data modeling of menu items, using `.get()` for safe fallbacks, and `json.dumps()` / `json.loads()`.
2. **Type Hints & Docstrings**: Defining clear function contracts (`def get_price(item: str, qty: int = 1) -> int:`) so future agents can inspect and use them as tools.
3. **Decorators (`@log_call`)**: Wrapping functions to add logging and observability without altering function logic.
4. **Resilience (`try / except`)**: Catching specific exceptions (`RateLimitError`, `APIConnectionError`, `AuthenticationError`) gracefully without crashing.

---

## File Structure
```
day2/
├── task.py      # Multi-turn chatbot implementation with memory, tools, and error handling
└── readme.md    # Documentation and explanation of concepts
```

---

## Configuration & Credentials
The Groq API key is referenced as `agent1` and loaded securely from the environment:
```python
agent1 = os.environ.get("agent1") or os.environ.get("GROQ_API_KEY")
```

### Setting the Key
```bash
# Windows PowerShell
$env:agent1 = "your_groq_api_key_here"
# or
$env:GROQ_API_KEY = "your_groq_api_key_here"

# Linux / macOS
export agent1="your_groq_api_key_here"
```

---

## How to Run

### 1. Install Dependencies
```bash
pip install openai python-dotenv
```

### 2. Execute Task
```bash
python task.py
```

---

## Sample Execution & Test Output

```text
=== Sweet Crumbs Bakery Chatbot - Day 2 ===
Powered by Groq API Key (agent1)

Testing get_price tool:
   [log] get_price('cupcake', 6) -> 480
Total for 6 cupcakes: Rs 480

Starting chat session (Type 'bye', 'exit', or 'quit' to end):

You: Hi, my name is Ravi.
Bot: Hi Ravi! 😊 Welcome to Sweet Crumbs Home Bakery. How can I assist you with your cake order today?

You: Do you have eggless chocolate cake?
Bot: Yes, Ravi! All our cakes, including our chocolate cake (₹650), have eggless versions available. Please note that we need at least 24 hours' notice for all orders. Would you like to place an order?

You: What is my name and what is the price for 2 chocolate cakes?
Bot: Your name is Ravi! Two chocolate cakes will cost ₹1,300. Please let us know at least 24 hours in advance so we can bake them fresh for you.

You: quit
Bot: Thank you for visiting Sweet Crumbs!
```
