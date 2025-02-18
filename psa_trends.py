import streamlit as st
import pandas as pd
import os

# Constants
DATA_FOLDER = "Data"  # Correctly capitalized folder name

def get_data_files():
    """Get the available data files in the Data folder."""
    data_files = [f for f in os.listdir(DATA_FOLDER) if f.startswith("filtered_price_data_") and f.endswith(".csv")]
    data_files.sort(reverse=True)  # Sort files by name (newest date first)
    return data_files

def load_data_files(selected_previous_file):
    """Load the newest and selected previous data files for trend analysis."""
    # Get all available files
    data_files = get_data_files()

    # Ensure at least two files exist
    if len(data_files) < 2:
        st.error(f"At least two data files are required in the '{DATA_FOLDER}' folder for trends analysis.")
        st.stop()

    # Load the newest file
    newest_file = os.path.join(DATA_FOLDER, data_files[0])

    # Validate the selected previous file
    if selected_previous_file not in data_files:
        st.error(f"Invalid selected file: {selected_previous_file}. Please select a valid previous data set.")
        st.stop()

    previous_file = os.path.join(DATA_FOLDER, selected_previous_file)

    newest_df = pd.read_csv(newest_file)
    previous_df = pd.read_csv(previous_file)

    # Add the release-year column dynamically
    for df in [newest_df, previous_df]:
        if 'release-date' in df.columns:
            df['release-year'] = pd.to_datetime(df['release-date'], errors='coerce').dt.year.fillna(0).astype(int)

    return newest_df, previous_df

def calculate_trends(newest_df, previous_df, filters):
    """Calculate trends by comparing the newest and previous datasets, with filtering."""
    # Apply filters to both dataframes
    def apply_filters(df, filters):
        filtered_df = df[
            (df['psa-10-price'] >= filters['min_psa_price']) &
            (df['psa-10-price'] <= filters['max_psa_price']) &
            (df['loose-price'] >= filters['min_loose_price']) &
            (df['loose-price'] <= filters['max_loose_price']) &
            (df['sales-volume'] >= filters['min_sales']) &
            (df['release-year'].isin(filters['selected_years']))
        ]
        if 'selected_sets' in filters and filters['selected_sets']:  # Ensure it exists before using
            filtered_df = filtered_df[filtered_df['console-name'].isin(filters['selected_sets'])]
        return filtered_df

    newest_df = apply_filters(newest_df, filters)
    previous_df = apply_filters(previous_df, filters)

    # Merge and calculate trends
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

def render_trends_page():
    """Render the PSA Trends page."""
    st.title("PSA Trends Dashboard")

    # Select previous data set (newest is default)
    data_files = get_data_files()
    selected_previous_file = st.selectbox("Select the previous data set", data_files[1:], index=0)  # Default to second newest

    try:
        # Load the data files
        newest_df, previous_df = load_data_files(selected_previous_file)

        # Sidebar filters
        st.sidebar.header("Filters")
        min_psa_price = st.sidebar.number_input("Min PSA 10 Price ($)", min_value=0.0, value=0.0, step=1.0)
        max_psa_price = st.sidebar.number_input("Max PSA 10 Price ($)", min_value=0.0, value=1000.0, step=1.0)
        min_loose_price = st.sidebar.number_input("Min Loose Price ($)", min_value=0.0, value=0.0, step=1.0)
        max_loose_price = st.sidebar.number_input("Max Loose Price ($)", min_value=0.0, value=1000.0, step=1.0)
        min_sales = st.sidebar.number_input("Min Sales Volume", min_value=0, value=0, step=1)
        selected_years = st.sidebar.multiselect("Select Release Years", options=list(range(1999, 2026)), default=list(range(1999, 2026)))
        
        # Dropdown to select sets
        all_sets = newest_df['console-name'].dropna().unique().tolist()
        selected_sets = st.sidebar.multiselect("Select Set", options=all_sets, default=[])

        # Filters
        filters = {
            "min_psa_price": min_psa_price,
            "max_psa_price": max_psa_price,
            "min_loose_price": min_loose_price,
            "max_loose_price": max_loose_price,
            "min_sales": min_sales,
            "selected_years": selected_years,
            "selected_sets": selected_sets
        }

        # Calculate trends
        trend_data = calculate_trends(newest_df, previous_df, filters)

        # Add toggle button for gainers/losers
        trend_type = st.radio("Select Trend Type", ["Top Gainers", "Top Losers"], horizontal=True)
        ascending = (trend_type == "Top Losers")  # Sort descending for gainers, ascending for losers

        # Generate PriceCharting link for each card
        trend_data['Product Link'] = trend_data['id'].apply(lambda x: f"[View on PriceCharting](https://www.pricecharting.com/offers?product={x})")

        # Helper function to render a trends table
        def render_table(title, sort_column, additional_columns):
            st.subheader(title)
            sorted_trend_data = trend_data.copy()
            sorted_trend_data[sort_column] = pd.to_numeric(
                sorted_trend_data[sort_column].astype(str).str.replace('%', ''), errors='coerce'
            )  # Convert percentages back to numeric
            sorted_trend_data = sorted_trend_data.sort_values(by=sort_column, ascending=ascending)
            sorted_trend_data['Ranking'] = range(1, len(sorted_trend_data) + 1)  # Add ranking column

            # Remove index before displaying
            sorted_trend_data = sorted_trend_data.reset_index(drop=True)

            # Display the table
            st.table(
                sorted_trend_data.head(10)[['Ranking', 'product-name', 'console-name'] + additional_columns + [sort_column, 'Product Link']].rename(
                    columns={
                        'Ranking': 'Rank',
                        'product-name': 'Card Name',
                        'console-name': 'Set',
                        'loose-price_old': 'Last Price',
                        'loose-price_new': 'New Price',
                        'psa-10-price_old': 'Last Price',
                        'psa-10-price_new': 'New Price',
                        'sales-volume_old': 'Previous Sales',
                        'sales-volume_new': 'New Sales',
                        sort_column: '% Change',
                        'Product Link': 'PriceCharting Link'
                    }
                )
            )

        # Render tables
        render_table("Top 10 Cards by Loose Price Change", 'loose-price-change', ['loose-price_old', 'loose-price_new'])
        render_table("Top 10 Cards by PSA 10 Price Change", 'psa-10-price-change', ['psa-10-price_old', 'psa-10-price_new'])
        render_table("Top 10 Cards by Sales Volume Change", 'sales-volume-change', ['sales-volume_old', 'sales-volume_new'])

    except Exception as e:
        st.error(f"An error occurred while rendering the PSA Trends page: {str(e)}")

# Run the page
render_trends_page()
