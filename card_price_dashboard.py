import os
import pandas as pd
import streamlit as st

# Set the folder path where your data files are stored
DATA_FOLDER = "Data"

# Get the latest data file
data_files = sorted(
    [
        f for f in os.listdir(DATA_FOLDER)
        if f.startswith("filtered_price_data_") and f.endswith(".csv")
    ],
    key=lambda x: pd.to_datetime(x.split('_')[-1].replace('.csv', ''), format='%Y_%m_%d'),
    reverse=True
)

if data_files:
    latest_file = os.path.join(DATA_FOLDER, data_files[0])
    st.write(f"Loaded data file: {data_files[0]}")
    df = pd.read_csv(latest_file)
else:
    st.error("No valid data files found in the Data folder.")
    st.stop()

# Ensure all necessary columns exist and compute missing ones dynamically
df['grading-profitability'] = pd.to_numeric(df['psa-10-price'], errors='coerce') - pd.to_numeric(df['loose-price'], errors='coerce')
df['grading-profitability'] = df['grading-profitability'].fillna(0)
df['market-cap'] = pd.to_numeric(df['loose-price'], errors='coerce') * pd.to_numeric(df['sales-volume'], errors='coerce')
df['market-cap'] = df['market-cap'].fillna(0)
df['release-year'] = pd.to_datetime(df['release-date'], errors='coerce').dt.year.fillna(0).astype(int)
df['product-url'] = df['id'].apply(lambda x: f"https://www.pricecharting.com/offers?product={x}")

# Rest of your Streamlit app logic...
