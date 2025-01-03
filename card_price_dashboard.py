import streamlit as st
import pandas as pd
import plotly.express as px

# Load the data
DATA_FILE = "filtered_price_data.csv"  # Your filtered CSV file
df = pd.read_csv(DATA_FILE)

# Ensure all necessary columns exist and compute missing ones dynamically
df['grading-profitability'] = pd.to_numeric(df['psa-10-price'], errors='coerce') - pd.to_numeric(df['loose-price'], errors='coerce')
df['grading-profitability'] = df['grading-profitability'].fillna(0)

df['market-cap'] = pd.to_numeric(df['loose-price'], errors='coerce') * pd.to_numeric(df['sales-volume'], errors='coerce')
df['market-cap'] = df['market-cap'].fillna(0)

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

# Minimum grading profitability filter
st.sidebar.markdown("### Grading Profitability ($)")
min_grading_profitability = st.sidebar.number_input(
    "Minimum Grading Profitability ($)", 
    min_value=0.0, 
    max_value=float(df['grading-profitability'].max()), 
    value=0.0, 
    step=1.0
)

# Minimum sales volume filter
st.sidebar.markdown("### Sales Volume")
min_sales = st.sidebar.number_input(
    "Minimum Sales Volume",
    min_value=0,
    max_value=int(df['sales-volume'].max()),
    value=0,
    step=1
)

# Apply filters
filtered_df = df[
    (df['psa-10-price'] >= min_psa_price) &
    (df['psa-10-price'] <= max_psa_price) &
    (df['loose-price'] >= min_loose_price) &
    (df['loose-price'] <= max_loose_price) &
    (df['grading-profitability'] >= min_grading_profitability) &
    (df['sales-volume'] >= min_sales)
]

# Add ranks for the tables
filtered_df['Ranking'] = filtered_df['market-cap'].rank(ascending=False, method="dense").astype(int)
filtered_df['Rank Grading'] = filtered_df['grading-profitability'].rank(ascending=False, method="dense").astype(int)

# Format price and market cap columns
price_columns = ['psa-10-price', 'loose-price', 'grading-profitability', 'market-cap']
for col in price_columns:
    filtered_df[col] = filtered_df[col].apply(lambda x: f"${x:,.2f}" if pd.notnull(x) else "N/A")

# Main Dashboard
st.title("PSA Card Market Cap Dashboard")

# Total Cards Metric
st.header("Total Cards Included in Filter Selections")
st.metric("Total Cards", len(filtered_df))

# Top Cards by Market Cap
st.header("Top Cards by Market Cap")
top_market_cap = (
    filtered_df.sort_values(by="market-cap", ascending=False)
    .head(20)
    .reset_index(drop=True)
)
top_market_cap['Ranking'] = top_market_cap.index + 1
st.subheader("Top 20 Cards by Market Cap")
st.write(
    top_market_cap.rename(
        columns={
            "Ranking": "Ranking",
            "product-name": "Card",
            "console-name": "Console",
            "loose-price": "Raw Price",
            "psa-10-price": "PSA 10 Price",
            "sales-volume": "Sales/Year",
            "market-cap": "Market Cap"
        }
    )[['Ranking', 'Card', 'Console', 'Raw Price', 'PSA 10 Price', 'Sales/Year', 'Market Cap']]
)

# Scatterplot Visualization
st.header("Grading Profitability Data")
st.subheader("Loose Price vs PSA 10 Graded Price")
scatter_fig = px.scatter(
    filtered_df,
    x="loose-price",
    y="psa-10-price",
    hover_name="product-name",
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
st.write(
    top_grading_profitability.rename(
        columns={
            "Ranking": "Ranking",
            "product-name": "Card",
            "console-name": "Console",
            "loose-price": "Raw Price",
            "psa-10-price": "PSA 10 Price",
            "sales-volume": "Sales/Year",
            "grading-profitability": "Grading Profitability"
        }
    )[['Ranking', 'Card', 'Console', 'Raw Price', 'PSA 10 Price', 'Sales/Year', 'Grading Profitability']]
)
