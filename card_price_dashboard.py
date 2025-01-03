import streamlit as st
import pandas as pd
import plotly.express as px

# Load the data
DATA_FILE = "filtered_price_data.csv"  # Your filtered CSV file
df = pd.read_csv(DATA_FILE)

# Convert prices to dollars for better readability
df['psa-10-price'] = df['psa-10-price'] / 100
df['loose-price'] = df['loose-price'] / 100
df['grading-profitability'] = df['psa-10-price'] - df['loose-price']

# Sidebar Filters
st.sidebar.header("Filters")

# Minimum and maximum PSA 10 price filter
min_psa_price = st.sidebar.slider(
    "Minimum PSA 10 Price ($)",
    min_value=float(df['psa-10-price'].min()),
    max_value=float(df['psa-10-price'].max()),
    value=float(df['psa-10-price'].min()),
    format="$%.2f"
)

max_psa_price = st.sidebar.slider(
    "Maximum PSA 10 Price ($)",
    min_value=float(df['psa-10-price'].min()),
    max_value=float(df['psa-10-price'].max()),
    value=float(df['psa-10-price'].max()),
    format="$%.2f"
)

# Minimum and maximum loose price filter
min_loose_price = st.sidebar.slider(
    "Minimum Loose Price ($)",
    min_value=float(df['loose-price'].min()),
    max_value=float(df['loose-price'].max()),
    value=float(df['loose-price'].min()),
    format="$%.2f"
)

max_loose_price = st.sidebar.slider(
    "Maximum Loose Price ($)",
    min_value=float(df['loose-price'].min()),
    max_value=float(df['loose-price'].max()),
    value=float(df['loose-price'].max()),
    format="$%.2f"
)

# Minimum grading profitability filter
min_grading_profitability = st.sidebar.slider(
    "Minimum Grading Profitability ($)",
    min_value=float(df['grading-profitability'].min()),
    max_value=float(df['grading-profitability'].max()),
    value=float(df['grading-profitability'].min()),
    format="$%.2f"
)

# Minimum sales volume filter
min_sales = st.sidebar.slider(
    "Minimum Sales Volume",
    min_value=0,
    max_value=int(df['sales-volume'].max()),
    value=0
)

# Apply filters
filtered_df = df[
    (df['psa-10
