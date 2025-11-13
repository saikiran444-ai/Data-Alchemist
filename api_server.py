from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
import pandas as pd
from utils.gemini_api import generate_code_for_query
from utils.code_executor import run_generated_code  # ✅ Added
import io, base64, matplotlib.pyplot as plt

app = FastAPI()

# Allow frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load your existing datasets
def load_datasets():
    base = "data"
    datasets = {}
    print("🔹 Checking data folder...")

    important_files = [
        "olist_orders_dataset.csv",
        "olist_order_items_dataset.csv",
        "olist_order_payments_dataset.csv",
        "olist_customers_dataset.csv",
        "olist_order_reviews_dataset.csv"
    ]

    for f in important_files:
        path = os.path.join(base, f)
        if not os.path.exists(path):
            print(f"⚠️ Skipping missing file: {f}")
            continue

        print(f"➡️ Loading {f} ...")
        try:
            df = pd.read_csv(path, nrows=50000)
            datasets[f.replace(".csv", "")] = df
            print(f"✅ Loaded {f} ({len(df)} rows)")
        except Exception as e:
            print(f"❌ Error loading {f}: {e}")

    print("✅ Essential datasets loaded successfully.")
    return datasets

datasets = load_datasets()

# Model for chat input
class Query(BaseModel):
    query: str

@app.get("/api/data")
def get_data():
    """Send KPI + chart data to frontend"""
    try:
        orders = datasets.get("olist_orders_dataset")
        payments = datasets.get("olist_order_payments_dataset")
        customers = datasets.get("olist_customers_dataset")
        reviews = datasets.get("olist_order_reviews_dataset")

        total_orders = len(orders)
        total_customers = customers["customer_unique_id"].nunique()
        total_revenue = payments["payment_value"].sum()
        avg_order_value = payments["payment_value"].mean()
        avg_review = reviews["review_score"].mean()

        return {
            "kpis": {
                "total_orders": total_orders,
                "total_customers": total_customers,
                "total_revenue": total_revenue,
                "avg_order_value": avg_order_value,
                "avg_review": avg_review
            },
            "revenue_by_state": customers["customer_state"].value_counts().head(6).to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ✅ Enhanced endpoint — executes Gemini’s generated code
@app.post("/api/query_gemini")
def query_gemini(req: Query):
    """Handle chat query, generate code using Gemini, run it, return result + visualization."""
    from utils.code_executor import run_generated_code

    try:
        context = [f"{name} has columns: {', '.join(df.columns)}" for name, df in datasets.items()]
        context_str = "\n".join(context)
        sample = datasets.get("olist_orders_dataset", pd.DataFrame()).head(2).to_dict(orient="records")

        # ✅ Ask Gemini to generate code
        code_or_text = generate_code_for_query(context_str, sample, req.query)

        # ✅ Force Gemini output into executable code block if not pure text
        if "import" not in code_or_text:
            return {"response": code_or_text, "type": "text"}

        # ✅ Execute the generated code
        output, fig = run_generated_code(datasets, code_or_text)

        # ✅ Convert figure to base64 image
        img_data = None
        if fig:
            buf = io.BytesIO()
            fig.savefig(buf, format="png", bbox_inches="tight")
            buf.seek(0)
            img_data = base64.b64encode(buf.read()).decode("utf-8")
            buf.close()

        # ✅ Send both text + image + code to frontend
        return {
            "response": output,
            "image": img_data,
            "code": code_or_text
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)