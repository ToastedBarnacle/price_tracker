import streamlit as st
import pandas as pd
import os

# Constants
DATA_FOLDER = "Data"  # Correctly capitalized folder name

def load_data_files(selected_previous_file):
    """Load the newest and selected previous data files for trend analysis."""
    data_files = [f for f in os.listdir(DATA_FOLDER) if f.startswith("filtered_price_data_") and f.endswith(".csv")]
    data_files.sort(reverse=True)  

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

def apply_filters(df, filters):
    """Apply filters including search and language toggle."""
    df = df[
        (df['psa-10-price'] >= filters['min_psa_price']) & 
        (df['psa-10-price'] <= filters['max_psa_price']) &
        (df['loose-price'] >= filters['min_loose_price']) & 
        (df['loose-price'] <= filters['max_loose_price']) & 
        (df['sales-volume'] >= filters['min_sales']) &
        (df['release-year'].isin(filters['selected_years']))
    ]

    if filters['selected_sets']:
        df = df[df['console-name'].isin(filters['selected_sets'])]

    # Apply name search filter
    if filters['search_name']:
        df = df[df['product-name'].str.contains(filters['search_name'], case=False, na=False)]

    # Apply language filter
    if filters['language_filter'] == "English Only":
        df = df[~df['console-name'].str.contains("Japanese", case=False, na=False)]
    elif filters['language_filter'] == "Japanese Only":
        df = df[df['console-name'].str.contains("Japanese", case=False, na=False)]

    return df

def render_trends_page(filters):
    """Render the PSA Trends page."""
    try:
        selected_previous_file = st.selectbox("Select the previous data set", get_data_files(), index=1)
        newest_df, previous_df = load_data_files(selected_previous_file)

        newest_df = apply_filters(newest_df, filters)
        previous_df = apply_filters(previous_df, filters)

        trend_data = newest_df[['id', 'product-name', 'console-name', 'loose-price', 'psa-10-price', 'sales-volume']].merge(
            previous_df[['id', 'loose-price', 'psa-10-price', 'sales-volume']],
            on='id',
            suffixes=('_new', '_old')
        )

        trend_data['loose-price-change'] = ((trend_data['loose-price_new'] - trend_data['loose-price_old']) /
                                            trend_data['loose-price_old']) * 100
        trend_data['psa-10-price-change'] = ((trend_data['psa-10-price_new'] - trend_data['psa-10-price_old']) /
                                             trend_data['psa-10-price_old']) * 100
        trend_data['sales-volume-change'] = ((trend_data['sales-volume_new'] - trend_data['sales-volume_old']) /
                                             trend_data['sales-volume_old']) * 100

        st.dataframe(trend_data)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

def get_data_files():
    """Get the available data files in the Data folder."""
    data_files = [f for f in os.listdir(DATA_FOLDER) if f.startswith("filtered_price_data_") and f.endswith(".csv")]
    data_files.sort(reverse=True)
    return data_files

filters = {
    "min_psa_price": 0.0,
    "max_psa_price": 1000.0,
    "min_loose_price": 0.0,
    "max_loose_price": 1000.0,
    "min_sales": 0,
    "selected_years": list(range(1999, 2026)),
    "selected_sets": [],
    "search_name": st.sidebar.text_input("Search Card Name"),
    "language_filter": st.sidebar.radio("Filter by Language", ["Both", "English Only", "Japanese Only"])
}

render_trends_page(filters)
