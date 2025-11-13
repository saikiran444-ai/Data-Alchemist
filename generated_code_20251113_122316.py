import pandas as pd
import matplotlib.pyplot as plt

# Load datasets (assuming 'datasets' is already populated as per the problem description)
# For demonstration, I'll create dummy dataframes if 'datasets' is not pre-filled in this environment.
# In a real scenario, these lines would not be needed as 'datasets' is preloaded.
try:
    datasets
except NameError:
    datasets = {
        "olist_order_payments_dataset": pd.DataFrame({
            'order_id': ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j'],
            'payment_type': ['credit_card', 'boleto', 'credit_card', 'debit_card', 'credit_card', 'boleto', 'voucher', 'credit_card', 'boleto', 'voucher'],
            'payment_value': [100.50, 50.25, 120.00, 75.00, 90.00, 60.00, 25.00, 110.00, 55.00, 30.00]
        })
    }

payments_df = datasets["olist_order_payments_dataset"]

# Calculate the average payment value by payment type
avg_payment_by_type = payments_df.groupby('payment_type')['payment_value'].mean().sort_values(ascending=False)

# Prepare data for the table
table_data = [(index, value) for index, value in avg_payment_by_type.items()]

# Plotting the results
plt.figure(figsize=(10, 6))
avg_payment_by_type.plot(kind='bar', color='skyblue')
plt.title('Average Payment Value by Payment Type')
plt.xlabel('Payment Type')
plt.ylabel('Average Payment Value')
plt.xticks(rotation=45, ha='right')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

# Generate summary
highest_type = avg_payment_by_type.index[0]
highest_value = avg_payment_by_type.iloc[0]
lowest_type = avg_payment_by_type.index[-1]
lowest_value = avg_payment_by_type.iloc[-1]

summary = f"The average payment value varies by type, with '{highest_type}' having the highest average of ${highest_value:.2f} and '{lowest_type}' having the lowest average of ${lowest_value:.2f}."

RESULT = {
    "summary": summary,
    "table": table_data,
    "plot": True
}

print(f"✅ Summary: {RESULT['summary']}")