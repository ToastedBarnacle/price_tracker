import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# Set page title
st.set_page_config(page_title="PSA 10 Card Dashboard", layout="wide")

# Load the data
DATA_FILE = "filtered_price_data.csv"
df = pd.read_csv(DATA_FILE)

# Add "page" selection
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Market Cap Dashboard", "PSA 10 Card Trends"])

# Common calculations
df['grading-profitability'] = pd.to_numeric(df['psa-10-price'], errors='coerce') - pd.to_numeric(df['loose-price'], errors='coerce')
df['grading-profitability'] = df['grading-profitability'].fillna(0)
df['market-cap'] = pd.to_numeric(df['loose-price'], errors='coerce') * pd.to_numeric(df['sales-volume'], errors='coerce')
df['market-cap'] = df['market-cap'].fillna(0)
df['release-year'] = pd.to_datetime(df['release-date'], errors='coerce').dt.year.fillna(0).astype(int)
df['product-url'] = df['id'].apply(lambda x: f"https://www.pricecharting.com/offers?product={x}")

# Filters for both pages
st.sidebar.header("Filters")
min_psa_price = st.sidebar.number_input("Minimum PSA 10 Price ($)", min_value=0.0, value=0.0, step=1.0)
max_psa_price = st.sidebar.number_input("Maximum PSA 10 Price ($)", min_value=0.0, value=df['psa-10-price'].max(), step=1.0)
min_loose_price = st.sidebar.number_input("Minimum Loose Price ($)", min_value=0.0, value=0.0, step=1.0)
max_loose_price = st.sidebar.number_input("Maximum Loose Price ($)", min_value=0.0, value=df['loose-price'].max(), step=1.0)
min_sales = st.sidebar.number_input("Minimum Sales Volume", min_value=0, value=0, step=1)
years = list(range(1999, 2026))
selected_years = st.sidebar.multiselect("Select Release Years", options=years, default=years)

# Filter data
filtered_df = df[
    (df['psa-10-price'] >= min_psa_price) &
    (df['psa-10-price'] <= max_psa_price) &
    (df['loose-price'] >= min_loose_price) &
    (df['loose-price'] <= max_loose_price) &
    (df['sales-volume'] >= min_sales) &
    (df['release-year'].isin(selected_years))
]

# Render Market Cap Dashboard
if page == "Market Cap Dashboard":
    st.title("PSA 10 Card Market Cap Dashboard")
    st.metric("Total Cards", len(filtered_df))
    
    # Market Cap Table
    st.subheader("Top 20 Cards by Market Cap")
    top_market_cap = filtered_df.sort_values(by="market-cap", ascending=False).head(20)
    top_market_cap['Ranking'] = top_market_cap.index + 1
    st.dataframe(
        top_market_cap[[
            'Ranking', 'product-name', 'console-name', 'loose-price', 'psa-10-price', 'sales-volume', 'market-cap'
        ]]
    )

# Render PSA 10 Card Trends Page
elif page == "PSA 10 Card Trends":
    st.title("PSA 10 Card Trends")
    st.sidebar.markdown("### Time Range")
    time_range = st.sidebar.selectbox("Select Time Range", ["Weekly", "Monthly", "3 Months", "6 Months"])
    
    # Define time deltas
    time_deltas = {
        "Weekly": timedelta(weeks=1),
        "Monthly": timedelta(days=30),
        "3 Months": timedelta(days=90),
        "6 Months": timedelta(days=180),
    }
    delta = time_deltas[time_range]
    
    # Simulated time series data (Replace this with real data loading logic)
    today = datetime.now()
    filtered_df['date'] = today - pd.to_timedelta(filtered_df.index, unit='d')
    filtered_df['psa-10-price-change'] = filtered_df['psa-10-price'] * (1 + (filtered_df.index % 10) / 100)
    filtered_df['sales-volume-change'] = filtered_df['sales-volume'] * (1 + (filtered_df.index % 5) / 100)
    filtered_df['loose-price-change'] = filtered_df['loose-price'] * (1 + (filtered_df.index % 8) / 100)

    # Weekly Change Tables
    st.subheader(f"Top 10 Cards by PSA 10 Price Change ({time_range})")
    top_psa_change = filtered_df.sort_values(by='psa-10-price-change', ascending=False).head(10)
    st.dataframe(
        top_psa_change[[
            'product-name', 'console-name', 'psa-10-price', 'psa-10-price-change'
        ]]
    )
    
    st.subheader(f"Top 10 Cards by Sales Volume Change ({time_range})")
    top_sales_change = filtered_df.sort_values(by='sales-volume-change', ascending=False).head(10)
    st.dataframe(
        top_sales_change[[
            'product-name', 'console-name', 'sales-volume', 'sales-volume-change'
        ]]
    )
    
    st.subheader(f"Top 10 Cards by Loose Price Change ({time_range})")
    top_loose_change = filtered_df.sort_values(by='loose-price-change', ascending=False).head(10)
    st.dataframe(
        top_loose_change[[
            'product-name', 'console-name', 'loose-price', 'loose-price-change'
        ]]
    )
