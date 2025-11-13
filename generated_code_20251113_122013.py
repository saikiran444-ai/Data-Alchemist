import pandas as pd
import matplotlib.pyplot as plt

# Load datasets (assuming 'datasets' is already populated as per the problem description)
# For demonstration, let's create dummy dataframes if datasets is not pre-populated in this environment
# In a real scenario, these would be pre-loaded.
try:
    olist_order_payments_dataset = datasets["olist_order_payments_dataset"]
except NameError:
    # This block is for testing purposes if 'datasets' is not defined.
    # In the actual environment, 'datasets' will be pre-populated.
    data_payments = {
        'order_id': ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j'],
        'payment_type': ['credit_card', 'boleto', 'credit_card', 'debit_card', 'credit_card', 'boleto', 'voucher', 'credit_card', 'debit_card', 'voucher'],
        'payment_value': [100.50, 50.25, 120.00, 75.10, 90.00, 60.00, 25.00, 110.00, 80.00, 30.00]
    }
    olist_order_payments_dataset = pd.DataFrame(data_payments)


# Calculate the average payment value by payment type
avg_payment_by_type = olist_order_payments_dataset.groupby('payment_type')['payment_value'].mean().sort_values(ascending=False)

# Prepare data for RESULT['table']
table_data = [(payment_type, value) for payment_type, value in avg_payment_by_type.items()]

# Plotting
plt.figure(figsize=(10, 6))
avg_payment_by_type.plot(kind='bar', color='skyblue')
plt.title('Average Payment Value by Payment Type')
plt.xlabel('Payment Type')
plt.ylabel('Average Payment Value (R$)')
plt.xticks(rotation=45, ha='right')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

# Summary
highest_payment_type = avg_payment_by_type.index[0]
highest_payment_value = avg_payment_by_type.iloc[0]
lowest_payment_type = avg_payment_by_type.index[-1]
lowest_payment_value = avg_payment_by_type.iloc[-1]

summary_text = f"The average payment value varies by type, with '{highest_payment_type}' having the highest average of R${highest_payment_value:.2f} and '{lowest_payment_type}' having the lowest average of R${lowest_payment_value:.2f}."

RESULT = {
    "summary": summary_text,
    "table": table_data,
    "plot": True
}

print(f"✅ Summary: {RESULT['summary']}")