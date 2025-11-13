import os
import time
import random
import datetime
import google.generativeai as genai

# ✅ Configure Gemini safely
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("⚠️ GEMINI_API_KEY not found. Please export it before running Streamlit.")

genai.configure(api_key=api_key)

MODEL_NAME = "gemini-2.5-flash"

# 🧠 Enhanced Base Prompt — Full Dataset Awareness + Adaptive Conversational Handling
BASE_PROMPT = """
You are a professional Python Data Analyst.
You are given a variable called `datasets` containing multiple Pandas DataFrames from the Olist E-Commerce dataset.

Available DataFrames:
- datasets["olist_orders_dataset"]
- datasets["olist_order_items_dataset"]
- datasets["olist_products_dataset"]
- datasets["product_category_name_translation"]
- datasets["olist_order_reviews_dataset"]
- datasets["olist_order_payments_dataset"]
- datasets["olist_customers_dataset"]
- datasets["olist_sellers_dataset"]
- datasets["olist_geolocation_dataset"]

Each DataFrame is preloaded in memory — never read files or fetch external data.

---

🚫 NEVER:
- Create, simulate, or assume any data.
- Guess summaries or random numbers.
- Use file I/O, os/sys calls, eval, exec, or web requests.
- Use libraries other than pandas and matplotlib.
- Print anything other than the final summary.

✅ ALWAYS:
1️⃣ Use only real data from `datasets`.
2️⃣ Perform legitimate Pandas operations (merge, groupby, mean, sum, etc.).
3️⃣ Handle NaN safely using fillna() or dropna().
4️⃣ Call plt.show() for any visualization.
5️⃣ Keep axis labels, titles, and layout clean.

---

### 💬 Adaptive Conversational Mode (No Code)
If the user’s query is conversational, emotional, or general (like greetings, small talk, motivation, or concept discussion):
- DO NOT generate or execute any Python code.
- DO NOT access or analyze datasets.
- Respond in natural, human-like text only — friendly, situational, and context-aware.
- Avoid robotic tone or repeated phrases.
- Keep responses concise and natural.
- If the user later asks for data or analysis, smoothly transition back to analytical mode.

---

### 📊 Analytical Mode (Code Generation)

#### 1️⃣ Ranking or Extremes Queries
(Keywords: top, highest, lowest, largest, smallest, most, least)
- Compute a ranking (min. top/bottom 10).
- Use .idxmax() and .idxmin() for accuracy.
- Include all results in RESULT['table'].
- Plot with plt.barh().
- Mention both top and bottom items in summary.

#### 2️⃣ Trend or Time-Series Queries
(Keywords: trend, over time, monthly, yearly, growth, timeline)
- Convert date columns to datetime.
- Group by time period.
- Plot with plt.plot().
- Summarize pattern clearly (growth, stability, or decline).

#### 3️⃣ Aggregation or Average Queries
(Keywords: mean, median, total, sum, revenue, delay, performance)
- Use groupby() + aggregation.
- Include all results in RESULT['table'].
- Plot with bar/barh.
- Mention highest and lowest groups in summary.

#### 4️⃣ Proportion or Comparison Queries
(Keywords: percentage, ratio, share, distribution, compare)
- Compute proportions in %.
- Plot with plt.pie() or plt.bar().
- Include category–percentage pairs.

#### 5️⃣ Descriptive or Summary Queries
(Keywords: describe, statistics, breakdown)
- Use df.describe() or numeric summaries.
- Include result in RESULT['table'].
- Plot only if meaningful.

---

🧩 FINAL OUTPUT FORMAT
At the end of every analysis:
    RESULT = {
        "summary": "<1-line factual summary>",
        "table": <list of (label, value) pairs>,
        "plot": <True if plt.show() was called, else False>
    }

print(f"✅ Summary: {RESULT['summary']}")

---

💡 VISUALIZATION RULES
- Always label axes clearly.
- Rotate long labels: plt.xticks(rotation=45, ha='right')
- Add grid lines: plt.grid(axis='x', linestyle='--', alpha=0.6)
- Use plt.tight_layout()
- Never use seaborn or any external style.

❌ No markdown, comments, or explanations.
✅ Output must be pure, runnable Python code only.
"""

# ----------------------------------------------------------
# ⚙️ Deterministic Code Generation
# ----------------------------------------------------------

def generate_code_for_query(context: str, sample: dict, user_query: str) -> str:
    """Generate context-aware Gemini output per query."""

    random_seed = random.randint(1000, 9999)

    # 🧼 Ensure fresh state each query
    try:
        genai.clear_cache()
    except Exception:
        pass

    # 🚦 Build contextual prompt
    full_prompt = f"""
{BASE_PROMPT}

-----------------------------------
🧩 CONTEXT (available dataset columns):
{context}

🧠 USER QUERY:
{user_query}

RULES:
- Respond conversationally (no code) if query is casual.
- If query involves analysis, output full executable Python code.
- Include RESULT dict and plt.show() if visual.
- Random session ID: {random_seed}
"""

    model = genai.GenerativeModel(MODEL_NAME)

    def extract_code(response):
        """Safely extract code or text from Gemini response."""
        try:
            if hasattr(response, "text") and response.text:
                return response.text
            if hasattr(response, "candidates") and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, "content") and hasattr(candidate.content, "parts"):
                    return "".join(
                        p.text for p in candidate.content.parts if hasattr(p, "text")
                    )
        except Exception:
            return ""
        return ""

    def clean_code(code):
        """Remove markdown fences."""
        return code.replace("```python", "").replace("```", "").strip()

    try:
        response = model.generate_content(
            full_prompt,
            generation_config={
                "temperature": 0.0,
                "top_p": 0.85,
                "max_output_tokens": 2500,
            },
        )

        code = clean_code(extract_code(response))

        # 🔁 Retry if empty or incomplete (and not plain text)
        if not code.strip() or ("plt.show()" not in code and "✅ Summary" not in code):
            time.sleep(0.5)
            retry_prompt = full_prompt + "\n\n⚠️ Retry — ensure a valid response (text for casual, code for analytical)."
            retry = model.generate_content(retry_prompt)
            code = clean_code(extract_code(retry))

        # 🧩 Handle conversational replies (plain text)
        if not any(kw in code for kw in ["plt.", "RESULT", "import pandas", "import matplotlib"]):
            # conversational reply — return directly
            return code.strip()

        # 🪵 Log valid code
        os.makedirs("logs", exist_ok=True)
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(f"logs/generated_code_{ts}.py", "w") as f:
            f.write(code)

        return code

    except Exception as e:
        log_issue(f"Error generating code: {e}", user_query, full_prompt)
        return f"print('⚠️ Gemini internal error: {e}')"

# ----------------------------------------------------------
# 🪵 Logging for debugging
# ----------------------------------------------------------

def log_issue(message, query, prompt):
    """Log Gemini issues for debugging."""
    os.makedirs("logs", exist_ok=True)
    with open("logs/gemini_failures.log", "a") as f:
        f.write(
            f"\n[{datetime.datetime.now()}] {message}\nQuery: {query}\nPromptID: {hash(prompt)}\n{'-'*80}\n"
        )