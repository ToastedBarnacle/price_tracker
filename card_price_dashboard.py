import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load the data
DATA_FILE = "filtered_price_data.csv"  # Your filtered CSV file
df = pd.read_csv(DATA_FILE)

# Convert prices to dollars for better readability
df['psa-10-price'] = df['psa-10-price'] / 100
df['loose-price'] = df['loose-price'] / 100

# Sidebar Filters
st.sidebar.header("Filters")
min_price = st.sidebar.slider("Minimum PSA 10 Price ($)", 0, int(df['psa-10-price'].max()), 0)
max_price = st.sidebar.slider("Maximum PSA 10 Price ($)", min_price, int(df['psa-10-price'].max()), int(df['psa-10-price'].max()))
min_sales = st.sidebar.slider("Minimum Sales Volume", 0, int(df['sales-volume'].max()), 0)

# Apply filters
filtered_df = df[
    (df['psa-10-price'] >= min_price) &
    (df['psa-10-price'] <= max_price) &
    (df['sales-volume'] >= min_sales)
]

# Main Dashboard
st.title("Card Price Tracker Dashboard")

# Display Metrics
st.header("Summary Metrics")
st.metric("Total Cards", len(filtered_df))
st.metric("Average PSA 10 Price ($)", f"{filtered_df['psa-10-price'].mean():.2f}")
st.metric("Total Sales Volume", int(filtered_df['sales-volume'].sum()))

# Charts
st.header("Price Distribution")
fig, ax = plt.subplots()
filtered_df['psa-10-price'].plot(kind='hist', bins=20, ax=ax, alpha=0.7, label='PSA 10 Price')
filtered_df['loose-price'].plot(kind='hist', bins=20, ax=ax, alpha=0.7, label='Loose Price')
ax.set_title("Price Distribution")
ax.set_xlabel("Price ($)")
ax.set_ylabel("Frequency")
ax.legend()
st.pyplot(fig)

# Display Filtered Table
st.header("Filtered Card Data")
st.dataframe(filtered_df)
