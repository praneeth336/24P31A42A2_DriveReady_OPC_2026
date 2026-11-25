# Day 1 - Task 1: AI Car Showroom Assistant

## Overview
This task demonstrates setting up a domain-specific conversational assistant using the OpenAI SDK connected to Groq's fast inference endpoint. The assistant represents an **AI Car Showroom Assistant** that guides customers in exploring, comparing, and selecting vehicles while strictly following professional showroom guidelines.

---

## Implementation Details (`task1.py`)

### 1. LLM & Client Configuration
- **SDK**: `openai.OpenAI`
- **Base URL**: `https://api.groq.com/openai/v1`
- **Model**: `openai/gpt-oss-20b`
- **Temperature**: `0.2` (focused, accurate, and consistent responses)
- **API Key**: Retrieved from Google Colab Secrets using `userdata.get("agent1")`

### 2. System Prompt Guidelines
The system prompt establishes the assistant persona and 10 operational rules:
1. Greet customers politely.
2. Answer questions about available cars.
3. Explain car features, specifications, and variants.
4. Help customers compare different cars.
5. Recommend cars based on customer requirements.
6. Keep responses clear and easy to understand.
7. Never invent vehicle specifications or prices.
8. If information is unavailable, politely state that confirmation is needed.
9. Ask relevant questions when additional information is required.
10. Maintain a professional and friendly conversation.

### 3. Execution & Token Usage Tracking
The script sends a customer inquiry (`"Hello! I am looking for a new car."`) and displays the assistant's response along with detailed token consumption metrics (`response.usage`).

---

## Setup & Execution

### 1. Prerequisites
In Google Colab or your Python environment:
```bash
pip install -q openai
```

### 2. Configure API Key
In Google Colab, add your Groq API key under the **Secrets** tab (key icon) with the name `agent1`.

### 3. Run the Code
```bash
python task1.py
```

---

## Sample Output
```text
Hello and welcome to our showroom! I would be delighted to help you find the perfect car. 

To help me narrow down the best options for you, could you share a bit more about what you're looking for? For example:
- What type of vehicle do you prefer (Hatchback, Sedan, SUV)?
- What is your approximate budget?
- What will be the primary usage (daily city commute, family road trips, rough terrain)?
- Do you have a preferred fuel type (Petrol, Diesel, Electric)?

Token Usage: CompletionUsage(completion_tokens=112, prompt_tokens=154, total_tokens=266)
```
