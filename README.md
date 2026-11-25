# 24P31A42A2 - DriveReady OPC 2026: Agentic AI

Welcome to the **DriveReady OPC 2026** repository for **Agentic AI**.

This repository contains daily tasks, source code, and documentation for hands-on assignments.

---

## Repository Structure

```
24P31A42A2_DriveReady_OPC_2026/
├── day1/
│   ├── task1.py       # Sweet Crumbs Bakery Assistant using ChatGroq & Prompt Engineering
│   └── README.md      # Day 1 Task description, setup instructions, and sample output
├── day2/
│   ├── task2.py       # Multi-turn chatbot with memory, decorators, tools & error handling (agent1 key)
│   └── readme.md      # Day 2 documentation, concepts, and execution guide
├── .gitignore         # Standard Python gitignore
└── README.md          # Repository overview
```

---

## Modules Overview

### [Day 1 - Foundations of Agentic AI & LLM Guardrails](./day1)
- Model initialization with `langchain-groq` using `openai/gpt-oss-120b`.
- System prompt engineering enforcing operational facts, rules, and polite response constraints under 60 words.

### [Day 2 - Prompts, Memory, and the Python Agents Need](./day2)
- Multi-turn conversation management via OpenAI-compatible endpoint with Groq.
- Sliding memory window (`MAX_TURNS = 8`) to preserve context without blowing up token limits.
- Core Python primitives: Dictionary lookups (`.get()`), type-annotated tool functions, `@log_call` decorator, and resilient `try / except` blocks.
- Configured using Groq API key named `agent1`.

---

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/praneeth336/24P31A42A2_DriveReady_OPC_2026.git
cd 24P31A42A2_DriveReady_OPC_2026
```

### 2. Install Dependencies
```bash
pip install openai langchain-groq python-dotenv
```

### 3. Run Tasks
- **Day 1**:
  ```bash
  cd day1
  python task1.py
  ```
- **Day 2**:
  ```bash
  cd ../day2
  python task2.py
  ```
