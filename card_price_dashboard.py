import streamlit as st
import pandas as pd
import os

# Set page title
st.set_page_config(page_title="CardMarketCap.App", layout="wide")

DATA_FOLDER = "Data"
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)
    st.error(f"Data folder '{DATA_FOLDER}' does not exist. Please upload CSV files.")
    st.stop()

data_files = [f for f in os.listdir(DATA_FOLDER) if f.startswith("filtered_price_data_") and f.endswith(".csv")]
data_files.sort(reverse=True)

if not data_files:
    st.error(f"No
