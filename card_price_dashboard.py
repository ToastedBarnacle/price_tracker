# Main Dashboard
st.markdown("<h1 style='text-align: center;'>CardMarketCap.App</h1>", unsafe_allow_html=True)
selected_page = st.radio("Navigation", ["PSA Card Market Cap", "PSA Card Trends"], horizontal=True)

if selected_page == "PSA Card Market Cap":
    st.header("PSA 10 Card Market Cap Dashboard")
    st.metric("Total Cards", len(filtered_df))

    # Keep numeric version of 'market-cap' for sorting
    sorted_market_cap_df = filtered_df.copy()
    sorted_market_cap_df = sorted_market_cap_df.sort_values(by="market-cap", ascending=False).head(20)

    # Format financial columns for display
    sorted_market_cap_df['Raw Price'] = sorted_market_cap_df['loose-price'].apply(format_currency)
    sorted_market_cap_df['PSA 10 Price'] = sorted_market_cap_df['psa-10-price'].apply(format_currency)
    sorted_market_cap_df['Market Cap'] = sorted_market_cap_df['market-cap'].apply(format_currency)
    sorted_market_cap_df['Sales/Year'] = sorted_market_cap_df['sales-volume'].apply(format_sales)

    # Top Cards by Market Cap
    st.subheader("Top 20 Cards by Market Cap")
    sorted_market_cap_df['Ranking'] = range(1, len(sorted_market_cap_df) + 1)
    st.markdown(
        render_table_with_links(
            sorted_market_cap_df,
            ['Ranking', 'product-name', 'console-name', 'Raw Price', 'PSA 10 Price', 'Sales/Year', 'Market Cap'],
            'product-url'
        ),
        unsafe_allow_html=True
    )

    # Top Cards by Profitability
    st.subheader("Top 20 Cards by Profitability")
    top_profitability = (
        filtered_df.sort_values(by="grading-profitability", ascending=False)
        .head(20)
        .reset_index(drop=True)
    )
    top_profitability['Ranking'] = range(1, len(top_profitability) + 1)
    top_profitability['Raw Price'] = top_profitability['loose-price'].apply(format_currency)
    top_profitability['PSA 10 Price'] = top_profitability['psa-10-price'].apply(format_currency)
    top_profitability['Sales/Year'] = top_profitability['sales-volume'].apply(format_sales)
    top_profitability['Grading Profitability'] = top_profitability['grading-profitability'].apply(format_currency)

    st.markdown(
        render_table_with_links(
            top_profitability,
            ['Ranking', 'product-name', 'console-name', 'Raw Price', 'PSA 10 Price', 'Sales/Year', 'Grading Profitability'],
            'product-url'
        ),
        unsafe_allow_html=True
    )

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

elif selected_page == "PSA Card Trends":
    st.header("PSA Card Trends")
    st.write("This page is under construction.")
