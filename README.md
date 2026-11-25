# 24P31A42A2 - DriveReady OPC 2026: Agentic AI

Welcome to the **DriveReady OPC 2026** repository for **Agentic AI**.

This repository contains daily tasks, source code, and comprehensive documentation for hands-on assignments and implementations.

---

## Repository Structure

```
24P31A42A2_DriveReady_OPC_2026/
├── Day_01/
│   ├── bakery_assistant_langchain.py  # LangChain ChatGroq Bakery Assistant
│   ├── prompt_guard_security.py       # Prompt Guard & Injection Detection
│   └── README.md                      # Day 1 Task description & implementation
├── .gitignore                         # Standard Python gitignore
└── README.md                          # Repository overview
```

---

## Daily Modules

### [Day 01: Foundations of Agentic AI & LLM Guardrails](./Day_01)
- **Task 1: Sweet Crumbs Bakery Assistant**
  - Model initialization with `langchain-groq` using `openai/gpt-oss-120b`.
  - System prompt engineering enforcing operational facts, rules, and polite response constraints.
- **Task 2: Prompt Guard & Security Evaluation**
  - Implementing safety guardrails with Groq's `meta-llama/llama-prompt-guard-2-22m`.
  - Detecting and scoring adversarial jailbreaks and prompt injection attempts.

---

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/praneeth336/24P31A42A2_DriveReady_OPC_2026.git
cd 24P31A42A2_DriveReady_OPC_2026
```

### 2. Install Dependencies
```bash
pip install langchain-groq groq python-dotenv
```

### 3. Configure API Credentials
Set your Groq API Key:
```bash
# Windows PowerShell
$env:GROQ_API_KEY="your_groq_api_key_here"

# Linux / macOS
export GROQ_API_KEY="your_groq_api_key_here"
```

### 4. Run Day 1 Tasks
```bash
cd Day_01
python bakery_assistant_langchain.py
python prompt_guard_security.py
```
