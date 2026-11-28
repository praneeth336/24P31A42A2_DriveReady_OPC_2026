# Day 6 · Workflows, Planning, and LangGraph

## Overview
Day 6 marks the transition from **Level 2 (Single-Agent Systems)** to **Level 3 (Multi-Agent Systems & Workflows)**.

Instead of relying on a single monolith agent to handle every request, we build an intelligent **Router Workflow** using **LangGraph**:
- **Outer Architecture**: A deterministic state graph controlling message paths (`START -> classify -> route -> handler -> END`).
- **Inner Architecture**: Focused specialist sub-agents (`faq_agent` and `order_agent`), each equipped with only the specific tools and prompts they need.
- **Observability**: Live step streaming (`graph.stream`) and visual graph rendering (`draw_mermaid_png`).

---

## Core Topics & Theoretical Foundations

### 1. Workflows vs. Agents
| Dimension | Workflow | Agent |
| :--- | :--- | :--- |
| **Who decides the path?** | You, explicitly in code | The model, dynamically at runtime |
| **Predictability** | High: same input always follows the specified steps | Variable: chooses different tools/steps per invocation |
| **Best Used For** | Fixed business processes (order -> check -> approve -> save) | Open-ended exploration ("help me plan a customized party") |
| **Sweet Crumbs Pattern** | Every message is classified first: `order`, `faq`, or `other` | Inside each path, the specialist agent decides tool calls |

> **Real-World Analogy (The Train vs. The Auto-Rickshaw)**:
> - A **train** follows fixed tracks and scheduled stations (**Workflow**). Rules like owner approval can never be skipped.
> - An **auto-rickshaw** navigates freely through streets and traffic (**Agent**).
> - Production AI systems combine both: **a workflow on the outside, agents on the inside**.

---

### 2. Planning Techniques: How Models Reason
| Technique | How It Operates | Best Used For | Real-World Analogy |
| :--- | :--- | :--- | :--- |
| **Chain-of-Thought (CoT)** | Prompts the model to reason step-by-step before producing a single reply | Single-turn arithmetic and logic without tools | Showing your steps in a math exam |
| **ReAct** (Days 3–5) | Executes a dynamic loop: `Think -> Act (Tool) -> Observe -> Repeat` | Tasks where each step depends on external tool outputs | Cooking while tasting as you go |
| **Plan-and-Execute** | First writes a full numbered plan, executes each step sequentially, then verifies | Complex multi-stage requests (e.g. bulk party order) | A wedding planner's detailed checklist |

---

### 3. Router in Plain Python vs. LangGraph
Before using LangGraph, routing can be achieved with a simple structured classifier and `if/elif/else`:
```python
intent = classifier.invoke(message).intent
if intent == "order":
    return take_order(message)
elif intent == "faq":
    return answer_faq(message)
else:
    return general_reply(message)
```
> **Hospital Reception Desk Analogy**:
> A receptionist listens to the patient's complaint and directs them to Cardiology, Orthopedics, or General Inquiry. The receptionist doesn't perform medical treatments; they only route.

**Why upgrade to LangGraph?**
As systems grow, plain `if/else` becomes unwieldy. LangGraph enables:
1. Visualizing the workflow as a flowchart (`draw_mermaid_png`).
2. Centralized shared state that travels across nodes.
3. Pausing for human-in-the-loop approval (Day 7).
4. Multi-agent supervision and cyclical review loops (Day 8).

---

### 4. LangGraph State (`BakeryState`)
Every node in LangGraph reads from and writes to a central typed dictionary called **State**:
```python
class BakeryState(TypedDict):
    message: str   # Customer query
    intent: str    # Filled by classify node
    reply: str     # Filled by faq / order / other node
```
> **Car Service Center Job Card Analogy**:
> When a car enters service, one physical job card moves between stations. The advisor records the issue, the mechanic notes the repairs, and the cashier writes the bill. Each technician adds their section without rewriting the whole card.

---

### 5. Nodes, Edges, and Graph Lifecycle
- **Node**: A Python function that takes `state` as input and returns a dictionary updating only the keys it modified:
  ```python
  def classify(state: BakeryState) -> dict:
      return {"intent": classifier.invoke(state["message"]).intent}
  ```
- **Edge**: Directed arrow connecting one step to the next (`builder.add_edge(START, "classify")`).
- **Graph Assembly Steps**:
  1. Initialize `builder = StateGraph(BakeryState)`
  2. Register nodes: `builder.add_node("name", func)`
  3. Connect entrypoint and exits: `START`, `END`
  4. Compile: `graph = builder.compile()`

---

