import streamlit as st
import pandas as pd
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder

# Set page title
st.set_page_config(page_title="PSA 10 Card Market Cap Dashboard")

# Load the data
DATA_FILE = "filtered_price_data.csv"  # Your filtered CSV file
df = pd.read_csv(DATA_FILE)

# Debugging: Print column names to ensure they match
st.write("Columns in Dataframe:", df.columns.tolist())

# Ensure all necessary columns exist and rename them
df.rename(
    columns={
        "loose-price": "Raw Price",
        "psa-10-price": "PSA 10 Price",
        "sales-volume": "Sales/Year",
        "market-cap": "Market Cap",
        "console-name": "Set",
        "grading-profitability": "Grading Profitability",
    },
    inplace=True,
    errors="ignore",  # Do not raise errors for missing columns
)

# Add computed columns if missing
if "Grading Profitability" not in df.columns:
    df["Grading Profitability"] = pd.to_numeric(df["PSA 10 Price"], errors="coerce") - pd.to_numeric(df["Raw Price"], errors="coerce")
    df["Grading Profitability"] = df["Grading Profitability"].fillna(0)

if "Market Cap" not in df.columns:
    df["Market Cap"] = pd.to_numeric(df["Raw Price"], errors="coerce") * pd.to_numeric(df["Sales/Year"], errors="coerce")
    df["Market Cap"] = df["Market Cap"].fillna(0)

# Sidebar Filters
st.sidebar.header("Filters")

# Minimum and maximum PSA 10 price filter
st.sidebar.markdown("### PSA 10 Price ($)")
min_psa_price = st.sidebar.number_input(
    "Minimum PSA 10 Price ($)", 
    min_value=0.0, 
    max_value=float(df["PSA 10 Price"].max()), 
    value=float(df["PSA 10 Price"].min()), 
    step=1.0
)
max_psa_price = st.sidebar.number_input(
    "Maximum PSA 10 Price ($)", 
    min_value=0.0, 
    max_value=float(df["PSA 10 Price"].max()), 
    value=float(df["PSA 10 Price"].max()), 
    step=1.0
)

# Minimum and maximum raw price filter
st.sidebar.markdown("### Raw Price ($)")
min_raw_price = st.sidebar.number_input(
    "Minimum Raw Price ($)", 
    min_value=0.0, 
    max_value=float(df["Raw Price"].max()), 
    value=float(df["Raw Price"].min()), 
    step=1.0
)
max_raw_price = st.sidebar.number_input(
    "Maximum Raw Price ($)", 
    min_value=0.0, 
    max_value=float(df["Raw Price"].max()), 
    value=float(df["Raw Price"].max()), 
    step=1.0
)

# Minimum grading profitability filter
st.sidebar.markdown("### Grading Profitability ($)")
min_grading_profitability = st.sidebar.number_input(
    "Minimum Grading Profitability ($)", 
    min_value=0.0, 
    max_value=float(df["Grading Profitability"].max()), 
    value=0.0, 
    step=1.0
)

# Minimum sales volume filter
st.sidebar.markdown("### Sales/Year")
min_sales = st.sidebar.number_input(
    "Minimum Sales/Year",
    min_value=0,
    max_value=int(df["Sales/Year"].max()),
    value=0,
    step=1
)

# Apply filters
filtered_df = df[
    (df["PSA 10 Price"] >= min_psa_price) &
    (df["PSA 10 Price"] <= max_psa_price) &
    (df["Raw Price"] >= min_raw_price) &
    (df["Raw Price"] <= max_raw_price) &
    (df["Grading Profitability"] >= min_grading_profitability) &
    (df["Sales/Year"] >= min_sales)
]

# Add ranks for the tables
filtered_df["Ranking"] = filtered_df["Market Cap"].rank(ascending=False, method="dense")
filtered_df["Rank Grading"] = filtered_df["Grading Profitability"].rank(ascending=False, method="dense")

# Main Dashboard
st.title("PSA 10 Card Market Cap Dashboard")

# Total Cards Metric
st.metric("Total Cards", len(filtered_df))

# Render sortable tables with AgGrid
def render_aggrid_table(df, columns):
    grid_options = GridOptionsBuilder.from_dataframe(df[columns])
    grid_options.configure_pagination(paginationAutoPageSize=True)
    grid_options.configure_default_column(
        sortable=True, filter=True, resizable=True
    )
    AgGrid(df[columns], gridOptions=grid_options.build())

# Top Cards by Market Cap
st.subheader("Top 20 Cards by Market Cap")
top_market_cap = (
    filtered_df.sort_values(by="Market Cap", ascending=False)
    .head(20)
    .reset_index(drop=True)
)
top_market_cap["Ranking"] = top_market_cap.index + 1
render_aggrid_table(
    top_market_cap,
    ["Ranking", "product-name", "Set", "Raw Price", "PSA 10 Price", "Sales/Year", "Market Cap"]
)
