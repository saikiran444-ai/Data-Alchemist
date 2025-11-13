import pandas as pd
import matplotlib.pyplot as plt

# Load the dataset
payments_df = datasets["olist_order_payments_dataset"]

# Calculate the average payment value by payment type
average_payment_by_type = payments_df.groupby('payment_type')['payment_value'].mean().sort_values(ascending=False)

# Prepare data for the RESULT dictionary
table_data = [(payment_type, value) for payment_type, value in average_payment_by_type.items()]

# Create the plot
plt.figure(figsize=(10, 6))
average_payment_by_type.plot(kind='barh', color='skyblue')
plt.title('Average Payment Value by Payment Type')
plt.xlabel('Average Payment Value')
plt.ylabel('Payment Type')
plt.grid(axis='x', linestyle='--', alpha=0.6)
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()

# Generate summary
highest_type = average_payment_by_type.index[0]
highest_value = average_payment_by_type.iloc[0]
lowest_type = average_payment_by_type.index[-1]
lowest_value = average_payment_by_type.iloc[-1]

summary = f"The average payment value varies significantly by type, with '{highest_type}' having the highest average of ${highest_value:.2f} and '{lowest_type}' having the lowest average of ${lowest_value:.2f}."

RESULT = {
    "summary": summary,
    "table": table_data,
    "plot": True
}

print(f"✅ Summary: {RESULT['summary']}")