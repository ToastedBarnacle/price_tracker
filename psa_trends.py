import streamlit as st
import pandas as pd
import os

# Constants
DATA_FOLDER = "Data"

def load_data_files(selected_previous_file):
    """Load the newest and selected previous data files for trend analysis."""
    data_files = get_data_files()

    if len(data_files) < 2:
        st.error(f"At least two data files are required in the '{DATA_FOLDER}' folder for trends analysis.")
        st.stop()

    newest_file = os.path.join(DATA_FOLDER, data_files[0])

    if selected_previous_file not in data_files:
        st.error(f"Invalid selected file: {selected_previous_file}. Please select a valid previous data set.")
        st.stop()

    previous_file = os.path.join(DATA_FOLDER, selected_previous_file)

    newest_df = pd.read_csv(newest_file)
    previous_df = pd.read_csv(previous_file)

    for df in [newest_df, previous_df]:
        if 'release-date' in df.columns:
            df['release-year'] = pd.to_datetime(df['release-date'], errors='coerce').dt.year.fillna(0).astype(int)

    return newest_df, previous_df

def calculate_trends(newest_df, previous_df):
    """Calculate trends by comparing the newest and previous datasets."""
    trend_data = newest_df[['id', 'product-name', 'console-name', 'loose-price', 'psa-10-price', 'sales-volume']].merge(
        previous_df[['id', 'loose-price', 'psa-10-price', 'sales-volume']],
        on='id',
        suffixes=('_new', '_old')
    )

    # Calculate percentage changes
    trend_data['loose-price-change'] = ((trend_data['loose-price_new'] - trend_data['loose-price_old']) /
                                        trend_data['loose-price_old']) * 100
    trend_data['psa-10-price-change'] = ((trend_data['psa-10-price_new'] - trend_data['psa-10-price_old']) /
                                         trend_data['psa-10-price_old']) * 100
    trend_data['sales-volume-change'] = ((trend_data['sales-volume_new'] - trend_data['sales-volume_old']) /
                                         trend_data['sales-volume_old']) * 100

    return trend_data

def render_trends_page(selected_previous_file):
    """Render the PSA Trends page."""
    try:
        # 🚀 Debugging: Ensure this is a string
        st.write(f"DEBUG: Selected Previous File -> {selected_previous_file} (Type: {type(selected_previous_file)})")

        if not isinstance(selected_previous_file, str):
            st.error(f"Invalid file selection: {selected_previous_file}. Please select a valid CSV file.")
            return

        # Load the data files
        newest_df, previous_df = load_data_files(selected_previous_file)
        trend_data = calculate_trends(newest_df, previous_df)

        # Toggle to switch between gainers and losers
        toggle_option = st.radio("Select Trend View", ["Biggest Gainers", "Biggest Losers"], horizontal=True)

        # Formatting for display
        def format_currency(value):
            return f"${value:,.2f}" if pd.notnull(value) else "N/A"

        def format_sales(value):
            return f"{int(value):,}" if pd.notnull(value) else "N/A"

        def format_percentage(value):
            return f"{value:.2f}%" if pd.notnull(value) else "N/A"

        # Apply formatting
        for column in ['loose-price-change', 'psa-10-price-change', 'sales-volume-change']:
            trend_data[column] = trend_data[column].apply(lambda x: format_percentage(x) if pd.notnull(x) else "N/A")

        for column in ['loose-price_new', 'loose-price_old', 'psa-10-price_new', 'psa-10-price_old']:
            trend_data[column] = trend_data[column].apply(lambda x: format_currency(x) if pd.notnull(x) else "N/A")

        for column in ['sales-volume_new', 'sales-volume_old']:
            trend_data[column] = trend_data[column].apply(lambda x: format_sales(x) if pd.notnull(x) else "N/A")

        # Generate PriceCharting link for each card
        def get_pricecharting_link(product_id):
            return f"https://www.pricecharting.com/offers?product={product_id}"

        trend_data['Product Link'] = trend_data['id'].apply(get_pricecharting_link)

        # Function to render a trends table
        def render_table(title, sort_column, ascending_order):
            st.subheader(title)

            sorted_trend_data = trend_data.sort_values(by=sort_column, ascending=ascending_order)
            sorted_trend_data['Ranking'] = range(1, len(sorted_trend_data) + 1)

            table = sorted_trend_data.head(10)[
                ['Ranking', 'product-name', 'console-name', 'loose-price_old', 'loose-price_new',
                 'psa-10-price_old', 'psa-10-price_new', 'sales-volume_old', 'sales-volume_new',
                 sort_column, 'Product Link']
            ].rename(columns={
                'Ranking': 'Rank',
                'product-name': 'Card Name',
                'console-name': 'Set',
                'loose-price_old': 'Last Loose Price',
                'loose-price_new': 'New Loose Price',
                'psa-10-price_old': 'Last PSA 10 Price',
                'psa-10-price_new': 'New PSA 10 Price',
                'sales-volume_old': 'Previous Sales',
                'sales-volume_new': 'New Sales',
                sort_column: '% Change',
                'Product Link': 'PriceCharting Link'
            }).reset_index(drop=True)

            st.table(table)

        # Render either biggest gainers or biggest losers based on toggle selection
        if toggle_option == "Biggest Gainers":
            render_table("Top 10 Gainers - Loose Price", 'loose-price-change', ascending_order=False)
            render_table("Top 10 Gainers - PSA 10 Price", 'psa-10-price-change', ascending_order=False)
            render_table("Top 10 Gainers - Sales Volume", 'sales-volume-change', ascending_order=False)
        else:
            render_table("Top 10 Losers - Loose Price", 'loose-price-change', ascending_order=True)
            render_table("Top 10 Losers - PSA 10 Price", 'psa-10-price-change', ascending_order=True)
            render_table("Top 10 Losers - Sales Volume", 'sales-volume-change', ascending_order=True)

    except Exception as e:
        st.error(f"An error occurred while rendering the PSA Trends page: {str(e)}")

def get_data_files():
    """Get the available data files in the Data folder."""
    data_files = [f for f in os.listdir(DATA_FOLDER) if f.startswith("filtered_price_data_") and f.endswith(".csv")]
    data_files.sort(reverse=True)
    return data_files

# ✅ **Final Fix**
available_files = get_data_files()

if available_files:
    # 🚀 **Ensure only filenames are passed to `render_trends_page()`**
    selected_previous_file = st.sidebar.selectbox("Select the previous data set", available_files, index=1)
    
    if isinstance(selected_previous_file, str) and selected_previous_file in available_files:
        render_trends_page(selected_previous_file)
    else:
        st.error("Invalid file selection. Please select a valid dataset.")
else:
    st.error("No valid data files found in the 'Data' folder. Please upload at least two CSV files.")
