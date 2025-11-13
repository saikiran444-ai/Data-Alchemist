# app.py (patched - keeps your logic, only fixes glow + safety checks)
import streamlit as st
import pandas as pd
import os
import re, ast
import matplotlib.pyplot as plt
from utils.gemini_api import generate_code_for_query
from utils.code_executor import run_generated_code
from utils.chat_memory import init_chat, add_chat_entry
import plotly.graph_objects as go
import plotly.express as px
import time  # ⏱️ Added for timing
import tempfile
import streamlit.components.v1 as components

print("🔹 Step 1: Imports done")
time.sleep(0.5)

print("🔹 Step 2: Loading datasets now...")
start = time.time()

# # 🎨 GLOBAL CSS + Neon Mouse Glow + Remove that weird blue semicircle
# st.markdown("""
# <style>

# html, body, [data-testid="stAppViewContainer"] {
#     background: #0f172a !important;
#     overflow-x: hidden !important;
# }

# /* Smooth fade-in */
# .stApp {
#     animation: fadein 0.8s ease-in-out;
# }
# @keyframes fadein {
#     from { opacity: 0; transform: translateY(8px); }
#     to { opacity: 1; transform: translateY(0); }
# }

# /* Remove the default Streamlit blue bar (the one you see bottom-right!) */
# [data-testid="stDecoration"] {
#     display: none !important;
# }

# /* Neon glow on hover for blocks */
# div[data-testid="stVerticalBlock"] > div:hover {
#     transition: 0.15s ease;
#     box-shadow: 0 0 28px rgba(56,189,248,0.35);
# }

# /* Sidebar hover */
# section[data-testid="stSidebar"] div:hover {
#     background: rgba(255,255,255,0.07);
#     border-radius: 8px;
# }

# /* 🌈 FOLLOW MOUSE GLOW */
# #mouseGlow {
#     position: fixed;
#     width: 280px;
#     height: 280px;
#     pointer-events: none;
#     border-radius: 50%;
#     background: radial-gradient(
#         circle,
#         rgba(56,189,248,0.45),
#         rgba(124,58,237,0.25),
#         transparent 70%
#     );
#     filter: blur(50px);
#     transform: translate(-50%, -50%);
#     transition: opacity 0.1s ease-out;
#     opacity: 0;
#     z-index: 9999;  /* 🔥🔥 now it will be visible */
# }
# </style>

# <div id="mouseGlow"></div>

# <script>
# document.addEventListener("mousemove", (e) => {
#     const glow = document.getElementById("mouseGlow");
#     glow.style.left = e.clientX + "px";
#     glow.style.top = e.clientY + "px";
#     glow.style.opacity = 1;
# });
# document.addEventListener("mouseleave", () => {
#     document.getElementById("mouseGlow").style.opacity = 0;
# });
# </script>
# """, unsafe_allow_html=True)

# 🎯 Streamlit Page Setup
st.set_page_config(page_title="Gemini Data Analyst", page_icon="🤖", layout="wide")

# 🌈🔥 ANIMATED GRADIENT TITLE — “DATA ALCHEMIST”
st.markdown("""
<style>

.title-wrapper {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-top: 25px;
    margin-bottom: 0px;
}

/* Neon gradient animated title */
.data-alchemist-title {
    font-family: "Poppins", sans-serif;
    font-size: 70px;
    text-transform: uppercase;
    background: linear-gradient(
        to right,
        #fc72ff,
        #8f68ff,
        #487bff,
        #8f68ff,
        #fc72ff
    );
    background-size: 220%;
    background-clip: text;
    -webkit-background-clip: text;
    color: transparent;
    -webkit-text-fill-color: transparent;
    animation: title-animate 3s linear infinite;
    letter-spacing: 3px;
}

@keyframes title-animate {
    to {
        background-position: 200%;
    }
}

/* Subtitle styling */
.subtitle-text {
    text-align: center;
    color: #d1d5db;  /* soft gray-white */
    font-size: 20px;
    margin-top: -10px;
    margin-bottom: 25px;
    letter-spacing: 1px;
}

</style>

<div class="title-wrapper">
    <h1 class="data-alchemist-title">DATA ALCHEMIST</h1>
</div>

<p class="subtitle-text">
    Chat with Gemini — your AI data analyst for the Olist E-Commerce dataset!
</p>

""", unsafe_allow_html=True)

