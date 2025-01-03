import os
import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from bs4 import BeautifulSoup

# Set page title
st.set_page_config(page_title="PSA 10 Card Market Cap Dashboard")

# Load the data
DATA_FILE = "filtered_price_data.csv"  # Your filtered CSV file
df = pd.read_csv(DATA_FILE)

# Ensure all necessary columns exist and compute missing ones dynamically
df['grading-profitability'] = pd.to_numeric(df['psa-10-price'], errors='coerce') - pd.to_numeric(df['loose-price'], errors='coerce')
df['grading-profitability'] = df['grading-profitability'].fillna(0)

df['market-cap'] = pd.to_numeric(df['loose-price'], errors='coerce') * pd.to_numeric(df['sales-volume'], errors='coerce')
df['market-cap'] = df['market-cap'].fillna(0)

# Extract release year from release-date
df['release-year'] = pd.to_datetime(df['release-date'], errors='coerce').dt.year.fillna(0).astype(int)

# Function to fetch image URLs (cached)
@st.cache_data
def fetch_image_url(product_id):
    try:
        url = f"https://www.pricecharting.com/offers?product={product_id}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            img_tag = soup.find("img", {"class": "product-image"})
            if img_tag and "src" in img_tag.attrs:
                return img_tag["src"]
    except Exception as e:
        st.error(f"Error fetching image for product {product_id}: {e}")
    return None

# Add a column for image URLs
df["image-url"] = df["id"].apply(fetch_image_url)

# Sidebar Filters
st.sidebar.header("Filters")

# Minimum and maximum PSA 10 price filter
st.sidebar.markdown("### PSA 10 Price ($)")
min_psa_price = st.sidebar.number_input(
    "Minimum PSA 10 Price ($)", 
    min_value=0.0, 
    max_value=float(df['psa-10-price'].max()), 
    value=float(df['psa-10-price'].min()), 
    step=1.0
)
max_psa_price = st.sidebar.number_input(
    "Maximum PSA 10 Price ($)", 
    min_value=0.0, 
    max_value=float(df['psa-10-price'].max()), 
    value=float(df['psa-10-price'].max()), 
    step=1.0
)

# Minimum and maximum loose price filter
st.sidebar.markdown("### Loose Price ($)")
min_loose_price = st.sidebar.number_input(
    "Minimum Loose Price ($)", 
    min_value=0.0, 
    max_value=float(df['loose-price'].max()), 
    value=float(df['loose-price'].min()), 
    step=1.0
)
max_loose_price = st.sidebar.number_input(
    "Maximum Loose Price ($)", 
    min_value=0.0, 
    max_value=float(df['loose-price'].max()), 
    value=float(df['loose-price'].max()), 
    step=1.0
)

# Apply filters
filtered_df = df[
    (df['psa-10-price'] >= min_psa_price) &
    (df['psa-10-price'] <= max_psa_price) &
    (df['loose-price'] >= min_loose_price) &
    (df['loose-price'] <= max_loose_price)
]

# Add ranks for the tables
filtered_df['Ranking'] = filtered_df['market-cap'].rank(ascending=False, method="dense")
filtered_df['Rank Grading'] = filtered_df['grading-profitability'].rank(ascending=False, method="dense")

# Main Dashboard
st.title("PSA 10 Card Market Cap Dashboard")

# Total Cards Metric
st.metric("Total Cards", len(filtered_df))

# Display Top Cards by Market Cap with Images
st.header("Top Cards by Market Cap")
top_market_cap = (
    filtered_df.sort_values(by="market-cap", ascending=False)
    .head(20)
    .reset_index(drop=True)
)
top_market_cap['Ranking'] = top_market_cap.index + 1

# Add images to the dataframe
top_market_cap["Image"] = top_market_cap["image-url"].apply(
    lambda url: f'<img src="{url}" style="width:50px; height:auto;">' if url else "No Image"
)

# Display HTML table
st.write(
    top_market_cap.to_html(
        escape=False,
        index=False,
        columns=["Ranking", "product-name", "psa-10-price", "loose-price", "market-cap", "Image"],
    ),
    unsafe_allow_html=True,
)
