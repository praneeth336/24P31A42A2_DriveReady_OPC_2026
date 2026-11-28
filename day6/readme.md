# Day 6 · Workflows, Planning, and LangGraph

## Overview
Day 6 introduces **Multi-Agent Systems (Level 3)**. Instead of one single agent doing everything, we build a **LangGraph Router Workflow** that:
1. **Sorts incoming customer messages** (`order`, `faq`, or `other`).
2. **Routes each message** to a specialized agent with only the tools it needs.
3. **Visualizes and streams** the execution step-by-step.

---

## Key Concepts & Simple Analogies

### 1. Workflows vs. Agents
- **Workflow (The Train)**: Follows fixed tracks and stations in a set order. Used for predictable business steps (classify → route → handle).
- **Agent (The Auto-Rickshaw)**: Chooses its own route and decides which tools to pick as it goes.
- **The Pattern**: **Workflow on the outside, agents on the inside.**

### 2. Planning Techniques
- **Chain-of-Thought (CoT)**: Reasons step-by-step in one response (*showing work in a math exam*).
- **ReAct**: Thinks, calls a tool, observes the result, and repeats (*tasting food while cooking*).
- **Plan-and-Execute**: Writes a full numbered plan first, then executes each step (*a wedding planner's checklist*).

### 3. The Router (Hospital Reception Desk)
Before LangGraph, routing is just classification + `if/else`:
- A reception desk listens to each customer and points them to the right room.
- LangGraph lets you turn this logic into a visual, debuggable graph.

### 4. State (The Job Card)
- In LangGraph, every step shares one dictionary defined with `TypedDict`:
  ```python
  class BakeryState(TypedDict):
      message: str   # Customer message
      intent: str    # Set by classify node
      reply: str     # Set by handler node
  ```
- **Analogy**: A **car service job card**. The advisor writes the complaint, the mechanic writes the work done, and the cashier writes the bill. Each person adds their section without rewriting the whole card.

### 5. Nodes and Edges (The Metro Map)
- **Node**: A Python step/function.
- **Edge**: An arrow connecting one step to the next.
- **Flow**: `START` → `classify` → `[order / faq / other]` → `END`.

### 6. Conditional Edges (Traffic Police at a Junction)
- A routing function (`route(state)`) inspects the `intent` in state and chooses which road the message takes:
  - `"order"` → `order` node
  - `"faq"` → `faq` node
  - `"other"` → `other` node

### 7. Observability: `invoke()` vs. `stream()`
- `graph.invoke(...)`: Shows only the final output (*the final score*).
- `graph.stream(...)`: Shows what each node changed in order (*ball-by-ball commentary*). If a message goes to the wrong path, streaming instantly tells you why.

### 8. Specialist Agents Inside the Graph
- **`faq_agent`**: Has `[search_faq, get_price, is_open]`. Cannot save orders.
- **`order_agent`**: Has `[get_price, log_order]`. Focused on collecting order details.
- **`other`**: Simple polite reply without spending tokens on extra agent reasoning.

---

## Day 6 Summary in One Table

| Concept | What It Does | Real-World Analogy |
| :--- | :--- | :--- |
| **Workflow vs Agent** | Fixed path vs dynamic reasoning | Train vs auto-rickshaw |
| **Planning Techniques** | CoT, ReAct, and Plan-and-Execute | Show math steps, taste while cooking, checklist |
| **Router** | Classify intent once, then branch | Hospital reception desk |
| **State (`TypedDict`)** | Shared dictionary passed across nodes | Job card at a car service center |
| **Nodes & Edges** | Steps and connecting arrows | Stations and tracks on a metro map |
| **Conditional Edges** | Runtime branching based on state values | Traffic police officer at a junction |
| **Streaming** | Step-by-step observation of graph updates | Ball-by-ball cricket commentary |
| **Specialist Agents** | Scoped tools and prompts per role | College office departments (Admissions, Exams) |

---

## Program Structure (`task6.py`)

1. **Setup**: Connects to Groq (`openai/gpt-oss-20b`) via Colab Secrets (`agent1` or `GROQ_API_KEY`).
2. **State & Classifier**: Defines `BakeryState` and Pydantic `Intent` (`order`, `faq`, `other`).
3. **Specialist Agents**: Creates `faq_agent` and `order_agent` with scoped tools.
4. **Nodes & Router**: Builds node functions (`classify`, `answer_faq`, `take_order`, `other`) and `route`.
5. **Graph Compilation**: Connects nodes with `START`, conditional edges, and `END`, then compiles.
6. **Streaming Tests**: Runs test messages through `graph.stream` to inspect updates.
7. **Text-based Classifier**: Shows a prompt-based classification approach for comparison.

---

## How to Run in Google Colab

1. **Install Packages**:
   ```bash
   !pip install -qU langchain langchain-groq langgraph langchain-core
   ```
2. **Add Secret**:
   - Go to **Secrets (key icon)** in Colab.
   - Name: `agent1` (or `GROQ_API_KEY`).
   - Value: *Your Groq API key*.
3. **Execute**:
   ```bash
   python task6.py
   ```

---

## Sample Test Results

```text
CUSTOMER: What are your bakery opening hours?
  -> GRAPH UPDATE: {'classify': {'intent': 'faq'}}
  -> GRAPH UPDATE: {'faq': {'reply': 'Sweet Crumbs is open Monday to Saturday 9 AM to 8 PM, Sunday 10 AM to 6 PM.'}}

CUSTOMER: I want to order 2 eggless plum cakes.
  -> GRAPH UPDATE: {'classify': {'intent': 'order'}}
  -> GRAPH UPDATE: {'order': {'reply': 'I can help with that! May I have your name and preferred pickup date?'}}

CUSTOMER: Hello, good morning!
  -> GRAPH UPDATE: {'classify': {'intent': 'other'}}
  -> GRAPH UPDATE: {'other': {'reply': 'Hello from Sweet Crumbs! I can help with cakes, prices, orders and bakery policies.'}}
```
