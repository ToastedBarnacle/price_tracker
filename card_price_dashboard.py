import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Load the data
DATA_FILE = "filtered_price_data.csv"  # Your filtered CSV file
df = pd.read_csv(DATA_FILE)

# Calculate grading profitability
df['grading-profitability'] = df['psa-10-price'] - df['loose-price']

# Helper function to create a logarithmic slider
def log_slider(label, min_value, max_value, default_value):
    # Convert the min, max, and default values to logarithmic scale
    min_log = np.log10(min_value + 1)
    max_log = np.log10(max_value + 1)
    default_log = np.log10(default_value + 1)

    # Create a slider using logarithmic values
    log_value = st.sidebar.slider(
        label,
        min_value=min_log,
        max_value=max_log,
        value=default_log,
        step=0.1  # Fine-grained steps for better control
    )

    # Convert the logarithmic value back to linear space for display and filtering
    linear_value = 10**log_value - 1
    return round(linear_value, 2)

# Sidebar Filters
st.sidebar.header("Filters")

# Minimum and maximum PSA 10 price filter
min_psa_price = log_slider(
    "Minimum PSA 10 Price ($)",
    min_value=float(df['psa-10-price'].min()),
    max_value=float(df['psa-10-price'].max()),
    default_value=float(df['psa-10-price'].min())
)

max_psa_price = log_slider(
    "Maximum PSA 10 Price ($)",
    min_value=float(df['psa-10-price'].min()),
    max_value=float(df['psa-10-price'].max()),
    default_value=float(df['psa-10-price'].max())
)

# Minimum and maximum loose price filter
min_loose_price = log_slider(
    "Minimum Loose Price ($)",
    min_value=float(df['loose-price'].min()),
    max_value=float(df['loose-price'].max()),
    default_value=float(df['loose-price'].min())
)

max_loose_price = log_slider(
    "Maximum Loose Price ($)",
    min_value=float(df['loose-price'].min()),
    max_value=float(df['loose-price'].max()),
    default_value=float(df['loose-price'].max())
)

# Minimum grading profitability filter
min_grading_profitability = log_slider(
    "Minimum Grading Profitability ($)",
    min_value=float(df['grading-profitability'].min()),
    max_value=float(df['grading-profitability'].max()),
    default_value=float(df['grading-profitability'].min())
)

# Minimum sales volume filter (linear scale)
min_sales = st.sidebar.slider(
    "Minimum Sales Volume",
    min_value=0,
    max_value=int(df['sales-volume'].max()),
    value=0
)

# Sidebar Ranges (formatted)
st.sidebar.markdown("### Filter Ranges")
st.sidebar.markdown(f"PSA 10 Price: ${min_psa_price:.2f} - ${max_psa_price:.2f}")
st.sidebar.markdown(f"Loose Price: ${min_loose_price:.2f} - ${max_loose_price:.2f}")
st.sidebar.markdown(f"Grading Profitability: ${min_grading_profitability:.2f}+")

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
