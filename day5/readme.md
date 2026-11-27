# Day 5 · Retrieval-Augmented Generation (RAG) & Multi-Tenant Memory

## Overview
Day 5 elevates the AI Car Showroom Assistant from a tool-using chatbot into an enterprise-grade agent equipped with:
- **Semantic Retrieval (RAG)**: Integrates **ChromaDB** vector storage to ground agent answers in 16 official showroom policies (test drives, loans, warranties, exchanges, bookings) without hallucinating.
- **Multi-Tenant State & Thread Isolation**: Leverages LangGraph's `InMemorySaver` checkpointer with `thread_id` to maintain distinct conversation memories per customer, preventing data leakage across users.
- **Automated Policy Evaluation Suite**: Runs automated regression tests across factual, financial, policy, and unsupported questions to ensure accuracy and safe fallback compliance.

---

## Conceptual Deep Dive & Core Topics

### 1. The Need for Retrieval-Augmented Generation (RAG)
- **The Problem**: Pre-trained LLMs do not know private business policies (e.g., your showroom's booking amount, EMI schemes, warranty terms). Stuffing all policies into the system prompt wastes tokens, exceeds context windows, and degrades model attention.
- **The RAG Solution**: Store policies in an external vector database. When a user asks a question, retrieve the top matching facts and provide them to the model as grounded context just in time.
- **Analogy**: A customer service agent with a company policy manual. Rather than memorizing the entire encyclopedia, the agent flips directly to the index, pulls the relevant page, and answers accurately.

---

### 2. Semantic Search vs Keyword Search with ChromaDB
Traditional keyword search fails when users use synonyms (e.g. asking for "car loan" when the FAQ says "vehicle finance").
- **Vector Embeddings**: Text is converted into numerical coordinate vectors capturing semantic meaning. Sentences with similar intent cluster near each other in vector space.
- **ChromaDB**: An open-source, embedded vector database.
  - `chroma_client.get_or_create_collection(name="car_showroom_faq")`: Initializes or retrieves the FAQ vector collection.
  - `showroom_faq.upsert(ids=..., documents=...)`: Embeds and indexes documents into the database.
  - `showroom_faq.query(query_texts=[question], n_results=3)`: Calculates cosine distance and retrieves the top-3 semantically closest policy documents.

---

### 3. Packaging Vector Search into an Agent Tool (`@tool`)
The agent shouldn't query the vector database blindly; it uses a specialized tool:
```python
@tool
def search_showroom_faq(question: str) -> str:
    """Search showroom policies about test drives, booking, finance,
    EMI, exchange, insurance, registration, warranty, service,
    delivery, discounts, availability, colours and documents.
    Use this tool for showroom policy questions.
    """
    results = showroom_faq.query(query_texts=[question], n_results=3)
    documents = results["documents"][0]
    if not documents:
        return "No matching showroom information was found."
    return "\n".join(documents)
```
- **Docstring Precision**: The tool docstring explicitly enumerates the topics covered, signaling to the agent exactly when to select `search_showroom_faq` versus catalogue tools like `get_car_price`.

---

### 4. Multi-Tenant Memory with LangGraph Checkpointers
In production, hundreds of customers interact with the showroom assistant simultaneously. Conversations must never cross-contaminate.
- **`InMemorySaver`**: A checkpointer that serializes conversation graphs and assigns them to distinct session threads.
- **`thread_id` Routing**:
  ```python
  config = {"configurable": {"thread_id": thread_id}}
  car_agent.invoke({"messages": [...]}, config)
  ```
  - `customer_101` (Ravi interested in Nexon) remembers his car preference and name.
  - `customer_202` (Sravani interested in Creta) maintains her independent state.
  - Attempting to inspect Customer 1's preferences from Customer 2's session returns no knowledge, guaranteeing data privacy.

---

### 5. Fallback Rules & Hallucination Prevention
Rule 6 of the system prompt enforces strict bounds on out-of-scope queries:
> *"If the FAQ does not contain the answer, say: 'I don't have that information. Please check with the showroom team.'"*
- When a user asks an unsupported question (e.g. *"Do you provide free home delivery anywhere in India?"*), the tool returns empty or irrelevant results, and the agent safely falls back to showroom staff referral rather than fabricating false promises.

---

## Day 5 in One Table

| Concept | What It Does | Real-World Analogy |
| :--- | :--- | :--- |
| **ChromaDB Collection** | Stores policy documents as vector embeddings | Indexed company policy manual |
| **`search_showroom_faq`** | Semantic lookup tool for policies & FAQs | Index lookup assistant |
| **`InMemorySaver`** | Preserves conversation states per session | A bank of labeled customer filing folders |
| **`thread_id`** | Routes messages to the correct customer's memory | Customer account number / ticket ID |
| **Grounded Answering** | Answers strictly using retrieved documents | Answering open-book from official guidelines |
| **Safe Fallback** | Refuses unsupported queries with standard staff referral | Polite reception desk redirect |

---

## Implementation Architecture (`task5.py`)

### 1. Showroom Policy Knowledge Base (16 FAQs)
Comprehensive policies indexed into ChromaDB:
1. `test_drive`: Booking and scheduling test drives.
2. `booking`: Vehicle reservation process.
3. `booking_amount`: Deposit policies.
4. `finance`: Loan eligibility and lender requirements.
5. `emi`: Calculations based on price, down payment, interest, tenure.
6. `exchange`: Trade-in valuation process.
7. `insurance`: Coverage options.
8. `registration`: RTO charges.
9. `warranty`: Manufacturer warranty terms.
10. `service`: Scheduled maintenance.
11. `delivery`: Timeline and stock availability.
12. `discounts`: Promotional offers.
13. `availability`: Stock confirmation.
14. `colours`: Available paint options.
15. `documents`: KYC and registration documents.
16. `cancellation`: Refund and cancellation terms.

### 2. Full Suite of Tools
1. **`get_car_details`**: Vehicle specs, fuel types, body type.
2. **`get_car_price`**: Official price range lookup.
3. **`log_enquiry`**: Validates lead with Pydantic & writes to Google Sheets.
4. **`search_showroom_faq`**: Vector similarity retrieval from ChromaDB.

### 3. Agent System Prompt (8 Guidelines)
1. Use `get_car_details` for vehicle specifications.
2. Use `get_car_price` for vehicle prices.
3. Use `search_showroom_faq` for showroom policies.
4. Use `log_enquiry` when a customer is ready to submit an enquiry.
5. Never invent prices, specifications, or showroom policies.
6. If the FAQ does not contain the answer, say: `"I don't have that information. Please check with the showroom team."`
7. Remember details shared earlier in the same conversation.
8. Do not share one customer's conversation with another customer.

---

## File Structure
```
day5/
├── task5.py     # Complete Day 5 implementation (ChromaDB, RAG Tool, LangGraph Checkpointer, Regression Suite)
└── readme.md    # Conceptual foundations, architecture, and test explanations
```

---

## Setup & Running in Google Colab

### 1. Install Dependencies
```python
!pip install -qU langchain langchain-groq langgraph chromadb gspread
```

### 2. Configure Colab Secrets
In Google Colab, open the **Secrets (key icon)** tab:
- **Key**: `agent1` (or `GROQ_API_KEY`)
- **Value**: *Your Groq API key*

### 3. Run the Script
```bash
python task5.py
```

---

## Sample Outputs & Evaluation Suite

### 1. Multi-Customer Memory Isolation Demo
```text
CUSTOMER 1
User: Hi, my name is Ravi. I am interested in Tata Nexon.
Bot: Hello Ravi! Nice to meet you. The Tata Nexon is a fantastic SUV. How can I assist you with it today?

User: Can I request a test drive?
Bot: Yes, Ravi! You can request a test drive by contacting our showroom and providing your preferred date and time.

User: What is my name and which car am I interested in?
Bot: Your name is Ravi, and you are interested in the Tata Nexon.

CUSTOMER 2
User: My name is Sravani. I am interested in Hyundai Creta.
Bot: Hello Sravani! Welcome. The Hyundai Creta is a great choice. How can I help you today?

User: Can I exchange my old car?
Bot: Yes, Sravani! You can enquire about exchanging your existing vehicle. The exchange value depends on a vehicle inspection.

User: What is my name and which car am I interested in?
Bot: Your name is Sravani, and you are interested in the Hyundai Creta.

UNSUPPORTED QUESTION
User: Does your showroom provide free home delivery anywhere in India?
Bot: I don't have that information. Please check with the showroom team.
```

### 2. Automated Regression Test Summary
`task5.py` evaluates accuracy across policy retrieval and safety guardrails:
```text
Test 1: PASS
Question: Can I request a test drive?
Response: Customers can request a test drive by contacting the showroom and providing their preferred date and time.

Test 2: PASS
Question: Can I get a vehicle loan?
Response: Vehicle finance options are available subject to lender approval and customer eligibility.

Test 3: PASS
Question: Can I exchange my old vehicle?
Response: Customers can enquire about exchanging their existing vehicle. The exchange value depends on vehicle inspection.

Test 4: PASS
Question: Does the vehicle have a warranty?
Response: Warranty coverage depends on the vehicle manufacturer and model. Refer to the official warranty terms.

Test 5: PASS
Question: Do you provide free home delivery anywhere in India?
Response: I don't have that information. Please check with the showroom team.

========== TEST SUMMARY ==========
Total tests: 5
Passed: 5
Failed: 0
Pass rate: 100.00%
Target achieved! Day 5 testing passed.
```
