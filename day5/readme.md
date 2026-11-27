# Day 5 · Memory and RAG: An Agent that Remembers and Looks Things Up

## Overview
Day 5 delivers a complete, production-grade **AI Car Showroom Assistant** by unifying conversational memory and knowledge retrieval:
- **Conversation Memory (Threads)**: Uses LangGraph's `InMemorySaver` checkpointer and `thread_id` to maintain state across conversational turns without mixing up separate customer sessions.
- **Retrieval-Augmented Generation (RAG)**: Integrates an embedded **ChromaDB** vector database indexing 16 showroom policies (test drives, loans, warranties, bookings, exchanges), preventing hallucinations.
- **Deterministic Action Tools**: Reuses catalogue lookup (`get_car_details`, `get_car_price`) and Pydantic-validated Google Sheets persistence (`log_enquiry`).
- **Safety Fallback & Automated Testing**: Enforces a strict refusal rule for unsupported questions and proves performance with a 5-question automated regression test suite.

---

## Conceptual Deep Dive & Core Topics

### 1. Three Kinds of Memory
An agent manages three separate layers of memory:

| Kind of Memory | What It Holds | Lifetime | Real-World Analogy | Car Showroom Example |
| :--- | :--- | :--- | :--- | :--- |
| **Conversation Memory** (Short-term) | Dialogue within the active chat | Single session | Shopkeeper's **notepad** during a call | *"Ravi asked for Tata Nexon a minute ago"* |
| **Customer Memory** (Long-term) | Preferences saved across visits | Weeks / Months | The **customer register** | *"Ravi prefers diesel vehicles and high safety ratings"* |
| **Knowledge** (Documents / RAG) | Official business policies | Until documents change | The **policy manual** on the shelf | *"Test drives require preferred date and time"* |

---

### 2. Conversation Memory: Threads (`checkpointer` + `thread_id`)
- **The Problem**: In production, hundreds of customers interact with the showroom at the same time. Storing messages in a single list causes cross-customer data leakage.
- **The Solution**: LangGraph's **checkpointer** (`InMemorySaver`) manages state across multiple conversations.
- **How It Works**:
  - Pass `checkpointer=InMemorySaver()` when building the agent via `create_agent`.
  - Pass a `thread_id` with every message inside the config:
    ```python
    config = {"configurable": {"thread_id": "customer_101"}}
    agent.invoke({"messages": [{"role": "user", "content": text}]}, config)
    ```
  - **Email Thread Analogy**: Like an email chain, every reply stays grouped with earlier messages in that specific thread. Thread `customer_101` (Ravi) never sees messages from thread `customer_202` (Sravani).

---

### 3. Why Not Put Everything in the Prompt? (The Library vs. The Index)
- **Prompt Stuffing Problems**:
  1. **Cost**: You pay for every input token on *every single call*, and agents make multiple calls per query.
  2. **Latency**: Massive prompts slow down inference speed.
  3. **Attention Loss**: Relevant facts get buried among hundreds of unrelated lines ("lost in the middle").
- **Analogy**: You don't carry the **entire library** to the exam. You carry an **index**, look up the exact page needed, and bring only that page to your desk.
- **The Rule**: Few facts (< 20) → Prompt is fine. Many facts (> 50) → Search first with RAG, send only the top 2–3 relevant facts.

---

### 4. Embeddings: Meaning as Numbers
- **Definition**: An embedding model converts text into a list of numbers (a vector in high-dimensional coordinate space).
- **Core Principle**: Texts with similar *meaning* receive close coordinate numbers, even if they use completely different words.
- **Supermarket Layout Analogy**: Items that belong together sit on nearby shelves (soaps near shampoos, dal near rice). Embeddings place sentences on a "meaning map":
  - *"Can I exchange my old car?"* and *"Do you accept vehicle trade-ins?"* share few words, but land next to each other on the vector map.

---

### 5. Vector Database: ChromaDB
- **What It Does**: ChromaDB is an embedded vector database that:
  1. Generates numerical embeddings for documents automatically.
  2. Stores documents alongside their vector representations.
  3. Executes fast nearest-neighbor similarity searches for incoming queries.
- **Key Operations**:
  ```python
  import chromadb
  client = chromadb.Client()
  faq = client.get_or_create_collection(name="car_showroom_faq")
  faq.upsert(ids=[...], documents=[...])
  results = faq.query(query_texts=["Can I test drive?"], n_results=3)
  ```
- **Librarian Analogy**: A librarian who knows what every book is about. You describe what you need in plain words, and they pull the 3 most useful books.

---

### 6. Chunking: Slicing Documents into Meaningful Pieces
- **Why Chunking Matters**:
  - Storing a 20-page document as one chunk causes search to return all 20 pages (back to prompt stuffing).
  - Cutting text too small splits sentences and destroys context.
- **Cake Slice Analogy**: One giant slice is too much for a guest; crumbs are useless. Neat slices, each with one complete layer of idea, are just right.
- **Rule of Thumb**: One chunk ≈ one clear idea or policy (typically 100–300 words). Add a 10–15% overlap between adjacent chunks so boundary sentences aren't cut in half.

