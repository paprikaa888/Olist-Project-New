
import pandas as pd
import numpy as np
import seaborn as sns
import datetime as dt
import matplotlib.pyplot as plt
import plotly.express as px

customers = pd.read_csv('./download/olistbr_brazilian-ecommerce/olist_customers_dataset.csv', sep=",")
locations = pd.read_csv('./download/olistbr_brazilian-ecommerce/olist_geolocation_dataset.csv', sep=",")
order_items = pd.read_csv('./download/olistbr_brazilian-ecommerce/olist_order_items_dataset.csv', sep=",")
order_payments = pd.read_csv('./download/olistbr_brazilian-ecommerce/olist_order_payments_dataset.csv', sep=",")
order_reviews = pd.read_csv('./download/olistbr_brazilian-ecommerce/olist_order_reviews_dataset.csv', sep=",")
orders = pd.read_csv('./download/olistbr_brazilian-ecommerce/olist_orders_dataset.csv', sep=",")
products = pd.read_csv('./download/olistbr_brazilian-ecommerce/olist_products_dataset.csv', sep=",")
sellers = pd.read_csv('./download/olistbr_brazilian-ecommerce/olist_sellers_dataset.csv', sep=",")
product_category_name = pd.read_csv('./download/olistbr_brazilian-ecommerce/product_category_name_translation.csv', sep=",")



merged_df1 = pd.merge(products, product_category_name, on='product_category_name', how='left')

merged_df1 = merged_df1.drop(columns=['product_category_name', 'product_name_lenght', 'product_description_lenght', 'product_weight_g', 'product_length_cm', 'product_height_cm', 'product_width_cm'])


merged_df1 = merged_df1[['product_id', 'product_category_name_english', 'product_photos_qty']]
merged_df1


merged_df2 = pd.merge(order_items, merged_df1, on='product_id', how='left')
merged_df2

merged_df2 = merged_df2.drop('order_item_id', axis=1)

merged_df2

merged_df3 = pd.merge(merged_df2, order_payments, on= 'order_id', how= 'left')
merged_df3

orders.info()

merged_df3.info()

merged_df4= pd.merge(merged_df3, orders, on= 'order_id', how= 'left')
merged_df4.info()

merged_df4

order_reviews.info()

merged_df5= pd.merge(merged_df4, order_reviews, on= 'order_id', how= 'left')
merged_df5

reviews_only = pd.merge(order_reviews, merged_df4, on= 'order_id', how= 'left')
reviews_only
