import streamlit as st
import pandas as pd
import os

# Constants
DATA_FOLDER = "Data"  # Correctly capitalized folder name

def load_data_files():
    """Load the two most recent data files for trend analysis."""
    # List all data files
    data_files = [f for f in os.listdir(DATA_FOLDER) if f.startswith("filtered_price_data_") and f.endswith(".csv")]
    data_files.sort(reverse=True)  # Sort files by name (newest date first)

    # Ensure we have at least two files
    if len(data_files) < 2:
        st.error(f"At least two data files are required in the '{DATA_FOLDER}' folder for trends analysis.")
        st.stop()

    # Load the newest and previous data files
    newest_file = os.path.join(DATA_FOLDER, data_files[0])
    previous_file = os.path.join(DATA_FOLDER, data_files[1])
    newest_df = pd.read_csv(newest_file)
    previous_df = pd.read_csv(previous_file)

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

def render_trends_page():
    """Render the PSA Trends page."""
    try:
        newest_df, previous_df = load_data_files()
        trend_data = calculate_trends(newest_df, previous_df)

        # Formatting for display
        def format_percentage(value):
            return f"{value:.2f}%" if pd.notnull(value) else "N/A"

        # Apply formatting
        trend_data['loose-price-change'] = trend_data['loose-price-change'].apply(format_percentage)
        trend_data['psa-10-price-change'] = trend_data['psa-10-price-change'].apply(format_percentage)
        trend_data['sales-volume-change'] = trend_data['sales-volume-change'].apply(format_percentage)

        # Add toggle button for increase/decrease trends
        trend_type = st.radio("Select Trend Type", ["Increase", "Decrease"], horizontal=True)
        ascending = trend_type == "Decrease"

        # Helper function to render a trends table
        def render_table(title, column_name, sort_column):
            st.subheader(title)
            sorted_trend_data = trend_data.copy()
            sorted_trend_data[sort_column] = pd.to_numeric(
                sorted_trend_data[sort_column].str.replace('%', ''), errors='coerce'
            )  # Convert percentages back to numeric
            sorted_trend_data = sorted_trend_data.sort_values(by=sort_column, ascending=ascending)
            sorted_trend_data['Ranking'] = range(1, len(sorted_trend_data) + 1)  # Add ranking column
            table = sorted_trend_data.head(10)[['Ranking', 'product-name', 'console-name', sort_column]].rename(
                columns={
                    'Ranking': 'Rank',
                    'product-name': 'Card Name',
                    'console-name': 'Set',
                    sort_column: '% Change'
                }
            )
            st.table(table)

        # Render tables
        render_table("Top 10 Cards by Loose Price Change", "loose-price-change", 'loose-price-change')
        render_table("Top 10 Cards by PSA 10 Price Change", "psa-10-price-change", 'psa-10-price-change')
        render_table("Top 10 Cards by Sales Volume Change", "sales-volume-change", 'sales-volume-change')

    except Exception as e:
        st.error(f"An error occurred while rendering the PSA Trends page: {str(e)}")
