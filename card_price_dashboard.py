import streamlit as st
import pandas as pd
import plotly.express as px

# Set page title and layout
st.set_page_config(page_title="PSA 10 Card Dashboard", layout="wide")

# Load the data
DATA_FILE = "filtered_price_data.csv"
df = pd.read_csv(DATA_FILE)

# Ensure all necessary columns exist and compute missing ones dynamically
df['grading-profitability'] = pd.to_numeric(df['psa-10-price'], errors='coerce') - pd.to_numeric(df['loose-price'], errors='coerce')
df['grading-profitability'] = df['grading-profitability'].fillna(0)
df['market-cap'] = pd.to_numeric(df['loose-price'], errors='coerce') * pd.to_numeric(df['sales-volume'], errors='coerce')
df['market-cap'] = df['market-cap'].fillna(0)
df['release-year'] = pd.to_datetime(df['release-date'], errors='coerce').dt.year.fillna(0).astype(int)
df['product-url'] = df['id'].apply(lambda x: f"https://www.pricecharting.com/offers?product={x}")

# Format financial columns
def format_currency(value):
    return f"${value:,.2f}" if pd.notnull(value) else "N/A"

def format_sales(value):
    return f"{value:,}" if pd.notnull(value) else "N/A"

df['loose-price'] = df['loose-price'].apply(format_currency)
df['psa-10-price'] = df['psa-10-price'].apply(format_currency)
df['market-cap'] = df['market-cap'].apply(format_currency)
df['sales-volume'] = df['sales-volume'].apply(format_sales)

# Add navigation buttons
st.title("PSA 10 Card Dashboard")
selected_page = st.radio("Navigation", ["PSA Card Market Cap", "PSA Card Trends"])

# PSA Card Market Cap Page
if selected_page == "PSA Card Market Cap":
    st.header("PSA 10 Card Market Cap Dashboard")
    st.metric("Total Cards", len(df))

    # Display Top Cards by Market Cap
    st.subheader("Top 20 Cards by Market Cap")
    top_market_cap = (
        df.sort_values(by="market-cap", ascending=False)
        .head(20)
        .reset_index(drop=True)
    )
    st.dataframe(top_market_cap)

    # Scatterplot Visualization
    st.subheader("Loose Price vs PSA 10 Graded Price")
    scatter_fig = px.scatter(
        df,
        x="loose-price",
        y="psa-10-price",
        hover_name="product-name",
        hover_data=["console-name", "product-url"],
        title="Loose Price vs PSA 10 Graded Price",
        labels={"loose-price": "Loose Price ($)", "psa-10-price": "PSA 10 Price ($)"},
        template="plotly_white",
    )
    scatter_fig.update_traces(marker=dict(size=10, opacity=0.7))
    st.plotly_chart(scatter_fig, use_container_width=True)

# PSA Card Trends Page
elif selected_page == "PSA Card Trends":
    st.header("PSA Card Trends")
    st.write("This page is under construction.")
