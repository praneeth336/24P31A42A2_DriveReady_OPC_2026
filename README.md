# 24P31A42A2 - DriveReady OPC 2026: Agentic AI

Welcome to the **DriveReady OPC 2026** repository for **Agentic AI**.

This repository contains daily tasks, source code, and documentation for hands-on assignments.

---

## Repository Structure

```
24P31A42A2_DriveReady_OPC_2026/
├── day1/
│   ├── task1.py       # Task 1: Sweet Crumbs Bakery Assistant using ChatGroq & Prompt Engineering
│   └── README.md      # Task 1 description, setup instructions, and sample output
├── .gitignore         # Standard Python gitignore
└── README.md          # Repository overview
```

---

## Modules

### [Day 1 - Task 1: Sweet Crumbs Bakery Assistant](./day1)
- Model initialization with `langchain-groq` using `openai/gpt-oss-120b`.
- System prompt engineering enforcing operational facts, rules, and polite response constraints under 60 words.

---

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/praneeth336/24P31A42A2_DriveReady_OPC_2026.git
cd 24P31A42A2_DriveReady_OPC_2026
```

### 2. Install Dependencies
```bash
pip install langchain-groq python-dotenv
```

### 3. Configure API Credentials
```bash
# Windows PowerShell
$env:GROQ_API_KEY="your_groq_api_key_here"

# Linux / macOS
export GROQ_API_KEY="your_groq_api_key_here"
```

### 4. Run Day 1 Task
```bash
cd day1
python task1.py
```
