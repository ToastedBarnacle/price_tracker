import streamlit as st
import pandas as pd
import os

# Constants
DATA_FOLDER = "Data"

def load_data_files(selected_previous_file):
    """Load the newest and selected previous data files for trend analysis."""
    data_files = sorted(
        [f for f in os.listdir(DATA_FOLDER) if f.startswith("filtered_price_data_") and f.endswith(".csv")],
        reverse=True
    )

    if len(data_files) < 2:
        st.error("At least two data files are required for trend analysis.")
        st.stop()

    newest_file = os.path.join(DATA_FOLDER, data_files[0])

    if selected_previous_file not in data_files:
        st.error(f"Invalid previous dataset: {selected_previous_file}. Please select a valid file.")
        st.stop()

    previous_file = os.path.join(DATA_FOLDER, selected_previous_file)

    newest_df = pd.read_csv(newest_file)
    previous_df = pd.read_csv(previous_file)

    for df in [newest_df, previous_df]:
        if 'release-date' in df.columns:
            df['release-year'] = pd.to_datetime(df['release-date'], errors='coerce').dt.year.fillna(0).astype(int)

    return newest_df, previous_df

def calculate_trends(newest_df, previous_df, filters):
    """Compare datasets and calculate trends."""
    def apply_filters(df):
        return df[
            (df['psa-10-price'] >= filters['min_psa_price']) &
            (df['psa-10-price'] <= filters['max_psa_price']) &
            (df['loose-price'] >= filters['min_loose_price']) &
            (df['loose-price'] <= filters['max_loose_price']) &
            (df['sales-volume'] >= filters['min_sales']) &
            (df['release-year'].isin(filters['selected_years']))
        ]

    newest_df = apply_filters(newest_df)
    previous_df = apply_filters(previous_df)

    trend_data = newest_df[['id', 'product-name', 'console-name', 'loose-price', 'psa-10-price', 'sales-volume']].merge(
        previous_df[['id', 'loose-price', 'psa-10-price', 'sales-volume']],
        on='id',
        suffixes=('_new', '_old')
    )

    trend_data['loose-price-change'] = ((trend_data['loose-price_new'] - trend_data['loose-price_old']) / trend_data['loose-price_old']) * 100
    trend_data['psa-10-price-change'] = ((trend_data['psa-10-price_new'] - trend_data['psa-10-price_old']) / trend_data['psa-10-price_old']) * 100
    trend_data['sales-volume-change'] = ((trend_data['sales-volume_new'] - trend_data['sales-volume_old']) / trend_data['sales-volume_old']) * 100

    return trend_data

def render_trends_page(filters):
    """Render the PSA Trends page with only required tables."""
    try:
        selected_previous_file = st.selectbox("Compare to previous data set", get_data_files(), index=1)

        newest_df, previous_df = load_data_files(selected_previous_file)
        trend_data = calculate_trends(newest_df, previous_df, filters)

        trend_type = st.radio("Select Type:", ["Top Gainers", "Top Losers"], horizontal=True)
        ascending = trend_type == "Top Losers"

        def get_pricecharting_link(product_id):
            return f"[View](https://www.pricecharting.com/offers?product={product_id})"

        def render_table(title, sort_column):
            st.subheader(title)
            sorted_trend_data = trend_data.copy()
            sorted_trend_data[sort_column] = pd.to_numeric(sorted_trend_data[sort_column], errors='coerce')
            sorted_trend_data = sorted_trend_data.sort_values(by=sort_column, ascending=ascending).head(10)

            sorted_trend_data['PriceCharting Link'] = sorted_trend_data['id'].apply(get_pricecharting_link)
            table = sorted_trend_data[['product-name', 'console-name', 'loose-price_old', 'loose-price_new', 'psa-10-price_old', 'psa-10-price_new', 'sales-volume_old', 'sales-volume_new', sort_column, 'PriceCharting Link']]
            
            st.table(table)

        render_table("Top 10 Cards by Loose Price Change", 'loose-price-change')
        render_table("Top 10 Cards by PSA 10 Price Change", 'psa-10-price-change')
        render_table("Top 10 Cards by Sales Volume Change", 'sales-volume-change')

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

def get_data_files():
    """Get available data files."""
    return sorted(
        [f for f in os.listdir(DATA_FOLDER) if f.startswith("filtered_price_data_") and f.endswith(".csv")],
        reverse=True
    )