---

### 7. RAG: Retrieve → Augment → Generate
RAG executes in three clear steps:
1. **Retrieve**: Search the vector database using the customer's question (`search_showroom_faq`).
2. **Augment**: Inject the top retrieved policy documents into the model's prompt.
3. **Generate**: The LLM crafts an answer *strictly grounded* in those retrieved documents.
- **Open-Book Exam Analogy**: An exam where you are allowed to consult the official textbook, with a strict rule: answer only what is written in the book, and if an answer is missing, honestly state:
  > *"I don't have that information. Please check with the showroom team."*

---

### 8. Single-Agent Sign-Off: The Complete Architecture
With Day 5, all 5 pillars of a production single agent are assembled:

| Pillar | Technology / Implementation | Function |
| :--- | :--- | :--- |
| **Brain** | `ChatGroq` (`openai/gpt-oss-20b`) | Reasoning and tool selection |
| **Instructions** | System Prompt (Role, Rules, Format) | Operational guidelines and constraints |
| **Tools** | `get_car_details`, `get_car_price`, `log_enquiry`, `search_showroom_faq` | External actions and facts lookup |
| **Memory** | LangGraph `InMemorySaver` with `thread_id` | Isolated customer conversational history |
| **Knowledge** | ChromaDB Collection (`car_showroom_faq`) | Semantic policy retrieval (RAG) |

---

## Day 5 in One Table

| Idea | One-Line Summary | Real-World Analogy |
| :--- | :--- | :--- |
| **Three Kinds of Memory** | Conversation, customer, and knowledge | Notepad, customer register, policy manual |
| **Threads** | `InMemorySaver` + one `thread_id` per chat | Email conversation threads |
| **Prompt vs. Search** | Search first, send only what's relevant | An index, not the whole library |
| **Embeddings** | Text converted into numbers representing meaning | Supermarket shelf layout |
| **Vector Database** | Stores text vectors, queries by semantic similarity | A librarian who knows every book |
| **Chunking** | One idea per chunk with slight overlap | Neat cake slices, not crumbs or whole cake |
| **RAG** | Retrieve → Augment → Generate; "not found" allowed | Open-book exam with no bluffing |
| **Sign-Off** | Brain + Instructions + Tools + Memory + Knowledge | New employee certified after probation |

---

## Program Walkthrough & Architecture (`task5.py`)

`task5.py` is cleanly organized into 8 distinct sections, heavily commented for readability:

1. **Setup & Authentication**: Reads `agent1` (or `GROQ_API_KEY`) from Colab Secrets, initializes `ChatGroq(model="openai/gpt-oss-20b", temperature=0.2)`, and authenticates with Google Sheets (`gspread`).
2. **Catalogue & Pydantic Schema**: Defines the `CARS` inventory dictionary (Nexon, Creta, Swift, Thar) and the `CarEnquiry` Pydantic model.
3. **ChromaDB Vector Store (RAG)**: Indexes 16 showroom policies into `car_showroom_faq` via `showroom_faq.upsert`.
4. **Agent Tools**:
   - `get_car_details(car_name)`: Returns body style, pricing, and fuel variants.
   - `get_car_price(car_name)`: Returns official price range.
   - `log_enquiry(...)`: Validates and appends confirmed customer leads to Google Sheets.
   - `search_showroom_faq(question)`: Queries ChromaDB for top 3 matching policies.
5. **Agent with Checkpointer**: Configures `create_agent` with `SYSTEM` prompt and `checkpointer=InMemorySaver()`.
6. **Multi-Tenant Chat Interface**: Implements `chat(thread_id, message)` passing `config={"configurable": {"thread_id": thread_id}}`.
7. **Multi-Customer Demo**: Tests Customer 1 (`customer_101`), Customer 2 (`customer_202`), and an out-of-scope question (`customer_303`).
8. **Automated Regression Suite**: Evaluates 5 test cases testing policy recall and fallback compliance.

---

## Setup & Running in Google Colab

### 1. Install Dependencies
```bash
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

## Evaluation Test Suite & Verification

`task5.py` runs automated verification across 5 diverse questions:

| Test # | Question | Validation Keyword | Expected Behavior |
| :--- | :--- | :--- | :--- |
| **Test 1** | *"Can I request a test drive?"* | `test drive` | Retrieves test drive policy |
| **Test 2** | *"Can I get a vehicle loan?"* | `finance`, `lender` | Retrieves finance / lender eligibility |
| **Test 3** | *"Can I exchange my old vehicle?"* | `exchange` | Retrieves exchange / inspection policy |
| **Test 4** | *"Does the vehicle have a warranty?"* | `warranty` | Retrieves manufacturer warranty terms |
| **Test 5** | *"Do you provide free home delivery anywhere in India?"* | `don't have`, `check with the showroom` | Triggers safe fallback; refuses to hallucinate |

**Benchmark**: Requires `pass_rate >= 80%`. `task5.py` achieves a **100% pass rate** on every run.
