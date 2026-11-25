# Day 3 · Your First Agent: What an Agent Is, and LangChain

## Overview
Day 3 transitions from one-off chatbot prompts to **LangChain LCEL chains**, **systematic regression testing via test datasets (`tests.csv`)**, **prompt improvement cycles**, **temperature sensitivity analysis**, and **job classification (Agent vs. LLM call vs. Plain code)**.

The implementation in `task3.py` applies all Day 3 concepts directly to the **AI Car Showroom Assistant** case study.

---

## Task Implementation Details (`task3.py`)

The code in `task3.py` is organized into 9 structured sections:

### 1. Business System Prompt & Showroom Catalog
- **Authentication & Model**: Retrieves the Groq API key from Colab Secrets (`userdata.get("agent1")`) and connects to `openai/gpt-oss-20b`.
- **Catalogue (`CARS`)**: Structured inventory dictionary for showroom vehicles:
  - **Tata Nexon**: ₹8–15 lakh | Petrol, Diesel, Electric | SUV
  - **Hyundai Creta**: ₹11–20 lakh | Petrol, Diesel | SUV
  - **Maruti Suzuki Swift**: ₹6–9 lakh | Petrol | Hatchback
  - **Mahindra Thar**: ₹11–18 lakh | Petrol, Diesel | SUV
- **System Prompt**: Defines the showroom assistant persona, dynamic `{car_catalogue}` facts, 8 operational rules, dynamic `{extra_rule}` placeholder for iterative improvements, and concise formatting constraints.

### 2. LangChain Chain Construction (`create_chain`)
Builds a reusable LangChain pipeline using the pipe operator (`|`):
```python
chain = prompt | llm | StrOutputParser()
```
- **`ChatGroq`**: Language model initialized with parameterized temperature.
- **`ChatPromptTemplate`**: Formatted with the system prompt, `MessagesPlaceholder("history")` for conversational context, and human query `{question}`.
- **`prompt.partial(...)`**: Dynamically binds the car catalogue JSON and any optional rule additions without recreating the template from scratch.
- **`StrOutputParser`**: Extracts clean string output from the LLM's response.

### 3. Automated Test Suite (`tests.csv`)
Automatically generates a 10-question evaluation dataset (`tests.csv`) representing real customer inquiries paired with mandatory keywords/phrases (`must_include`):
| # | Customer Question | Must Include | Evaluates |
|---|---|---|---|
| 1 | What is the price of Tata Nexon? | `8–15` | Price accuracy |
| 2 | Tell me about Hyundai Creta. | `creta` | Model knowledge |
| 3 | Which car is an electric SUV? | `nexon` | EV feature lookup |
| 4 | What is the price of Maruti Swift? | `6–9` | Hatchback pricing |
| 5 | Tell me about Mahindra Thar. | `thar` | Off-road SUV facts |
| 6 | Which cars have diesel fuel? | `diesel` | Fuel filter query |
| 7 | Which car is a hatchback? | `swift` | Body type classification |
| 8 | Do you have a BMW? | `showroom` | Fallback rule compliance |
| 9 | What fuel types are available in Tata Nexon? | `electric` | Variant verification |
| 10 | What type of vehicle is Hyundai Creta? | `SUV` | Vehicle type recall |

### 4. Test Runner & Pass Rate Calculation (`run_tests`)
Reads `tests.csv`, queries the chain for each test case with a clean history (`"history": []`), performs case-insensitive verification, displays `PASS` or `FAIL` for each question, and calculates the overall percentage pass rate:
$$\text{Pass Rate} = \left(\frac{\text{Passed Tests}}{\text{Total Tests}}\right) \times 100\%$$

### 5. Baseline Evaluation
Runs the initial showroom chain at `temperature=0.2` and measures the starting baseline pass rate (`baseline_rate`).

### 6. Prompt Improvement Cycle
- **Change Made**: Injects an extra rule via `{extra_rule}`:
  ```text
  IMPORTANT:
  When a requested car is not in the catalogue,
  clearly include the exact phrase 'confirm with the showroom'.
  ```
- **Regression Evaluation**: Re-runs the test suite against `improved_chain` (`improved_rate`) and quantitatively compares the pass rate before and after the prompt change.

### 7. Temperature Sensitivity Analysis (`temperature = 1.0`)
- Explores model behavior under higher randomness (`temperature = 1.0`).
- Runs the test suite **twice** on the same creative chain to observe whether non-zero temperature causes answer variance or shifts the pass rate between runs (`Run 1` vs `Run 2`).

### 8. Agent or Not? (Job Classification)
Categorizes three common showroom operations based on architectural complexity:
1. **"Calculate the total car price with a fixed discount"** $\rightarrow$ **Plain Code**
   *(Exact arithmetic with predetermined formulas; no AI required).*
2. **"Explain the features of Tata Nexon"** $\rightarrow$ **One LLM Call**
   *(Single text generation request from known catalogue facts).*
3. **"Understand customer requirements, look up multiple cars, compare them and recommend a suitable car"** $\rightarrow$ **Agent**
   *(Dynamic multi-step goal requiring understanding, tool lookups, comparisons, and iterative reasoning).*

### 9. Interactive Showroom Chat
Interactive conversation loop allowing live testing with customer memory:
- Appends each turn to `history` (`("human", user_text)` and `("ai", answer)`).
- Carries customer context forward across multiple questions.
- Exits cleanly on typing `exit`, `bye`, or `quit`.

---

## File Structure
```
day3/
├── task3.py     # Complete Day 3 implementation (Catalogue, Chain, Evals, Comparisons & Chat)
├── tests.csv    # Generated evaluation dataset (10 questions + must_include assertions)
└── readme.md    # Detailed documentation matching task3.py
```

---

## Setup & Execution

### 1. Install Dependencies
```bash
pip install -qU langchain langchain-groq
```

### 2. Configure API Key
In Google Colab, add your Groq API key in the **Secrets** tab (key icon) as `agent1`.

If running locally:
```bash
# Windows PowerShell
$env:agent1 = "your_groq_api_key_here"

# Linux / macOS
export agent1="your_groq_api_key_here"
```

### 3. Run the Script
```bash
python task3.py
```

---

## Sample Console Output

```text
tests.csv created successfully.

========== BASELINE TEST ==========
PASS | What is the price of Tata Nexon? -> The Tata Nexon is priced between ₹8–15 lakh.
PASS | Tell me about Hyundai Creta. -> The Hyundai Creta is a popular SUV priced at ₹11–20 lakh...
...
Pass rate: 9/10 = 90%

========== IMPROVED PROMPT TEST ==========
PASS | Do you have a BMW? -> We currently do not have BMW vehicles. Please confirm with the showroom.
...
Pass rate: 10/10 = 100%

========== IMPROVEMENT COMPARISON ==========
Before improvement: 90 %
After improvement: 100 %
Result: Pass rate increased.

========== TEMPERATURE COMPARISON ==========
Run 1: 90 %
Run 2: 90 %

========== AGENT OR NOT? ==========
Calculate the total car price with a fixed discount -> Plain code
Explain the features of Tata Nexon -> One LLM call
Understand customer requirements, look up multiple cars, compare them and recommend a suitable car -> Agent

========== CAR SHOWROOM ASSISTANT ==========
You: Hi, I'm Rahul. What is the price of Thar?
Bot: Hello Rahul! The Mahindra Thar is priced between ₹11–18 lakh.
```
