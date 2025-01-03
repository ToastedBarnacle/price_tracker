import streamlit as st
import pandas as pd
import plotly.express as px

# Load the data
DATA_FILE = "filtered_price_data.csv"  # Your filtered CSV file
df = pd.read_csv(DATA_FILE)

# Convert prices to dollars for better readability
df['psa-10-price'] = df['psa-10-price']
df['loose-price'] = df['loose-price']
df['grading-profitability'] = df['psa-10-price'] - df['loose-price']

# Sidebar Filters
st.sidebar.header("Filters")
min_psa_price = st.sidebar.slider("Minimum PSA 10 Price ($)", 0, int(df['psa-10-price'].max()), 0)
min_loose_price = st.sidebar.slider("Minimum Loose Price ($)", 0, int(df['loose-price'].max()), 0)
min_grading_profitability = st.sidebar.slider("Minimum Grading Profitability ($)", 0, int(df['grading-profitability'].max()), 0)
min_sales = st.sidebar.slider("Minimum Sales Volume", 0, int(df['sales-volume'].max()), 0)

# Apply filters
filtered_df = df[
    (df['psa-10-price'] >= min_psa_price) &
    (df['loose-price'] >= min_loose_price) &
    (df['grading-profitability'] >= min_grading_profitability) &
    (df['sales-volume'] >= min_sales)
]

# Main Dashboard
st.title("Card Price Tracker Dashboard")

# Display Metrics
st.header("Summary Metrics")
st.metric("Total Cards", len(filtered_df))

# Scatterplot Visualization
st.header("Loose Price vs PSA 10 Graded Price")
scatter_fig = px.scatter(
    filtered_df,
    x="loose-price",
    y="psa-10-price",
    hover_name="product-name",  # Shows card name on hover
    title="Loose Price vs PSA 10 Graded Price",
    labels={"loose-price": "Loose Price ($)", "psa-10-price": "PSA 10 Price ($)"},
    template="plotly_white",
)
scatter_fig.update_traces(marker=dict(size=10, opacity=0.7))

# Show scatterplot
st.plotly_chart(scatter_fig, use_container_width=True)

# Display Filtered Table
st.header("Filtered Card Data")
st.dataframe(filtered_df[['product-name', 'loose-price', 'psa-10-price', 'grading-profitability', 'sales-volume']])
