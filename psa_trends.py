import streamlit as st
import pandas as pd
import os

# Constants
DATA_FOLDER = "Data"  # Folder where CSV data files are stored

def get_data_files():
    """Retrieve all available data files sorted by date (newest first)."""
    data_files = [f for f in os.listdir(DATA_FOLDER) if f.startswith("filtered_price_data_") and f.endswith(".csv")]
    data_files.sort(reverse=True)
    return data_files

def load_data_files(previous_file):
    """Load the most recent dataset and the selected previous dataset for comparison."""
    data_files = get_data_files()
    
    if len(data_files) < 2:
        st.error("Not enough data files for trend analysis. Upload at least two files.")
        return None, None

    newest_file = os.path.join(DATA_FOLDER, data_files[0])

    if previous_file not in data_files:
        st.error(f"Invalid previous file selected: {previous_file}")
        return None, None

    previous_file_path = os.path.join(DATA_FOLDER, previous_file)

    st.write(f"📂 Loading newest file: {data_files[0]}")
    st.write(f"📂 Loading previous file: {previous_file}")

    newest_df = pd.read_csv(newest_file)
    previous_df = pd.read_csv(previous_file_path)

    if newest_df.empty or previous_df.empty:
        st.error("🚨 One or both datasets are empty!")
        return None, None

    # Ensure 'release-year' is parsed correctly
    for df in [newest_df, previous_df]:
        if 'release-date' in df.columns:
            df['release-year'] = pd.to_datetime(df['release-date'], errors='coerce').dt.year.fillna(0).astype(int)

    st.write("✅ Newest dataset loaded:", newest_df.head())
    st.write("✅ Previous dataset loaded:", previous_df.head())

    return newest_df, previous_df

def calculate_trends(newest_df, previous_df, filters):
    """Apply filters and calculate trends."""
    if newest_df is None or previous_df is None:
        return None

    def apply_filters(df, filters):
        return df[
            (df['psa-10-price'] >= filters['min_psa_price']) &
            (df['psa-10-price'] <= filters['max_psa_price']) &
            (df['loose-price'] >= filters['min_loose_price']) &
            (df['loose-price'] <= filters['max_loose_price']) &
            (df['sales-volume'] >= filters['min_sales']) &
            (df['release-year'].isin(filters['selected_years']))
        ]

    newest_df = apply_filters(newest_df, filters)
    previous_df = apply_filters(previous_df, filters)

    if newest_df.empty or previous_df.empty:
        st.warning("⚠️ No matching data found after filtering.")
        return None

    # Merge datasets and calculate trends
    trend_data = newest_df[['id', 'product-name', 'console-name', 'loose-price', 'psa-10-price', 'sales-volume']].merge(
        previous_df[['id', 'loose-price', 'psa-10-price', 'sales-volume']],
        on='id',
        suffixes=('_new', '_old')
    )

    if trend_data.empty:
        st.warning("⚠️ No matching records found after merging datasets.")
        return None

    # Compute percentage changes, handling division by zero
    for col in ['loose-price', 'psa-10-price', 'sales-volume']:
        trend_data[f"{col}-change"] = ((trend_data[f"{col}_new"] - trend_data[f"{col}_old"]) /
                                       trend_data[f"{col}_old"].replace(0, float('nan'))) * 100

    st.write("✅ Trend data computed:", trend_data.head())

    return trend_data.dropna()

def render_trends_page(filters):
    """Render the PSA Trends page with proper debugging and fallback messages."""
    data_files = get_data_files()
    if len(data_files) < 2:
        st.warning("⚠️ Not enough data files for trend analysis. Upload at least two files.")
        return

    # Select previous dataset from dropdown
    selected_previous_file = st.selectbox("Compare to previous data set:", data_files[1:], index=0)

    # Load datasets
    newest_df, previous_df = load_data_files(selected_previous_file)
    if newest_df is None or previous_df is None:
        return

    trend_data = calculate_trends(newest_df, previous_df, filters)

    if trend_data is None or trend_data.empty:
        st.warning("⚠️ No data available to display.")
        return

    # Toggle for gainers/losers
    trend_type = st.radio("Select Trend Type", ["Top Gainers", "Top Losers"], horizontal=True)
    ascending = (trend_type == "Top Losers")

    # Formatting functions
    def format_currency(value):
        return f"${value:,.2f}" if pd.notnull(value) else "N/A"

    def format_sales(value):
        return f"{int(value):,}" if pd.notnull(value) else "N/A"

    def format_percentage(value):
        return f"{value:.2f}%" if pd.notnull(value) else "N/A"

    # Apply formatting
    for col in ['loose-price', 'psa-10-price', 'sales-volume']:
        trend_data[f"{col}-change"] = trend_data[f"{col}-change"].apply(format_percentage)
        trend_data[f"{col}_new"] = trend_data[f"{col}_new"].apply(format_currency)
        trend_data[f"{col}_old"] = trend_data[f"{col}_old"].apply(format_currency)

    # Generate PriceCharting links
    trend_data['PriceCharting Link'] = trend_data['id'].apply(lambda x: f"[View](https://www.pricecharting.com/offers?product={x})")

    # Function to render tables
    def render_table(title, sort_column, additional_columns):
        st.subheader(title)
        sorted_data = trend_data.copy()
        sorted_data[sort_column] = pd.to_numeric(sorted_data[sort_column].str.replace('%', ''), errors='coerce')
        sorted_data = sorted_data.sort_values(by=sort_column, ascending=ascending)
        sorted_data['Rank'] = range(1, len(sorted_data) + 1)

        table = sorted_data.head(10)[['Rank', 'product-name', 'console-name'] + additional_columns + [sort_column, 'PriceCharting Link']]
        table = table.rename(columns={
            'product-name': 'Card Name',
            'console-name': 'Set',
            'loose-price_old': 'Last Price',
            'loose-price_new': 'New Price',
            'psa-10-price_old': 'Last Price',
            'psa-10-price_new': 'New Price',
            'sales-volume_old': 'Previous Sales',
            'sales-volume_new': 'New Sales',
            sort_column: '% Change',
        })

        st.table(table)

    # Render trend tables
    render_table("Top 10 Cards by Loose Price Change", "loose-price-change", ['loose-price_old', 'loose-price_new'])
    render_table("Top 10 Cards by PSA 10 Price Change", "psa-10-price-change", ['psa-10-price_old', 'psa-10-price_new'])
    render_table("Top 10 Cards by Sales Volume Change", "sales-volume-change", ['sales-volume_old', 'sales-volume_new'])

# Sidebar Filters
filters = {
    "min_psa_price": 0.0,
    "max_psa_price": 1000.0,
    "min_loose_price": 0.0,
    "max_loose_price": 1000.0,
    "min_sales": 0,
    "selected_years": list(range(1999, 2026)),
}

# Render PSA Trends Page
render_trends_page(filters)
