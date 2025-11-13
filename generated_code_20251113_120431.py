import pandas as pd
import matplotlib.pyplot as plt

# Load datasets
orders_df = datasets["olist_orders_dataset"]
order_items_df = datasets["olist_order_items_dataset"]
products_df = datasets["olist_products_dataset"]
category_translation_df = datasets["product_category_name_translation"]

# Merge dataframes to get product category and order dates
df_merged = pd.merge(orders_df, order_items_df, on='order_id', how='inner')
df_merged = pd.merge(df_merged, products_df, on='product_id', how='inner')
df_merged = pd.merge(df_merged, category_translation_df, on='product_category_name', how='inner')

# Convert date columns to datetime objects
df_merged['order_delivered_customer_date'] = pd.to_datetime(df_merged['order_delivered_customer_date'])
df_merged['order_estimated_delivery_date'] = pd.to_datetime(df_merged['order_estimated_delivery_date'])

# Calculate delivery delay in days
# A delay occurs if the actual delivery date is after the estimated delivery date
df_merged['delivery_delay_days'] = (df_merged['order_delivered_customer_date'] - df_merged['order_estimated_delivery_date']).dt.days

# Filter for actual delays (positive delay_days) and drop NaNs in critical columns
df_delays = df_merged[df_merged['delivery_delay_days'] > 0].copy()
df_delays.dropna(subset=['product_category_name_english', 'delivery_delay_days'], inplace=True)

# Group by product category and calculate the average delivery delay
average_delay_by_category = df_delays.groupby('product_category_name_english')['delivery_delay_days'].mean().sort_values(ascending=False)

# Prepare data for table and plot
top_10_delays = average_delay_by_category.head(10)
bottom_10_delays = average_delay_by_category.tail(10)

# Combine top and bottom for visualization if there are enough categories, otherwise just show all
if len(average_delay_by_category) > 20:
    plot_data = pd.concat([top_10_delays, bottom_10_delays])
else:
    plot_data = average_delay_by_category

# Create a list of (label, value) pairs for the table
table_data = [(category, round(delay, 2)) for category, delay in average_delay_by_category.items()]

# Plotting
plt.figure(figsize=(12, 8))
plot_data.sort_values(ascending=True).plot(kind='barh', color='skyblue')
plt.title('Average Delivery Delay by Product Category (Days)', fontsize=16)
plt.xlabel('Average Delay (Days)', fontsize=12)
plt.ylabel('Product Category', fontsize=12)
plt.grid(axis='x', linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()

# Summary
highest_delay_category = average_delay_by_category.index[0]
highest_delay_value = average_delay_by_category.iloc[0]
lowest_delay_category = average_delay_by_category.index[-1]
lowest_delay_value = average_delay_by_category.iloc[-1]

summary_text = f"The average delivery delay varies significantly by product category. '{highest_delay_category}' has the highest average delay of {highest_delay_value:.2f} days, while '{lowest_delay_category}' has the lowest average delay of {lowest_delay_value:.2f} days."

RESULT = {
    "summary": summary_text,
    "table": table_data,
    "plot": True
}

print(f"✅ Summary: {RESULT['summary']}")