# 🎨 GLOBAL CSS + REMOVED BLUE SEMICIRCLE + SUPER NEON GLOW
st.markdown("""
<style>

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background: linear-gradient(135deg, #0a0f1f, #000212) !important;
}


/* Remove default streamlit highlight decoration */
[data-testid="stDecoration"] {
    display: none !important;
}



/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: #0d0d10 !important;
}
[data-testid="stSidebarContent"] {
    background: #0d0d10 !important;
}

/* RESTORE INSIGHT BOX COLOR */
.insight-card {
    background: linear-gradient(135deg, #1e293b, #334155) !important;
    border-radius: 14px !important;
    padding: 22px !important;
    box-shadow: 0 4px 18px rgba(0,0,0,0.35) !important;
}

/* RESTORE PIE CHART BOX COLOR */
.chart-card {
    background: #0c1220 !important;
    border-radius: 12px !important;
    padding: 20px !important;
    box-shadow: 0 0 25px rgba(0,150,255,0.1) !important;
}

/* FIX PLOTLY BG */
.js-plotly-plot .plotly, .js-plotly-plot {
    background: #0c1220 !important;
}
svg .bg {
    fill: #0c1220 !important;
}

/* CHAT */
[data-testid="stChatMessage"] {
    background: transparent !important;
}
[data-testid="stChatInput"] {
    background: #000 !important;
    border-top: 1px solid #333 !important;
}

/* SUPER EXTREME NEON GLOW */
#mouseGlow {
    position: fixed;
    width: 3000px;    /* 🔥 HUGE — 20x bigger */
    height: 3000px;   /* 🔥 HUGE — 20x bigger */
    pointer-events: none;
    border-radius: 50%;
    background: radial-gradient(
        circle,
        rgba(0,255,255,0.75),   /* brighter cyan */
        rgba(180,0,255,0.65),   /* brighter purple */
        rgba(0,0,0,0) 80%
    );
    filter: blur(320px);        /* 🔥 insane blur */
    transform: translate(-50%, -50%);
    opacity: 0;
    transition: opacity 0.03s linear;
    z-index: 999999999 !important;
}
</style>

<div id="mouseGlow"></div>

<script>
document.addEventListener("mousemove", (e) => {
    const glow = document.getElementById("mouseGlow");
    glow.style.left = e.clientX + "px";
    glow.style.top = e.clientY + "px";
    glow.style.opacity = 1;
});
document.addEventListener("mouseleave", () => {
    document.getElementById("mouseGlow").style.opacity = 0;
});
</script>
""", unsafe_allow_html=True)

st.markdown("""
<style>
    .kpi-card {
    background: rgba(255,255,255,0.04);
    padding: 18px;
    border-radius: 16px;
    border: 1px solid rgba(255,255,255,0.06);
    backdrop-filter: blur(10px);
    width: 100%;
    height: 150px;   /* ↓ reduced */
    transition: 0.2s ease;
    text-align: center;
}

.kpi-card:hover {
    box-shadow: 0 0 22px rgba(56,189,248,0.25);
}

/* 🔥 Smaller icon */
.kpi-icon {
    font-size: 34px;   /* ↓ reduced from 42 */
    margin-bottom: 6px;
}

/* 🔥 Smaller title */
.kpi-title {
    font-size: 16px;   /* ↓ reduced */
    color: #cbd5e1;
}

/* 🔥 Smaller number */
.kpi-value {
    font-size: 30px;   /* ↓ reduced from 38/40 */
    font-weight: 700;
    margin-top: 6px;
    color: white;
}
            
/* ONLY Total Revenue box — smaller text */
.revenue-card .kpi-title {
    font-size: 14px !important;   /* smaller title */
}

.revenue-card .kpi-value {
    font-size: 18px !important;   /* smaller number */
}
            
</style>
""", unsafe_allow_html=True)

# st.title("🤖 Gemini — Dynamic E-Commerce Data Analyst")
# st.write("Chat with Gemini — your AI data analyst for the Olist E-Commerce dataset!")

# 🧠 Initialize session state (defensive)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = init_chat()
if "messages" not in st.session_state or not isinstance(st.session_state.get("messages"), list):
    st.session_state.messages = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None  # store dict {code, output, figs}

# 📂 Load Datasets
@st.cache_data
def load_datasets():
    base = "data"
    datasets = {}
    if not os.path.exists(base):
        st.error("❌ 'data' folder not found!")
        return datasets

    for f in os.listdir(base):
        if f.endswith(".csv"):
            try:
                df = pd.read_csv(os.path.join(base, f))
                datasets[f.replace(".csv", "")] = df
            except Exception as e:
                st.warning(f"⚠️ Failed to load {f}: {e}")
    return datasets

