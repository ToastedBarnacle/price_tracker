# Main Dashboard
st.title("PSA 10 Card Dashboard")

# Enlarged Navigation with Side-by-Side Options
st.markdown("<h2 style='text-align: center;'>Navigation</h2>", unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    if st.button("PSA Card Market Cap"):
        selected_page = "PSA Card Market Cap"
    else:
        selected_page = "PSA Card Market Cap" if "selected_page" not in st.session_state else st.session_state["selected_page"]

with col2:
    if st.button("PSA Card Trends"):
        selected_page = "PSA Card Trends"
    else:
        selected_page = selected_page if "selected_page" in st.session_state else "PSA Card Market Cap"

# Persist selected page in session state
st.session_state["selected_page"] = selected_page

if selected_page == "PSA Card Market Cap":
    st.header("PSA 10 Card Market Cap Dashboard")
    st.metric("Total Cards", len(filtered_df))

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

    # Top Cards by Profitability
    st.subheader("Top 20 Cards by Profitability")
    top_profitability = (
        filtered_df.sort_values(by="grading-profitability", ascending=False)
        .head(20)
        .reset_index(drop=True)
    )
    top_profitability['Ranking'] = top_profitability.index + 1
    st.markdown(
        render_table_with_links(
            top_profitability,
            ['Ranking', 'product-name', 'console-name', 'loose-price', 'psa-10-price', 'sales-volume', 'grading-profitability'],
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
