# 24P31A42A2 - DriveReady OPC 2026: Agentic AI

Welcome to the **DriveReady OPC 2026** repository for **Agentic AI**.

This repository contains daily tasks, source code, and documentation for hands-on assignments.

---

## Repository Structure

```
24P31A42A2_DriveReady_OPC_2026/
├── day1/
│   ├── task1.py       # AI Car Showroom Assistant using OpenAI client on Groq
│   └── README.md      # Day 1 Task description, guidelines, and execution details
├── day2/
│   ├── task2.py       # Multi-turn Showroom Chatbot with car catalogue, tools, memory & error handling
│   └── readme.md      # Day 2 documentation, concepts, and execution guide
├── day3/
│   ├── task3.py       # LangChain Car Showroom Assistant with LCEL, memory & evaluation suite
│   └── readme.md      # Day 3 documentation, Agent vs Chatbot, and LangChain concepts
├── day4/
│   ├── task4.py       # Tools, Pydantic Structured Output, and Google Sheets Integration
│   └── readme.md      # Day 4 documentation on function calling, Pydantic, and gspread
├── day5/
│   ├── task5.py       # RAG with ChromaDB, LangGraph Multi-Tenant Memory & Evaluation Suite
│   └── readme.md      # Day 5 documentation on vector search, checkpointers, and safety fallbacks
├── day6/
│   ├── task6.py       # Multi-Agent Router Workflow with LangGraph, Specialist Agents & Streaming
│   └── readme.md      # Day 6 documentation on workflows, planning, state, and conditional edges
├── .env.example       # Template for environment configuration
├── .gitignore         # Standard Python gitignore
└── README.md          # Repository overview
```

---

## Modules Overview

### [Day 1 - Task 1: AI Car Showroom Assistant](./day1)
- Initializing the OpenAI SDK connected to Groq (`openai/gpt-oss-20b`).
- System prompt engineering implementing a 10-point guideline for professional car showroom interactions.
- Customer query execution with token usage tracking.

### [Day 2 - Task 2: Multi-Turn Car Showroom Assistant with Catalog & Tools](./day2)
- Structured data modeling of a showroom vehicle catalogue (`CARS`).
- Four-part system prompt (Role, Facts, Rules, Format) with English and Telugu multilingual capability.
- Function tools (`get_car_details`, `get_car_price`) wrapped with `@log_call` decorator for runtime tracing.
- Multi-turn conversation management with a sliding window buffer (`MAX_TURNS = 8`).
- Robust exception handling (`RateLimitError`, `AuthenticationError`, `APIConnectionError`).

### [Day 3 - Task 3: Your First Agent & LangChain](./day3)
- Foundations of Agentic AI: Chatbot vs. Agent, the four pillars (Brain, Instructions, Tools, Memory), and the ReAct Agent Loop.
- Rebuilding the assistant using **LangChain** and LCEL (`prompt | llm | StrOutputParser()`).
- Conversational memory management with `MessagesPlaceholder("history")`.
- Automated testing and regression evaluation suite (`run_tests`) asserting quantitative pass rates.

### [Day 4 - Task 4: Tools, Structured Output & Google Sheets](./day4)
- Agent tools via `@tool`: `get_car_details`, `get_car_price`, and `log_enquiry`.
- Strict schema validation with **Pydantic** (`CarEnquiry`, `Literal` constraints).
- Real-time cloud persistence by appending validated customer leads to **Google Sheets** using `gspread`.
- Comprehensive 14-rule system prompt enforcing enquiry details collection and customer confirmation.
- Direct structured output extraction with `llm.with_structured_output(CarEnquiry)` over messy chat messages.

### [Day 5 - Task 5: RAG with ChromaDB & Multi-Tenant Memory](./day5)
- Semantic knowledge retrieval with **ChromaDB** vector store holding 16 showroom policies (test drives, loans, warranty, exchange, etc.).
- Custom `@tool` `search_showroom_faq` for context-grounded policy answers.
- Multi-tenant state isolation using **LangGraph** `InMemorySaver` and `thread_id` session routing.
- Automated 5-question policy regression test suite verifying factual answers and safe fallback compliance.

### [Day 6 - Task 6: Workflows, Planning & LangGraph](./day6)
- Transitions from Level 2 single agent to Level 3 multi-agent architecture.
- Deterministic workflow router built with **LangGraph** (`StateGraph`, `START`, `END`, conditional branching).
- Centralized `BakeryState` schema (`TypedDict`) traveling across nodes.
- Separation of concerns: dedicated `faq_agent` and `order_agent` with scoped tools.
- Observability with step-by-step update streaming (`graph.stream`) and Mermaid visual diagrams.

---

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/praneeth336/24P31A42A2_DriveReady_OPC_2026.git
cd 24P31A42A2_DriveReady_OPC_2026
```

### 2. Install Dependencies
```bash
pip install -q openai langchain langchain-groq langgraph chromadb gspread python-dotenv
```

### 3. API Key Setup
In Google Colab, add your Groq API key under Secrets as `agent1`.
For local terminal runs:
```bash
# Windows PowerShell
$env:agent1 = "your_groq_api_key_here"

# Linux / macOS
export agent1="your_groq_api_key_here"
```

### 4. Run Daily Tasks
- **Day 1**:
  ```bash
  cd day1 && python task1.py
  ```
- **Day 2**:
  ```bash
  cd day2 && python task2.py
  ```
- **Day 3**:
  ```bash
  cd day3 && python task3.py
  ```
- **Day 4**:
  ```bash
  cd day4 && python task4.py
  ```
- **Day 5**:
  ```bash
  cd day5 && python task5.py
  ```
- **Day 6**:
  ```bash
  cd day6 && python task6.py
  ```
