import streamlit as st
import pandas as pd

def render_trends_page(newest_df, previous_df):
    st.header("PSA Card Trends")

    # Merge the newest and previous data files on the card ID
    trend_data = newest_df[['id', 'product-name', 'loose-price', 'psa-10-price', 'sales-volume']].merge(
        previous_df[['id', 'loose-price', 'psa-10-price', 'sales-volume']],
        on='id',
        suffixes=('_new', '_old')
    )

    # Calculate percentage changes
    trend_data['loose-price-change'] = ((trend_data['loose-price_new'] - trend_data['loose-price_old']) / trend_data['loose-price_old']) * 100
    trend_data['psa-10-price-change'] = ((trend_data['psa-10-price_new'] - trend_data['psa-10-price_old']) / trend_data['psa-10-price_old']) * 100
    trend_data['sales-volume-change'] = ((trend_data['sales-volume_new'] - trend_data['sales-volume_old']) / trend_data['sales-volume_old']) * 100

    # Button to toggle between INCREASE and DECREASE
    change_type = st.radio("View trends by:", ["INCREASE", "DECREASE"], horizontal=True)

    # Determine sorting order based on selected change type
    ascending_order = (change_type == "DECREASE")

    # Function to display a trend table
    def display_trend_table(title, column):
        st.subheader(title)
        sorted_trend_data = trend_data.sort_values(by=column, ascending=ascending_order).head(10)
        formatted_data = sorted_trend_data[['product-name', column]].copy()
        formatted_data[column] = formatted_data[column].apply(lambda x: f"{x:.2f}%" if pd.notnull(x) else "N/A")
        st.table(formatted_data)

    # Display tables for each trend
    display_trend_table("Top 10 Cards by Loose Price Change", "loose-price-change")
    display_trend_table("Top 10 Cards by PSA 10 Price Change", "psa-10-price-change")
    display_trend_table("Top 10 Cards by Sales Volume Change", "sales-volume-change")
