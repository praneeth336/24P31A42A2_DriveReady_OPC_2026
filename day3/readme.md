# Day 3 · Your First Agent: What an Agent Is, and LangChain

## Overview
Day 3 marks the transition from simple chatbots to **agentic architectures**. It covers the theoretical foundations of what turns a language model into an autonomous agent, how an agent reasons and acts in a loop, and how **LangChain** and LCEL (LangChain Expression Language) simplify building, chaining, and evaluating stateful AI systems.

---

## Key Concepts

### 1. Chatbot vs. Agent
- **Chatbot**: Answers questions using words only. The customer still has to perform the actions.
- **Agent**: Given an objective/goal, it decides the necessary steps, executes tools (functions, APIs, database updates), observes results, and acts until the goal is achieved.

### 2. The Four Parts of an Agent
Every AI agent is built from four core pillars:
1. **Brain**: The foundation LLM (`ChatGroq` with `openai/gpt-oss-20b`).
2. **Instructions**: System prompt defining the persona, facts, rules, and output format.
3. **Tools**: Functions the agent is permitted to execute (`get_car_details`, `get_car_price`).
4. **Memory**: Conversational state (`MessagesPlaceholder("history")`) maintained across turns.

### 3. The Agent Loop (ReAct: Reason + Act)
$$\text{Goal} \longrightarrow \text{Think} \longrightarrow \text{Act (Tool Call)} \longrightarrow \text{Observe (Tool Result)} \longrightarrow \text{Repeat / Answer}$$
- The model evaluates what information is needed, asks to call a tool, inspects the returned result, and iterates until it can formulate the final answer.

### 4. Three Levels of AI
- **Level 1 (Traditional AI / Rule-based)**: Fixed deterministic logic (e.g., calculating EMI or GST).
- **Level 2 (Generative AI)**: One prompt producing creative text without external actions.
- **Level 3 (Agentic AI)**: Generative reasoning coupled with autonomous tool execution.

### 5. LangChain & LCEL Pipeline
Using LangChain Expression Language (LCEL), components are linked via the pipe (`|`) operator:
```python
chain = prompt | llm | StrOutputParser()
```
- **`ChatPromptTemplate`**: Fills system and user templates dynamically.
- **`MessagesPlaceholder("history")`**: Injects past conversational turns seamlessly.
- **`StrOutputParser`**: Extracts clean string content directly from the model response.

### 6. Automated Testing & Evals (`tests.csv`)
System prompts require rigorous regression testing to ensure prompt edits don't break existing behavior. Each test case asserts that the model response contains an expected keyword/phrase (`must_include`), computing a quantitative **pass rate**:
$$\text{Pass Rate} = \frac{\text{Passed Tests}}{\text{Total Tests}} \times 100\%$$

---

## File Structure
```
day3/
├── task3.py     # LangChain chain with memory, car catalogue, and automated evaluation harness
└── readme.md    # Concepts, architecture, and execution guide
```

---

## Setup & Running

### 1. Prerequisites
Install LangChain and the Groq integration package:
```bash
pip install -q langchain langchain-groq
```

### 2. API Key Configuration
In Google Colab, add your Groq API key under **Secrets** (key icon) as `agent1` (or `GROQ_API_KEY`).
For local terminal runs:
```bash
# Windows PowerShell
$env:agent1 = "your_groq_api_key_here"
# or
$env:GROQ_API_KEY = "your_groq_api_key_here"

# Linux / macOS
export agent1="your_groq_api_key_here"
```

### 3. Execute Task
```bash
python task3.py
```

---

## Sample Execution & Test Output

```text
=== Multi-Turn Conversational Memory Test ===
User: Hi, I'm Rahul. I am looking for a compact SUV.
Bot:  Hello Rahul! Welcome to our showroom. We have great SUV options like the Tata Nexon (₹8–15 lakh, available in Petrol, Diesel, and Electric) and the Hyundai Creta (₹11–20 lakh). Would you prefer a petrol, diesel, or electric SUV?

User: What is my name and what car type did I ask for?
Bot:  Your name is Rahul, and you asked for a compact SUV!

=== Automated Showroom Evals (tests.csv) ===
PASS | What is the price range of Tata Nexon? → The Tata Nexon is priced between ₹8–15 lakh. It comes in Petrol, Diesel
PASS | Do you have an electric SUV? → Yes! We offer the Tata Nexon SUV in an Electric variant along with Pet
PASS | How much is Maruti Suzuki Swift? → The Maruti Suzuki Swift is priced in the range of ₹6–9 lakh.
PASS | Do you have a BMW sedan? → We do not have BMW sedans in our current catalogue. Please confirm with the showroom.
PASS | Which cars are available in diesel? → The Tata Nexon, Hyundai Creta, and Mahindra Thar are available in diesel.

5/5 passed (100%)
```
