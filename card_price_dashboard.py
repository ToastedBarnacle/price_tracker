import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Set page title and layout
st.set_page_config(page_title="CardMarketCap.App", layout="wide")

# Load the newest and previous data files
DATA_FOLDER = "Data"  # Correctly capitalized folder name

# Ensure the data folder exists
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)
    st.error(f"Data folder '{DATA_FOLDER}' does not exist. Please upload CSV files to this folder.")
    st.stop()

# List all data files
data_files = [f for f in os.listdir(DATA_FOLDER) if f.startswith("filtered_price_data_") and f.endswith(".csv")]
data_files.sort(reverse=True)  # Sort files by name (newest date first)

# Check for available files
if len(data_files) < 2:
    st.error(f"At least two data files are required in the '{DATA_FOLDER}' folder for trends analysis.")
    st.stop()

# Load the newest and previous data files
NEWEST_DATA_FILE = os.path.join(DATA_FOLDER, data_files[0])
PREVIOUS_DATA_FILE = os.path.join(DATA_FOLDER, data_files[1])

newest_df = pd.read_csv(NEWEST_DATA_FILE)
previous_df = pd.read_csv(PREVIOUS_DATA_FILE)

st.sidebar.info(f"Newest data file: {data_files[0]}")
st.sidebar.info(f"Previous data file: {data_files[1]}")

# Ensure all necessary columns exist and compute missing ones dynamically
def prepare_data(df):
    df['grading-profitability'] = pd.to_numeric(df['psa-10-price'], errors='coerce') - pd.to_numeric(df['loose-price'], errors='coerce')
    df['grading-profitability'] = df['grading-profitability'].fillna(0)
    df['market-cap'] = pd.to_numeric(df['loose-price'], errors='coerce') * pd.to_numeric(df['sales-volume'], errors='coerce')
    df['market-cap'] = df['market-cap'].fillna(0)
    df['release-year'] = pd.to_datetime(df['release-date'], errors='coerce').dt.year.fillna(0).astype(int)
    df['product-url'] = df['id'].apply(lambda x: f"https://www.pricecharting.com/offers?product={x}")
    return df

newest_df = prepare_data(newest_df)
previous_df = prepare_data(previous_df)

# Calculate trends
def calculate_trends(newest, previous):
    trend_data = newest[['id', 'product-name', 'loose-price', 'psa-10-price', 'sales-volume']].merge(
        previous[['id', 'loose-price', 'psa-10-price', 'sales-volume']],
        on='id',
        suffixes=('_new', '_old')
    )
    trend_data['loose-price-change'] = ((trend_data['loose-price_new'] - trend_data['loose-price_old']) / trend_data['loose-price_old']) * 100
    trend_data['psa-10-price-change'] = ((trend_data['psa-10-price_new'] - trend_data['psa-10-price_old']) / trend_data['psa-10-price_old']) * 100
    trend_data['sales-volume-change'] = ((trend_data['sales-volume_new'] - trend_data['sales-volume_old']) / trend_data['sales-volume_old']) * 100
    return trend_data

trend_data = calculate_trends(newest_df, previous_df)

# Format trends data
def format_percentage(value):
    return f"{value:.2f}%" if pd.notnull(value) else "N/A"

trend_data['loose-price-change'] = trend_data['loose-price-change'].apply(format_percentage)
trend_data['psa-10-price-change'] = trend_data['psa-10-price-change'].apply(format_percentage)
trend_data['sales-volume-change'] = trend_data['sales-volume-change'].apply(format_percentage)

# Function to display trends
def display_trends():
    st.subheader("Top 10 Cards by Loose Price Change")
    loose_price_trend = trend_data.sort_values(by='loose-price-change', ascending=False).head(10)
    st.table(loose_price_trend[['product-name', 'loose-price-change']])

    st.subheader("Top 10 Cards by PSA 10 Price Change")
    psa_price_trend = trend_data.sort_values(by='psa-10-price-change', ascending=False).head(10)
    st.table(psa_price_trend[['product-name', 'psa-10-price-change']])

    st.subheader("Top 10 Cards by Sales Volume Change")
    sales_volume_trend = trend_data.sort_values(by='sales-volume-change', ascending=False).head(10)
    st.table(sales_volume_trend[['product-name', 'sales-volume-change']])

# Navigation
st.markdown("<h1 style='text-align: center;'>CardMarketCap.App</h1>", unsafe_allow_html=True)
selected_page = st.radio("Navigation", ["PSA Card Market Cap", "PSA Card Trends"], horizontal=True)

if selected_page == "PSA Card Market Cap":
    st.header("PSA 10 Card Market Cap Dashboard")
    st.metric("Total Cards", len(newest_df))

    # Top Cards by Market Cap
    st.subheader("Top 20 Cards by Market Cap")
    top_market_cap = (
        newest_df.sort_values(by="market-cap", ascending=False)
        .head(20)
        .reset_index(drop=True)
    )
    top_market_cap['Ranking'] = top_market_cap.index + 1
    st.table(top_market_cap[['Ranking', 'product-name', 'loose-price', 'psa-10-price', 'sales-volume', 'market-cap']])

elif selected_page == "PSA Card Trends":
    st.header("PSA Card Trends")
    display_trends()
