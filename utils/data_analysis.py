import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

def analyze_data(query):
    """Analyze the dataset and display graphs or summaries."""
    query = query.lower()
    st.markdown("### 📊 Analysis Result")

    # Top 5 product categories
    if "category" in query and ("top" in query or "most" in query):
        items = pd.read_csv("data/olist_order_items_dataset.csv")
        products = pd.read_csv("data/olist_products_dataset.csv")
        merged = items.merge(products, on="product_id")
        top = merged["product_category_name"].value_counts().head(5)

        fig, ax = plt.subplots()
        top.plot(kind="bar", ax=ax, color="skyblue")
        ax.set_title("Top 5 Product Categories by Orders")
        ax.set_xlabel("Category")
        ax.set_ylabel("Number of Orders")
        st.pyplot(fig)
        return True

    # Monthly revenue trend
    elif "sales" in query or "revenue" in query:
        orders = pd.read_csv("data/olist_orders_dataset.csv")
        payments = pd.read_csv("data/olist_order_payments_dataset.csv")
        merged = orders.merge(payments, on="order_id")
        merged["order_purchase_timestamp"] = pd.to_datetime(
            merged["order_purchase_timestamp"]
        )
        merged["month"] = merged["order_purchase_timestamp"].dt.to_period("M")
        monthly = merged.groupby("month")["payment_value"].sum()

        fig, ax = plt.subplots()
        monthly.plot(kind="line", marker="o", ax=ax, color="green")
        ax.set_title("Monthly Revenue Trend")
        ax.set_xlabel("Month")
        ax.set_ylabel("Revenue")
        st.pyplot(fig)
        return True

    # Payment type breakdown
    elif "payment" in query or "method" in query:
        payments = pd.read_csv("data/olist_order_payments_dataset.csv")
        payment_types = payments["payment_type"].value_counts()

        fig, ax = plt.subplots()
        payment_types.plot(kind="pie", autopct="%1.1f%%", ax=ax)
        ax.set_ylabel("")
        ax.set_title("Payment Type Distribution")
        st.pyplot(fig)
        return True

    else:
        st.warning("⚠️ Sorry, I couldn’t match that query to a known analysis type.")
        return False