import streamlit as st
import pandas as pd
import plotly.express as px
import os
from importlib import import_module

# Set page title and layout
st.set_page_config(page_title="CardMarketCap.App", layout="wide")

# Load the newest data file
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
if not data_files:
    st.error(f"No data files found in the '{DATA_FOLDER}' folder. Please upload at least one file.")
    st.stop()

# Load the newest data file
DATA_FILE = os.path.join(DATA_FOLDER, data_files[0])
df = pd.read_csv(DATA_FILE)
st.sidebar.info(f"Loaded data file: {data_files[0]}")

# Ensure all necessary columns exist and compute missing ones dynamically
df['grading-profitability'] = pd.to_numeric(df['psa-10-price'], errors='coerce') - pd.to_numeric(df['loose-price'], errors='coerce')
df['grading-profitability'] = df['grading-profitability'].fillna(0)
df['market-cap'] = pd.to_numeric(df['loose-price'], errors='coerce') * pd.to_numeric(df['sales-volume'], errors='coerce')
df['market-cap'] = df['market-cap'].fillna(0)
df['release-year'] = pd.to_datetime(df['release-date'], errors='coerce').dt.year.fillna(0).astype(int)
df['product-url'] = df['id'].apply(lambda x: f"https://www.pricecharting.com/offers?product={x}")

# Sidebar Filters
st.sidebar.header("Filters")
min_psa_price = st.sidebar.number_input("Minimum PSA 10 Price ($)", min_value=0.0, value=0.0, step=1.0)
max_psa_price = st.sidebar.number_input("Maximum PSA 10 Price ($)", min_value=0.0, value=df['psa-10-price'].max(), step=1.0)
min_loose_price = st.sidebar.number_input("Minimum Loose Price ($)", min_value=0.0, value=0.0, step=1.0)
max_loose_price = st.sidebar.number_input("Maximum Loose Price ($)", min_value=0.0, value=df['loose-price'].max(), step=1.0)
min_sales = st.sidebar.number_input("Minimum Sales Volume", min_value=0, value=0, step=1)
years = list(range(1999, 2026))
selected_years = st.sidebar.multiselect("Select Release Years", options=years, default=years)

# New: Filter for console-name (Set) with no default selection
console_names = df['console-name'].dropna().unique().tolist()
selected_sets = st.sidebar.multiselect("Select Set", options=console_names, default=[])

# Apply filters
filtered_df = df[
    (df['psa-10-price'] >= min_psa_price) &
    (df['psa-10-price'] <= max_psa_price) &
    (df['loose-price'] >= min_loose_price) &
    (df['loose-price'] <= max_loose_price) &
    (df['sales-volume'] >= min_sales) &
    (df['release-year'].isin(selected_years)) &
    (df['console-name'].isin(selected_sets) if selected_sets else True)  # Allow all if no sets are selected
]

# Format columns for display
def format_currency(value):
    """Format value as currency with $ and commas."""
    return f"${value:,.2f}" if pd.notnull(value) else "N/A"

def format_sales(value):
    """Format value with commas for large numbers."""
    return f"{value:,}" if pd.notnull(value) else "N/A"

def format_percentage(value):
    """Format value as a percentage with 2 decimal places."""
    return f"{value:.2%}" if pd.notnull(value) else "N/A"

# Recalculate grading profitability as a numeric percentage
filtered_df['grading-profitability-percent'] = (
    filtered_df['grading-profitability'] / (pd.to_numeric(filtered_df['loose-price'], errors='coerce') + 15)
)

# Format columns for display
filtered_df['grading-profitability'] = filtered_df['grading-profitability-percent'].apply(format_percentage)
filtered_df['formatted-loose-price'] = filtered_df['loose-price'].apply(lambda x: format_currency(pd.to_numeric(x, errors='coerce')))
filtered_df['formatted-psa-10-price'] = filtered_df['psa-10-price'].apply(lambda x: format_currency(pd.to_numeric(x, errors='coerce')))
filtered_df['formatted-market-cap'] = filtered_df['market-cap'].apply(lambda x: format_currency(pd.to_numeric(x, errors='coerce')))
filtered_df['sales-volume'] = filtered_df['sales-volume'].apply(format_sales)

# Function to generate an HTML table with clickable links
def render_table_with_links(df, columns, url_column):
    table_html = df[columns + [url_column]].copy()
    table_html[url_column] = table_html[url_column].apply(
        lambda x: f'<a href="{x}" target="_blank">View on PriceCharting</a>'
    )
    table_html = table_html.rename(columns={
        "Ranking": "Ranking",
        "product-name": "Card",
        "console-name": "Set",
        "formatted-loose-price": "Raw Price",
        "formatted-psa-10-price": "PSA 10 Price",
        "sales-volume": "Sales/Year",
        "formatted-market-cap": "Market Cap",
        "grading-profitability": "Grading Profitability",
        "product-url": "PriceCharting Link"
    })
    table_html = table_html.to_html(escape=False, index=False)
    return table_html

# Main Dashboard
st.markdown("<h1 style='text-align: center;'>CardMarketCap.App</h1>", unsafe_allow_html=True)
selected_page = st.radio("Navigation", ["PSA Card Market Cap", "PSA Card Trends"], horizontal=True)

if selected_page == "PSA Card Market Cap":
    st.header("PSA 10 Card Market Cap Dashboard")
    st.metric("Total Cards", len(filtered_df))

    # Top Cards by Market Cap
    st.subheader("Top 20 Cards by Market Cap")
    top_market_cap = (
        filtered_df.sort_values(by="market-cap", ascending=False)
        .head(20)
        .reset_index(drop=True)
    )
    top_market_cap['Ranking'] = top_market_cap.index + 1
    st.markdown(
        render_table_with_links(
            top_market_cap,
            ['Ranking', 'product-name', 'console-name', 'formatted-loose-price', 'formatted-psa-10-price', 'sales-volume', 'formatted-market-cap'],
            'product-url'
        ),
        unsafe_allow_html=True
    )

    # Top Cards by Profitability
    st.subheader("Top 20 Cards by Profitability")
    top_profitability = (
        filtered_df.sort_values(by="grading-profitability-percent", ascending=False)  # Sort by numeric profitability
        .head(20)
        .reset_index(drop=True)
    )
    top_profitability['Ranking'] = top_profitability.index + 1
    st.markdown(
        render_table_with_links(
            top_profitability,
            ['Ranking', 'product-name', 'console-name', 'formatted-loose-price', 'formatted-psa-10-price', 'sales-volume', 'grading-profitability'],
            'product-url'
        ),
        unsafe_allow_html=True
    )

    # Scatterplot Visualization
    st.subheader("Loose Price vs PSA 10 Graded Price")
    scatter_fig = px.scatter(
        filtered_df,
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

elif selected_page == "PSA Card Trends":
    try:
        import psa_trends
        # Define filters to pass
        filters = {
            "min_psa_price": min_psa_price,
            "max_psa_price": max_psa_price,
            "min_loose_price": min_loose_price,
            "max_loose_price": max_loose_price,
            "min_sales": min_sales,
            "selected_years": selected_years,
            "selected_sets": selected_sets
        }
        psa_trends.render_trends_page(filters)
    except ModuleNotFoundError:
        st.write("The PSA Trends module is not yet available. Please upload `psa_trends.py` to enable this feature.")
    except Exception as e:
        st.error(f"An error occurred while rendering the PSA Trends page: {str(e)}")
