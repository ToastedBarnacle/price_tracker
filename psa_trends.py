import os
import pandas as pd

def load_trend_data(data_folder):
    data_files = [f for f in os.listdir(data_folder) if f.startswith("filtered_price_data_") and f.endswith(".csv")]
    data_files.sort(reverse=True)

    if len(data_files) < 2:
        raise ValueError("At least two data files are required to calculate trends.")

    df_new = pd.read_csv(os.path.join(data_folder, data_files[0]))
    df_old = pd.read_csv(os.path.join(data_folder, data_files[1]))

    merged_df = pd.merge(
        df_new,
        df_old,
        on="id",
        suffixes=("_new", "_old")
    )

    merged_df["loose_price_change"] = ((merged_df["loose-price_new"] - merged_df["loose-price_old"]) / merged_df["loose-price_old"]) * 100
    merged_df["psa10_price_change"] = ((merged_df["psa-10-price_new"] - merged_df["psa-10-price_old"]) / merged_df["psa-10-price_old"]) * 100
    merged_df["sales_volume_change"] = ((merged_df["sales-volume_new"] - merged_df["sales-volume_old"]) / merged_df["sales-volume_old"]) * 100

    merged_df.replace([float("inf"), -float("inf")], 0, inplace=True)
    merged_df.fillna(0, inplace=True)

    return merged_df

def display_trends(merged_df, st):
    st.subheader("Top 10 Cards by Loose Price Change")
    top_loose_price_change = (
        merged_df.sort_values(by="loose_price_change", ascending=False)
        .head(10)
        .reset_index(drop=True)
    )
    st.write(top_loose_price_change[["product-name_new", "loose_price_change"]])

    st.subheader("Top 10 Cards by PSA 10 Price Change")
    top_psa10_price_change = (
        merged_df.sort_values(by="psa10_price_change", ascending=False)
        .head(10)
        .reset_index(drop=True)
    )
    st.write(top_psa10_price_change[["product-name_new", "psa10_price_change"]])

    st.subheader("Top 10 Cards by Sales Volume Change")
    top_sales_volume_change = (
        merged_df.sort_values(by="sales_volume_change", ascending=False)
        .head(10)
        .reset_index(drop=True)
    )
    st.write(top_sales_volume_change[["product-name_new", "sales_volume_change"]])