datasets = load_datasets()

print(f"✅ Step 3: Datasets loaded in {time.time()-start:.2f}s")


st.markdown("### Smart Data Insights")

try:
    orders = datasets.get("olist_orders_dataset")
    payments = datasets.get("olist_order_payments_dataset")
    customers = datasets.get("olist_customers_dataset")
    reviews = datasets.get("olist_order_reviews_dataset")

    if all([orders is not None, payments is not None, customers is not None, reviews is not None]):
        total_orders = len(orders)
        total_customers = customers["customer_unique_id"].nunique()
        total_revenue = payments["payment_value"].sum()
        avg_order_value = payments["payment_value"].mean()
        avg_review = reviews["review_score"].mean()

        top_states = customers["customer_state"].value_counts().head(3)
        top_state_str = ", ".join([f"{state} ({count})" for state, count in zip(top_states.index, top_states.values)])

        col1, col2, col3, col4, col5 = st.columns(5, gap="large")

        with col1:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">🛒</div>
                <div class="kpi-title">Total Orders</div>
                <div class="kpi-value">{total_orders:,}</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">👥</div>
                <div class="kpi-title">Total Customers</div>
                <div class="kpi-value">{total_customers:,}</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="kpi-card revenue-card">
                <div class="kpi-icon">💵</div>
                <div class="kpi-title">Total Revenue</div>
                <div class="kpi-value">R$ {total_revenue:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">📦</div>
                <div class="kpi-title">Avg Order Value</div>
                <div class="kpi-value">R$ {avg_order_value:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)

        with col5:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">⭐</div>
                <div class="kpi-title">Avg Review</div>
                <div class="kpi-value">{avg_review:.2f}</div>
            </div>
            """, unsafe_allow_html=True)


        if "olist_order_items_dataset" in datasets:
            import numpy as np
            import plotly.graph_objects as go

            items = datasets["olist_order_items_dataset"]
            merged = pd.merge(orders, customers, on="customer_id", how="inner")
            merged = pd.merge(merged, items, on="order_id", how="inner")
            state_revenue = merged.groupby("customer_state")["price"].sum().sort_values(ascending=False).head(6)

            labels = state_revenue.index
            values = state_revenue.values
            colors = ["#FF6B6B", "#FFA62B", "#FFD93D", "#6BCB77", "#4D96FF", "#C77DFF"]

            # fig = go.Figure(data=[go.Pie(
            #     labels=labels,
            #     values=values,
            #     hole=0.35,
            #     marker=dict(colors=colors,
            #                 line=dict(color="#000000", width=2)),
            #     st.markdown("#### Revenue Distribution by State ")
            #     textinfo='label+percent',
            #     textfont=dict(size=15),
            #     pull=[0.05 if i == 0 else 0 for i in range(len(values))],
            #     hovertemplate="<b>%{label}</b><br>Revenue: R$ %{value:,.0f}<br>Share: %{percent}<extra></extra>",
            # )])
            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=0.35,
                marker=dict(colors=colors,
                            line=dict(color="#000000", width=2)),
                textinfo='label+percent',
                textfont=dict(size=15),
                pull=[0.05 if i == 0 else 0 for i in range(len(values))],
                hovertemplate="<b>%{label}</b><br>Revenue: R$ %{value:,.0f}<br>Share: %{percent}<extra></extra>",
            )])

            # WRAP INSIDE THE CHART BOX
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)

            st.markdown("""
                <h3 style="color:white; margin-bottom: 12px;">
                    Revenue Distribution by State
                </h3>
            """, unsafe_allow_html=True)

            st.plotly_chart(fig, use_container_width=True, key="revenue_by_state_chart")

            st.markdown('</div>', unsafe_allow_html=True)

            # # layout simplified (safe)
            # fig.update_layout(
            #     title=dict(text="💰 Revenue Distribution by State — Elegant 3D Illusion",
            #                font=dict(color="white", size=20), x=0.5),
            #     paper_bgcolor="#0f172a",
            #     plot_bgcolor="#0f172a",
            #     showlegend=False,
            # )

            
        else:
            st.warning("⚠️ Missing `olist_order_items_dataset` — cannot generate chart.")
    else:
        st.warning("⚠️ Some datasets missing. Smart Insights unavailable.")

except Exception as e:
    st.error(f"❌ Error generating insights: {e}")

st.markdown("---")
st.markdown("### Chat with Gemini")

# Display chat history (defensive: ensure messages exists and is list)
for msg in list(st.session_state.get("messages", [])):
    try:
        with st.chat_message(msg.get("role", "assistant")):
            st.markdown(msg.get("content", ""))
    except Exception:
        # fail-safe: print minimal fallback
        st.write(msg.get("content", ""))

# 🧍 Chat input
user_input = st.chat_input("Type your question to Gemini...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    # build dataset context
    context = [f"{name} has columns: {', '.join(df.columns)}" for name, df in datasets.items()]
    context_str = "\n".join(context)
    sample = (
        datasets.get("olist_orders_dataset", pd.DataFrame()).head(2).to_dict(orient="records")
        if "olist_orders_dataset" in datasets else {}
    )

    with st.chat_message("assistant"):
        with st.spinner("Gemini is generating response..."):
            code_or_text = generate_code_for_query(context_str, sample, user_input)

        # conversational vs analytical
        if not any(x in code_or_text for x in ["import ", "plt.", "pd.", "groupby", "def "]):
            st.write(code_or_text)
            st.session_state.messages.append({"role": "assistant", "content": code_or_text})
        else:
            # analytical query
            st.markdown("#### Gemini’s Generated Code")
            st.code(code_or_text, language="python")

            with st.spinner("Running Gemini’s analysis..."):
                output, fig = run_generated_code(datasets, code_or_text)

            # summary
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #0f172a, #1e293b);
                color: #f8fafc;
                padding: 16px 20px;
                border-radius: 12px;
                font-size: 17px;
                font-weight: 600;
                line-height: 1.5;
                letter-spacing: 0.3px;
                box-shadow: 0 2px 12px rgba(0, 0, 0, 0.25);
            ">
                {output}
            </div>
            """, unsafe_allow_html=True)

            # figures
            figs = []
            if fig:
                st.markdown("#### Visualization")
                st.pyplot(fig)
                figs.append(fig)
            else:
                fig_nums = plt.get_fignums()
                if fig_nums:
                    st.markdown("#### Visualization(s)")
                    for n in fig_nums:
                        current_fig = plt.figure(n)
                        st.pyplot(current_fig)
                        figs.append(current_fig)
                    plt.close("all")

            # save last result once
            st.session_state.last_result = {
                "code": code_or_text,
                "output": output,
                "figs": figs
            }

            # add to memory
            st.session_state.chat_history = add_chat_entry(
                st.session_state.chat_history, user_input, code_or_text, output
            )
            st.session_state.messages.append({"role": "assistant", "content": output})

            st.rerun()

