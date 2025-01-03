import streamlit as st
import pandas as pd
import plotly.express as px

# Load the data
DATA_FILE = "filtered_price_data.csv"  # Your filtered CSV file
df = pd.read_csv(DATA_FILE)

# Replace missing or invalid data with "N/A"
df = df.fillna("N/A")

# Convert numeric columns to "N/A" if invalid (non-numeric values)
numeric_columns = ['psa-10-price', 'loose-price', 'grading-profitability', 'sales-volume', 'market-cap']
for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna("N/A")

# Calculate grading profitability and market capitalization for valid rows
df['grading-profitability'] = pd.to_numeric(df['psa-10-price'], errors='coerce') - pd.to_numeric(df['loose-price'], errors='coerce')
df['grading-profitability'] = df['grading-profitability'].fillna("N/A")
df['market-cap'] = pd.to_numeric(df['loose-price'], errors='coerce') * pd.to_numeric(df['sales-volume'], errors='coerce')
df['market-cap'] = df['market-cap'].fillna("N/A")

# Sidebar Filters
st.sidebar.header("Filters")

# Minimum and maximum PSA 10 price filter
st.sidebar.markdown("### PSA 10 Price ($)")
min_psa_price = st.sidebar.number_input(
    "Minimum PSA 10 Price ($)", 
    min_value=0.0, 
    max_value=float(df[df['psa-10-price'] != "N/A"]['psa-10-price'].max() if "N/A" not in df['psa-10-price'].unique() else 0), 
    value=float(df[df['psa-10-price'] != "N/A"]['psa-10-price'].min() if "N/A" not in df['psa-10-price'].unique() else 0), 
    step=1.0
)
max_psa_price = st.sidebar.number_input(
    "Maximum PSA 10 Price ($)", 
    min_value=0.0, 
    max_value=float(df[df['psa-10-price'] != "N/A"]['psa-10-price'].max() if "N/A" not in df['psa-10-price'].unique() else 0), 
    value=float(df[df['psa-10-price'] != "N/A"]['psa-10-price'].max() if "N/A" not in df['psa-10-price'].unique() else 0), 
    step=1.0
)

# Minimum and maximum loose price filter
st.sidebar.markdown("### Loose Price ($)")
min_loose_price = st.sidebar.number_input(
    "Minimum Loose Price ($)", 
    min_value=0.0, 
    max_value=float(df[df['loose-price'] != "N/A"]['loose-price'].max() if "N/A" not in df['loose-price'].unique() else 0), 
    value=float(df[df['loose-price'] != "N/A"]['loose-price'].min() if "N/A" not in df['loose-price'].unique() else 0), 
    step=1.0
)
max_loose_price = st.sidebar.number_input(
    "Maximum Loose Price ($)", 
    min_value=0.0, 
    max_value=float(df[df['loose-price'] != "N/A"]['loose-price'].max() if "N/A" not in df['loose-price'].unique() else 0), 
    value=float(df[df['loose-price'] != "N/A"]['loose-price'].max() if "N/A" not in df['loose-price'].unique() else 0), 
    step=1.0
)

# Minimum grading profitability filter
st.sidebar.markdown("### Grading Profitability ($)")
min_grading_profitability = st.sidebar.number_input(
    "Minimum Grading Profitability ($)", 
    min_value=0.0, 
    max_value=float(df[df['grading-profitability'] != "N/A"]['grading-profitability'].max() if "N/A" not in df['grading-profitability'].unique() else 0), 
    value=float(df[df['grading-profitability'] != "N/A"]['grading-profitability'].min() if "N/A" not in df['grading-profitability'].unique() else 0), 
    step=1.0
)

# Minimum sales volume filter
st.sidebar.markdown("### Sales Volume")
min_sales = st.sidebar.number_input(
    "Minimum Sales Volume",
    min_value=0,
    max_value=int(df[df['sales-volume'] != "N/A"]['sales-volume'].max() if "N/A" not in df['sales-volume'].unique() else 0),
    value=0,
    step=1
)

# Apply filters
filtered_df = df[
    (df['psa-10-price'] != "N/A") & (df['loose-price'] != "N/A") &
    (df['grading-profitability'] != "N/A") & (df['sales-volume'] != "N/A") &
    (pd.to_numeric(df['psa-10-price']) >= min_psa_price) &
    (pd.to_numeric(df['psa-10-price']) <= max_psa_price) &
    (pd.to_numeric(df['loose-price']) >= min_loose_price) &
    (pd.to_numeric(df['loose-price']) <= max_loose_price) &
    (pd.to_numeric(df['grading-profitability']) >= min_grading_profitability) &
    (pd.to_numeric(df['sales-volume']) >= min_sales)
]

# Main Dashboard
st.title("Card Price Tracker Dashboard")

# Total Cards Metric
st.header("Total Cards Included in Filter Selections")
st.metric("Total Cards", len(filtered_df))

# Display Filtered Table
st.header("Filtered Card Data")
st.dataframe(filtered_df[['product-name', 'psa-10-price', 'loose-price', 'grading-profitability', 'sales-volume', 'market-cap']])
