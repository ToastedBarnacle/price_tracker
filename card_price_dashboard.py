import os
import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from bs4 import BeautifulSoup

# Set page title
st.set_page_config(page_title="PSA 10 Card Market Cap Dashboard")
@@ -22,23 +19,9 @@
# Extract release year from release-date
df['release-year'] = pd.to_datetime(df['release-date'], errors='coerce').dt.year.fillna(0).astype(int)

# Function to fetch image URLs (cached)
@st.cache_data
def fetch_image_url(product_id):
    try:
        url = f"https://www.pricecharting.com/offers?product={product_id}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            img_tag = soup.find("img", {"class": "product-image"})
            if img_tag and "src" in img_tag.attrs:
                return img_tag["src"]
    except Exception as e:
        st.error(f"Error fetching image for product {product_id}: {e}")
    return None
# Add a column for image URLs
df["image-url"] = df["id"].apply(fetch_image_url)
# Generate PriceCharting URLs
BASE_URL = "https://www.pricecharting.com/offers?product="
df['product-url'] = df['id'].apply(lambda x: f"{BASE_URL}{x}")

# Sidebar Filters
st.sidebar.header("Filters")
@@ -77,12 +60,48 @@ def fetch_image_url(product_id):
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
    (df['loose-price'] <= max_loose_price)
    (df['loose-price'] <= max_loose_price) &
    (df['grading-profitability'] >= min_grading_profitability) &
    (df['sales-volume'] >= min_sales) &
    (df['release-year'].isin(selected_years))
]

# Add ranks for the tables
@@ -95,26 +114,60 @@ def fetch_image_url(product_id):
# Total Cards Metric
st.metric("Total Cards", len(filtered_df))

# Display Top Cards by Market Cap with Images
st.header("Top Cards by Market Cap")
# Function to generate an HTML table with clickable links
def render_table_with_links(df, columns, url_column):
    table_html = df[columns + [url_column]].copy()
    table_html[url_column] = table_html[url_column].apply(
        lambda x: f'<a href="{x}" target="_blank">View on PriceCharting</a>'
    )
    table_html = table_html.to_html(escape=False, index=False)
    return table_html
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
        ['Ranking', 'product-name', 'console-name', 'loose-price', 'psa-10-price', 'sales-volume', 'market-cap'],
        'product-url'
    ),
    unsafe_allow_html=True
)

# Add images to the dataframe
top_market_cap["Image"] = top_market_cap["image-url"].apply(
    lambda url: f'<img src="{url}" style="width:50px; height:auto;">' if url else "No Image"
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

# Display HTML table
st.write(
    top_market_cap.to_html(
        escape=False,
        index=False,
        columns=["Ranking", "product-name", "psa-10-price", "loose-price", "market-cap", "Image"],
# Most Profitable Cards to Grade
st.subheader("20 Most Profitable Cards to Grade")
top_grading_profitability = (
    filtered_df.sort_values(by="grading-profitability", ascending=False)
    .head(20)
    .reset_index(drop=True)
)
top_grading_profitability['Ranking'] = top_grading_profitability.index + 1
st.markdown(
    render_table_with_links(
        top_grading_profitability,
        ['Ranking', 'product-name', 'console-name', 'loose-price', 'psa-10-price', 'sales-volume', 'grading-profitability'],
        'product-url'
    ),
    unsafe_allow_html=True,
    unsafe_allow_html=True
)