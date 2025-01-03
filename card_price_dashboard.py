import streamlit as st
import pandas as pd
import plotly.express as px

# Load the data
DATA_FILE = "filtered_price_data.csv"  # Your filtered CSV file
df = pd.read_csv(DATA_FILE)

# Calculate grading profitability
df['grading-profitability'] = df['psa-10-price'] - df['loose-price']

# Sidebar Filters
st.sidebar.header("Filters")

# Minimum and maximum PSA 10 price filter
min_psa_price = st.sidebar.slider(
    "Minimum PSA 10 Price ($)",
    min_value=float(df['psa-10-price'].min()),
    max_value=float(df['psa-10-price'].max()),
    value=float(df['psa-10-price'].min()),
    format="$%.2f"
)

max_psa_price = st.sidebar.slider(
    "Maximum PSA 10 Price ($)",
    min_value=float(df['psa-10-price'].min()),
    max_value=float(df['psa-10-price'].max()),
    value=float(df['psa-10-price'].max()),
    format="$%.2f"
)

# Minimum and maximum loose price filter
min_loose_price = st.sidebar.slider(
    "Minimum Loose Price ($)",
    min_value=float(df['loose-price'].min()),
    max_value=float(df['loose-price'].max()),
    value=float(df['loose-price'].min()),
    format="$%.2f"
)

max_loose_price = st.sidebar.slider(
    "Maximum Loose Price ($)",
    min_value=float(df['loose-price'].min()),
    max_value=float(df['loose-price'].max()),
    value=float(df['loose-price'].max()),
    format="$%.2f"
)

# Minimum grading profitability filter
min_grading_profitability = st.sidebar.slider(
    "Minimum Grading Profitability ($)",
    min_value=float(df['grading-profitability'].min()),
    max_value=float(df['grading-profitability'].max()),
    value=float(df['grading-profitability'].min()),
    format="$%.2f"
)

# Minimum sales volume filter
min_sales = st.sidebar.slider(
    "Minimum Sales Volume",
    min_value=0,
    max_value=int(df['sales-volume'].max()),
    value=0
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
