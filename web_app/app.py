# Import necessary libraries
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime


customers = pd.read_csv('../Data/olist_customers_dataset.csv', sep=",")
locations = pd.read_csv('../Data/olist_geolocation_dataset.csv', sep=",")
order_items = pd.read_csv('../Data/olist_order_items_dataset.csv', sep=",")
order_payments = pd.read_csv('../Data/olist_order_payments_dataset.csv', sep=",")
order_reviews = pd.read_csv('../Data/olist_order_reviews_dataset.csv', sep=",")
orders = pd.read_csv('../Data/olist_orders_dataset.csv', sep=",")
products = pd.read_csv('../Data/olist_products_dataset.csv', sep=",")
sellers = pd.read_csv('../Data/olist_sellers_dataset.csv', sep=",")
product_category_name = pd.read_csv('../Data/product_category_name_translation.csv', sep=",")


st.image("https://miro.medium.com/v2/resize:fit:4800/format:webp/1*1k72mg1_CZvLptX77zzKTg.png")
st.title("Olist E-Commerce Analysis             (2016-2018)")


st.header("Project Introduction")
st.write("Welcome to our Olist E-Commerce Analysis project! This project is a collaborative effort by four data enthusiasts who are passionate about understanding business performance through data analysis.")
st.write("We are Francesca, Patrycja, Apo, and Moses. This project analyzes the business performance of the company Olist. Our goal is to understand how Olist performed between 2016-2018 and identify key factors for its success.")

st.header("About Olist")
st.write("Olist is a Brazilian e-commerce platform that connects small and medium-sized businesses with customers. The company has experienced significant growth since its inception, particularly in the post-recession period. In this analysis, we will explore Olist's sales data to understand the factors contributing to its success.")

st.header("About the dataset")
st.write("""
    The dataset contains information about Olist's sales transactions, including order details, customer information, and product categories.  
    We will analyze this data to identify trends and patterns that can help us understand the company's growth trajectory.
    """)
st.header("Hypothesis")
st.write("""
    Our hypothesis is that Olist's growth during the recession can be attributed to its strong business model, effective marketing strategies, and the increasing popularity of e-commerce.
    """)
st.header("Tech Stack Used")
st.write("""
    We use Python, Streamlit, Plotly, Github and other libraries to analyze the data and visualize our findings.
    """)

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
        st.image("https://www.python.org/static/community_logos/python-logo-master-v3-TM.png", caption="Python", width=80)
with col2:
        st.image("https://upload.wikimedia.org/wikipedia/commons/8/84/Matplotlib_icon.svg", caption="Matplotlib", width=80)
with col3:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/37/Plotly-logo-01-square.png/480px-Plotly-logo-01-square.png", caption="Plotly", width=80)
with col4:
        st.image("https://streamlit.io/images/brand/streamlit-logo-primary-colormark-darktext.png", caption="Streamlit", width=80)
with col5:
        st.image("https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png", caption="GitHub", width=80)
with col6:
        st.image("https://pandas.pydata.org/pandas-docs/stable/_static/pandas.svg", caption="Pandas", width=80)


st.sidebar.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSbIviVf57xxZq-bMB7oCMNlPtgcqfclkyhGQ&s", width=100)
now = datetime.now()
formatted_time = now.strftime("%A, %d %B %Y, %H:%M")
st.sidebar.write(formatted_time)
st.sidebar.map()
st.sidebar.expander("Expand me!")
st.sidebar.download_button("Download data", "../Data")
st.sidebar.video("https://www.youtube.com/watch?v=YBw4flsZ-MM")
st.sidebar.text_input("Enter your name", "Type Here ...")
st.sidebar.text_area("Enter your feedback", "Type Here ...")

show_data = st.sidebar.checkbox("Show Data")
if show_data:
    st.write("### Data Frame")
    
    # Map display names to actual keys
    option_map = {
        "Order Reviews": "order_reviews",
        "Customers": "customers",
        "Sellers": "sellers",
        "Products": "products",
        "Orders": "orders",
        "Order Items": "order_items",
        "Order Payments": "order_payments",
        "Product Category Name": "product_category_name",
        "Locations": "locations"
    }

    option = st.selectbox("Select dataset:", list(option_map.keys()))

    df_dict = {
        "customers": pd.read_csv('../Data/olist_customers_dataset.csv', sep=","),
        "locations": pd.read_csv('../Data/olist_geolocation_dataset.csv', sep=","),
        "order_items": pd.read_csv('../Data/olist_order_items_dataset.csv', sep=","),
        "order_payments": pd.read_csv('../Data/olist_order_payments_dataset.csv', sep=","),
        "order_reviews": pd.read_csv('../Data/olist_order_reviews_dataset.csv', sep=","),
        "orders": pd.read_csv('../Data/olist_orders_dataset.csv', sep=","),
        "products": pd.read_csv('../Data/olist_products_dataset.csv', sep=","),
        "sellers": pd.read_csv('../Data/olist_sellers_dataset.csv', sep=","),
        "product_category_name": pd.read_csv('../Data/product_category_name_translation.csv', sep=",")
    }

    # Use the mapped key
    st.dataframe(df_dict[option_map[option]])