# Day 1 - Task 1: Sweet Crumbs Home Bakery Assistant

## Overview
This task demonstrates the fundamentals of building a specialized conversational assistant using LangChain and Groq (`ChatGroq`). The assistant represents **Sweet Crumbs Home Bakery** and is governed by strict operational rules and prompt constraints.

---

## Task Implementation Details (`task1.py`)

### 1. LLM Configuration
- **Library**: `langchain_groq.ChatGroq`
- **Model**: `openai/gpt-oss-120b`
- **Temperature**: `0` (deterministic, fact-grounded responses)
- **Authentication**: Retrieves `GROQ_API_KEY` from environment variables, `.env` file, or Google Colab userdata.

### 2. System Prompt Design
The prompt defines the persona, facts, rules, and output format:
```text
ROLE:   Assistant for Sweet Crumbs Home Bakery.
FACTS:  Bake to order; orders need 24 hours' notice; all cakes have eggless versions.
RULES:  Never promise delivery times; if you do not know, say so.
FORMAT: Reply politely in under 60 words.
```

### 3. Query Execution (`ask` function)
The function `ask(llm, question)` sends the structured messages `[("system", SYSTEM), ("human", question)]` to the LLM and extracts the assistant's response.

---

## Setup & Running

### 1. Install Dependencies
```bash
pip install langchain-groq python-dotenv
```

### 2. Set Environment Variable
```bash
# Windows PowerShell
$env:GROQ_API_KEY="your_groq_api_key_here"

# Linux / macOS
export GROQ_API_KEY="your_groq_api_key_here"
```

### 3. Run the Code
```bash
python task1.py
```

---

## Sample Output
```text
User: can i get my order tommorrow
Assistant: We need at least 24 hours’ notice for any order. We’ll do our best, but we can’t guarantee delivery tomorrow. Let us know what you’d like, and we’ll get it ready for you!

User: Do you make eggless cakes?
Assistant: Yes! All our cakes have eggless versions available. Please let us know your preferred flavor and order 24 hours in advance.

User: Can you deliver at 6 PM today?
Assistant: I am sorry, but all our cakes are baked to order and require at least 24 hours' notice. We cannot deliver today, nor can we promise specific delivery times.
```
