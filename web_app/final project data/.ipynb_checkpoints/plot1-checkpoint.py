
import plotly.express as px
import streamlit as st
import pandas as pd

from capstone_cleaning import final_df
final_df["order_purchase_timestamp"] = pd.to_datetime(final_df["order_purchase_timestamp"])

# Create a Plotly figure
fig = px.line(
    final_df,
    x="order_purchase_timestamp",
    y="price",
    color="product_category_name_english",
    title="Sales Trends by Category",
    labels={
        "price": "Total Sales",
        "order_purchase_timestamp": "Purchase Date",
        "product_category_name_english": "Product Category",
    },
    markers=True,
)