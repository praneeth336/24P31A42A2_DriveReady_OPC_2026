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

---

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/praneeth336/24P31A42A2_DriveReady_OPC_2026.git
cd 24P31A42A2_DriveReady_OPC_2026
```

### 2. Install Dependencies
```bash
pip install -q openai
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

### 4. Run Tasks
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
