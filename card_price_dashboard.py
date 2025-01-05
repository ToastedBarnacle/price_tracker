import streamlit as st
import pandas as pd
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder

# Set page title
st.set_page_config(page_title="PSA 10 Card Market Cap Dashboard")

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

# Sidebar Filters
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

# Add ranks for the tables
filtered_df['Ranking'] = filtered_df['market-cap'].rank(ascending=False, method="dense")

# Main Dashboard
st.title("PSA 10 Card Market Cap Dashboard")
st.metric("Total Cards", len(filtered_df))

# Function to render an AgGrid table
def render_aggrid_table(df, columns, rename_map):
    display_df = df.copy()
    display_df = display_df.rename(columns=rename_map)
    grid_options = GridOptionsBuilder.from_dataframe(display_df[columns])
    grid_options.configure_default_column(sortable=True, resizable=True, filter=True)
    grid_options.configure_pagination(enabled=True, paginationAutoPageSize=True)
    AgGrid(display_df[columns], gridOptions=grid_options.build(), theme="alpine", height=400)

# Top Cards by Market Cap
st.subheader("Top 20 Cards by Market Cap")
top_market_cap = (
    filtered_df.sort_values(by="market-cap", ascending=False)
    .head(20)
    .reset_index(drop=True)
)
top_market_cap['Ranking'] = top_market_cap.index + 1
render_aggrid_table(
    top_market_cap,
    ['Ranking', 'product-name', 'console-name', 'loose-price', 'psa-10-price', 'sales-volume', 'market-cap'],
    {
        "Ranking": "Ranking",
        "product-name": "Card",
        "console-name": "Set",
        "loose-price": "Raw Price",
        "psa-10-price": "PSA 10 Price",
        "sales-volume": "Sales/Year",
        "market-cap": "Market Cap"
    }
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

# Most Profitable Cards to Grade
st.subheader("20 Most Profitable Cards to Grade")
top_grading_profitability = (
    filtered_df.sort_values(by="grading-profitability", ascending=False)
    .head(20)
    .reset_index(drop=True)
)
top_grading_profitability['Ranking'] = top_grading_profitability.index + 1
render_aggrid_table(
    top_grading_profitability,
    ['Ranking', 'product-name', 'console-name', 'loose-price', 'psa-10-price', 'sales-volume', 'grading-profitability'],
    {
        "Ranking": "Ranking",
        "product-name": "Card",
        "console-name": "Set",
        "loose-price": "Raw Price",
        "psa-10-price": "PSA 10 Price",
        "sales-volume": "Sales/Year",
        "grading-profitability": "Grading Profitability"
    }
)