# 🔁 Restore last result safely
if st.session_state.last_result and not user_input:
    last = st.session_state.last_result
    st.markdown("---")
    st.markdown("### 🔁 Last Gemini Analysis")
    if last["code"]:
        st.markdown("#### 🧠 Gemini’s Generated Code")
        st.code(last["code"], language="python")
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #0f172a, #1e293b);
        color: #f8fafc;
        padding: 16px 20px;
        border-radius: 12px;
        font-size: 17px;
        font-weight: 600;
        line-height: 1.5;
        letter-spacing: 0.3px;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.25);
    ">
        {last["output"]}
    </div>
    """, unsafe_allow_html=True)
    if last["figs"]:
        st.markdown("#### 📈 Visualization(s)")
        for f in last["figs"]:
            st.pyplot(f)

# 🗂️ Sidebar Chat History
with st.sidebar:
    st.header("💬 Previous Chats")
    search = st.text_input("🔍 Search history...")
    hist = st.session_state.chat_history
    if search:
        hist = [h for h in hist if search.lower() in h["query"].lower()]

    for i, chat in enumerate(reversed(hist)):
        st.markdown(f"**{chat['timestamp']}** — {chat['query']}")
        if st.button(f"View #{len(hist)-i}", key=f"view_{i}"):
            with st.spinner("⚙️ Re-executing saved analysis..."):
                output, fig = run_generated_code(datasets, chat["generated_code"])
            figs = []
            if fig:
                figs.append(fig)
            else:
                fig_nums = plt.get_fignums()
                for n in fig_nums:
                    figs.append(plt.figure(n))
                plt.close("all")
            st.session_state.last_result = {
                "code": chat["generated_code"],
                "output": output,
                "figs": figs
            }
            st.rerun()

# ⬆️ Scroll to top button
st.markdown("""
    <button class="scroll-btn" onclick="scrollToTop()">↑</button>
""", unsafe_allow_html=True)
print("✅ Step 4: App fully initialized!")