### 6. Conditional Edges (Branching Decisions)
Conditional edges inspect the state dynamically and route execution down matching branches:
```python
def route(state: BakeryState) -> str:
    return state["intent"]

builder.add_conditional_edges(
    "classify",
    route,
    {
        "order": "order",
        "faq": "faq",
        "other": "other"
    }
)
```
> **Traffic Police at a Junction Analogy**:
> One road enters the intersection, but three roads exit. An officer checks each vehicle's permit (intent) and waves it down the corresponding street.

---

### 7. Observability: `invoke()` vs. `stream()`
- `graph.invoke(...)`: Returns only the final state (the "final score").
- `graph.stream(..., stream_mode="updates")`: Emits each node's output as it finishes (the "ball-by-ball replay").
  - If a message routes incorrectly, streaming immediately reveals whether the mistake occurred in the `classify` node or the downstream handler.

---

### 8. Specialist Agents Inside the Workflow
By decomposing a monolithic bot into specialized agents, each agent receives fewer tools and a focused prompt:
- **`faq_agent`**: Tools `[search_faq, get_price, is_open]`. Lacks `log_order`, making it **impossible** for it to accidentally place an order.
- **`order_agent`**: Tools `[get_price, log_order]`. Focused on parameter collection (name, item, quantity, date).
- **`other`**: Static polite greeting with zero token overhead.

---

## Day 6 in One Table

| Concept | Definition | Real-World Analogy |
| :--- | :--- | :--- |
| **Workflow vs Agent** | Fixed path vs dynamic reasoning | Train vs auto-rickshaw |
| **Planning Techniques** | CoT, ReAct, and Plan-and-Execute | Show math working, taste while cooking, wedding checklist |
| **Router** | Classify intent once, then branch | Hospital reception desk |
| **State (`TypedDict`)** | Shared dictionary passed across nodes | Job card at a car service center |
| **Nodes & Edges** | Python steps and connecting arrows | Stations and tracks on a metro map |
| **Conditional Edges** | Runtime branching based on state values | Traffic police officer at a junction |
| **Streaming** | Real-time observation of each step's update | Ball-by-ball cricket commentary |
| **Specialist Agents** | Scoped tools and prompts per role | College office departments (Admissions, Exams) |

---

## Program Walkthrough (`task6.py`)

`task6.py` is organized into 7 clean modules:
1. **Setup & Initialization**: Securely fetches API keys from Colab Secrets and configures Groq LLM (`openai/gpt-oss-20b`).
2. **State & Classifier**: Defines `BakeryState` and Pydantic `Intent` (`Literal["order", "faq", "other"]`).
3. **Specialist Agents**:
   - `faq_agent`: Dedicated to policy queries, pricing, and operating hours.
   - `order_agent`: Dedicated to taking cake orders with field validation.
4. **Graph Nodes & Routing**:
   - `classify`: Executes intent detection.
   - `answer_faq` & `take_order`: Invocations of the specialist agents.
   - `other`: Fallback greeting.
   - `route`: Reads `state["intent"]` for conditional branching.
5. **Workflow Compilation & Visualization**: Compiles the graph and generates a Mermaid diagram.
6. **Streaming Execution**: Tests order, FAQ, and greeting queries with step-by-step update logging.
7. **Alternative Classifier**: Pure prompt-based text classifier for comparative benchmarking.

---

## Setup & Running in Google Colab

### 1. Install Dependencies
```bash
!pip install -qU langchain langchain-groq langgraph langchain-core
```

### 2. Configure Secrets
In Google Colab, add your Groq key under **Secrets (key icon)**:
- **Name**: `agent1` (or `GROQ_API_KEY`)
- **Value**: *Your Groq API key*

### 3. Run the Script
```bash
python task6.py
```

---

## Sample Execution Log

```text
==================================================
CUSTOMER: What are your bakery opening hours?
==================================================
GRAPH UPDATE: {'classify': {'intent': 'faq'}}
GRAPH UPDATE: {'faq': {'reply': 'Sweet Crumbs is open Monday to Saturday 9 AM to 8 PM, Sunday 10 AM to 6 PM.'}}

==================================================
CUSTOMER: I want to order 2 eggless plum cakes.
==================================================
GRAPH UPDATE: {'classify': {'intent': 'order'}}
GRAPH UPDATE: {'order': {'reply': 'I would love to help you with that! May I please have your name and the preferred pickup date?'}}

==================================================
CUSTOMER: Hello, good morning!
==================================================
GRAPH UPDATE: {'classify': {'intent': 'other'}}
GRAPH UPDATE: {'other': {'reply': 'Hello from Sweet Crumbs! I can help with cakes, prices, orders and bakery policies.'}}
```
