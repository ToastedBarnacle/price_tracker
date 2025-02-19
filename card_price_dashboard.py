import streamlit as st
import pandas as pd
import plotly.express as px
import os
import psa_trends  # Ensure PSA Trends script is imported

# Set page title and layout
st.set_page_config(page_title="CardMarketCap.App", layout="wide")

# Load the newest data file
DATA_FOLDER = "Data"

if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)
    st.error(f"Data folder '{DATA_FOLDER}' does not exist. Please upload CSV files to this folder.")
    st.stop()

data_files = [f for f in os.listdir(DATA_FOLDER) if f.startswith("filtered_price_data_") and f.endswith(".csv")]
data_files.sort(reverse=True)

if not data_files:
    st.error(f"No data files found in the '{DATA_FOLDER}' folder. Please upload at least one file.")
    st.stop()

DATA_FILE = os.path.join(DATA_FOLDER, data_files[0])
df = pd.read_csv(DATA_FILE)
st.sidebar.info(f"Loaded data file: {data_files[0]}")

# Sidebar Filters
st.sidebar.header("Filters")
min_psa_price = st.sidebar.number_input("Minimum PSA 10 Price ($)", min_value=0.0, value=0.0, step=1.0)
max_psa_price = st.sidebar.number_input("Maximum PSA 10 Price ($)", min_value=0.0, value=df['psa-10-price'].max(), step=1.0)
min_loose_price = st.sidebar.number_input("Minimum Loose Price ($)", min_value=0.0, value=0.0, step=1.0)
max_loose_price = st.sidebar.number_input("Maximum Loose Price ($)", min_value=0.0, value=df['loose-price'].max(), step=1.0)
min_sales = st.sidebar.number_input("Minimum Sales Volume", min_value=0, value=0, step=1)
years = list(range(1999, 2026))
selected_years = st.sidebar.multiselect("Select Release Years", options=years, default=years)

# New: Filter for console-name (Set)
console_names = df['console-name'].dropna().unique().tolist()
selected_sets = st.sidebar.multiselect("Select Set", options=console_names, default=[])

# New: Search bar for card names
search_query = st.sidebar.text_input("Search for a card")

# New: Language filter (English, Japanese, All)
language_filter = st.sidebar.radio("Select Language", ["All", "English", "Japanese"])

# Send Filters to PSA Trends Page
filters = {
    "min_psa_price": min_psa_price,
    "max_psa_price": max_psa_price,
    "min_loose_price": min_loose_price,
    "max_loose_price": max_loose_price,
    "min_sales": min_sales,
    "selected_years": selected_years,
    "selected_sets": selected_sets
}

# Navigation
st.markdown("<h1 style='text-align: center;'>CardMarketCap.App</h1>", unsafe_allow_html=True)
selected_page = st.radio("Navigation", ["PSA Card Market Cap", "PSA Card Trends"], horizontal=True)

if selected_page == "PSA Card Market Cap":
    st.header("PSA 10 Card Market Cap Dashboard")
    st.metric("Total Cards", len(df))  # Show total cards available
elif selected_page == "PSA Card Trends":
    st.header("PSA Card Trends Analysis")
    
    # ✅ DEBUG: Print Filters to Ensure They're Being Passed
    st.write("### ✅ Filters Being Sent to PSA Trends:")
    st.json(filters)  # Display filters in JSON format for debugging
    
    # ✅ Call PSA Trends Function
    psa_trends.render_trends_page(filters)
