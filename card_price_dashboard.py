import streamlit as st
import pandas as pd
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder

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

# Generate PriceCharting URLs
BASE_URL = "https://www.pricecharting.com/offers?product="
df['product-url'] = df['id'].apply(lambda x: f"{BASE_URL}{x}")

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

# Filter by release year
st.sidebar.markdown("### Release Year")
years = list(range(1999, 2026))
selected_years = st.sidebar.multiselect(
    "Select Release Years",
    options=years,
    default=years
)

# "Select All" button
if st.sidebar.button("Select All Years"):
    selected_years = years

# Apply filters
filtered_df = df[
    (df['psa-10-price'] >= min_psa_price) &
    (df['psa-10-price'] <= max_psa_price) &
    (df['loose-price'] >= min_loose_price) &
    (df['loose-price'] <= max_loose_price) &
    (df['grading-profitability'] >= min_grading_profitability) &
    (df['sales-volume'] >= min_sales) &
    (df['release-year'].isin(selected_years))
]

# Add ranks for the tables
filtered_df['Ranking'] = filtered_df['market-cap'].rank(ascending=False, method="dense")
filtered_df['Rank Grading'] = filtered_df['grading-profitability'].rank(ascending=False, method="dense")

# Function to render tables using AgGrid
def render_aggrid_table(dataframe, columns):
    # Rename columns for consistency
    display_df = dataframe.rename(columns={
        'product-name': 'Card',
        'console-name': 'Set',
        'loose-price': 'Raw Price',
        'psa-10-price': 'PSA 10 Price',
        'sales-volume': 'Sales/Year',
        'market-cap': 'Market Cap',
        'product-url': 'PriceCharting Link'
    })
    grid_options = GridOptionsBuilder.from_dataframe(display_df[columns])
    grid_options.configure_pagination()
    grid_options.configure_sorting()
    grid_options.configure_column('PriceCharting Link', cellRenderer='function(params) { return `<a href="${params.value}" target="_blank">View</a>` }')
    grid_options = grid_options.build()
    AgGrid(display_df[columns], gridOptions=grid_options, enable_enterprise_modules=True)

# Main Dashboard
st.title("PSA 10 Card Market Cap Dashboard")

# Total Cards Metric
st.metric("Total Cards", len(filtered_df))

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
    ['Ranking', 'Card', 'Set', 'Raw Price', 'PSA 10 Price', 'Sales/Year', 'Market Cap', 'PriceCharting Link']
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
    ['Ranking', 'Card', 'Set', 'Raw Price', 'PSA 10 Price', 'Sales/Year', 'Grading Profitability', 'PriceCharting Link']
)
