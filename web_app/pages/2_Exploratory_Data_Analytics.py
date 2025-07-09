import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import copy
warnings.simplefilter(action='ignore', category=FutureWarning)

st.image("https://miro.medium.com/v2/resize:fit:4800/format:webp/1*1k72mg1_CZvLptX77zzKTg.png")

customers = pd.read_csv('../Data/olist_customers_dataset.csv', sep=",")
locations = pd.read_csv('../Data/olist_geolocation_dataset.csv', sep=",")
order_items = pd.read_csv('../Data/olist_order_items_dataset.csv', sep=",")
order_payments = pd.read_csv('../Data/olist_order_payments_dataset.csv', sep=",")
order_reviews = pd.read_csv('../Data/olist_order_reviews_dataset.csv', sep=",")
orders = pd.read_csv('../Data/olist_orders_dataset.csv', sep=",")
products = pd.read_csv('../Data/olist_products_dataset.csv', sep=",")
sellers = pd.read_csv('../Data/olist_sellers_dataset.csv', sep=",")
product_category_name = pd.read_csv('../Data/product_category_name_translation.csv', sep=",")

merged_df1 = pd.merge(orders, order_items, on='order_id', how='left')
merged_df2 = pd.merge(merged_df1, products, on='product_id', how='inner')
merged_df3 = pd.merge(merged_df2, order_payments, on='order_id', how='left')
merged_df4 = pd.merge(merged_df3, order_reviews, on='order_id', how='left')
merged_df5 = pd.merge(merged_df4, customers, on='customer_id', how='right')
final_df = pd.merge(merged_df5, product_category_name, on='product_category_name', how='inner')

final_df_filtered = final_df.drop(columns=['order_approved_at','order_delivered_carrier_date','shipping_limit_date','review_id', 'product_name_lenght','payment_installments', 'product_description_lenght', 'review_comment_title', 'review_comment_message', 'review_creation_date', 'review_answer_timestamp','order_item_id', 'customer_id'])

st.header("Exploratory Data Analysis (EDA)")
st.write("In this section, we will perform Exploratory Data Analysis (EDA) on the Olist dataset to gain insights into the business performance of Olist between 2016 and 2018. We will analyze customer distribution, monthly revenues, top product categories, review scores, delivery times, and more.")

final_df_capped = final_df_filtered.copy()

def capping_outlier(col):
    lwr_limit = final_df_capped[col].quantile(0.03)
    upr_limit = final_df_capped[col].quantile(0.97)

    print(str(col).upper())
    print("lwr:", lwr_limit, "upr:", upr_limit)
    print()
    
    final_df_capped[col] = np.where(
        final_df_capped[col] > upr_limit, upr_limit,
        np.where(final_df_capped[col] < lwr_limit, lwr_limit, final_df_capped[col])
    )

outlier_col = ['price', 'freight_value', 'payment_value']

for col in outlier_col:
    capping_outlier(col)

final_df_clean = final_df_capped.copy()

final_df_clean['order_purchase_timestamp'] = pd.to_datetime(final_df_clean['order_purchase_timestamp'])

#2. Fig. Customer Distribution by State
state_counts = final_df_clean['customer_state'].value_counts().reset_index()
state_counts.columns = ['State', 'Customer Count']

fig = px.bar(
    state_counts,
    x='State',
    y='Customer Count',
    labels={'State': 'State', 'Customer Count': 'Customer Count'},
    color='State',
    text='Customer Count'
)

fig.update_layout(
    xaxis_title='State',
    yaxis_title='Number of Customers',
    showlegend=False,
    plot_bgcolor='white',
    height=600,
    width=1000
)


st.subheader("Customer Distribution by State")
st.write("This bar chart shows the distribution of customers across different states in Brazil. Each bar represents the number of customers from a specific state, providing insights into regional customer demographics.")
st.write("The chart highlights the states with the highest customer counts, indicating where Olist has a strong customer base. This information can be useful for targeted marketing strategies and understanding regional market dynamics.")

st.plotly_chart(fig)

#3. Fig. Monthly Revenues by Top Five Cities
final_df_filtered['order_month'] = pd.to_datetime(final_df_filtered['order_purchase_timestamp']).dt.to_period('M')
if 'revenue' not in final_df_filtered.columns:
    final_df_filtered['revenue'] = final_df_filtered['price'] + final_df_filtered['freight_value']

top_cities = (
    final_df_filtered
    .groupby('customer_city')['revenue']
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .index
)
city_abbreviations = {city: city[:3].upper() for city in top_cities}

filtered_df = final_df_filtered[final_df_filtered['customer_city'].isin(top_cities)].copy()
filtered_df['city_abbr'] = filtered_df['customer_city'].map(city_abbreviations)
filtered_df['order_month'] = filtered_df['order_month'].dt.to_timestamp()

df = (
    filtered_df
    .groupby(['city_abbr', 'customer_city', 'order_month'])['revenue']
    .sum()
    .reset_index()
    .sort_values('order_month')
)

max_revenue = df['revenue'].max()
yaxis_range = [0, max_revenue * 1.1]  

fig2 = px.bar(
    df,
    x="city_abbr",
    y="revenue",
    color="customer_city",
    animation_frame=df['order_month'].dt.strftime('%Y-%m'),
    category_orders={"city_abbr": df['city_abbr'].unique().tolist()},  
    hover_name="customer_city",
    labels={
        "city_abbr": "City",
        "revenue": "Total Revenue (R$)",
        "customer_city": "City"
    },
    range_y=yaxis_range  
)

fig2.update_layout(
    xaxis_title="<b>City</b>",
    yaxis_title="<b>Total Revenue (R$)</b>",
    plot_bgcolor='white',
    height=500,
    width=1200,  
    hovermode='closest',
    updatemenus=[{
        'buttons': [
            {
                'args': [None, {'frame': {'duration': 800, 'redraw': True}, 
                               'transition': {'duration': 300}}],
                'label': '▶️ Play',
                'method': 'animate'
            },
            {
                'args': [[None], {'frame': {'duration': 0, 'redraw': True}, 
                                'mode': 'immediate', 'transition': {'duration': 0}}],
                'label': '❚❚ Pause',
                'method': 'animate'
            }
        ],
        'direction': 'left',
        'pad': {'r': 10, 't': 70},
        'x': 0.1,
        'xanchor': 'right',
        'y': 0,
        'yanchor': 'top'
    }],
    legend=dict(
        orientation="v",
        yanchor="middle",
        y=0.5,
        xanchor="left",
        x=1.05,
        title_text="City"
    ),
    margin=dict(l=50, r=50, t=80, b=50)
)

fig2.update_xaxes(tickangle=0, tickfont=dict(size=12))
fig2.update_yaxes(
    tickprefix="R$ ",
    gridcolor='lightgrey',
    tickformat=",.0f",
    range=yaxis_range
)

fig2.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>"
                 "Month: %{frame}<br>"
                 "Revenue: <b>R$ %{y:,.2f}</b><extra></extra>",
    hovertext=df['customer_city'] 
)

fig2.add_annotation(
    x=0.5,
    y=1.05,
    xref='paper',
    yref='paper',
    text='consistent scale',
    showarrow=False,
    font=dict(size=10, color='gray')
)

st.subheader("Monthly Revenues by Top 5 Cities")
st.write("This animated bar chart shows the monthly revenues generated by the top five cities in Brazil. Each bar represents the total revenue for a specific city in a given month, allowing us to observe trends and fluctuations over time.")
st.write("The chart highlights the cities with the highest revenues, providing insights into regional performance and customer engagement. The animation allows for easy tracking of revenue changes across months, making it a valuable tool for understanding market dynamics.")

st.plotly_chart(fig2)


st.subheader("Top 10 Product Categories by Orders and Monetary Value")
st.write("This section analyzes the top 10 product categories based on the number of orders and total monetary value. We will visualize the data using horizontal bar charts to compare the most popular categories in terms of order volume and revenue.")


products_by_order = final_df_clean.groupby('product_category_name_english').count()[['order_id']].sort_values(by='order_id', ascending=False).reset_index()[:10]
product_by_payment_value = final_df_clean.groupby('product_category_name_english')[['payment_value']].sum().sort_values(by='payment_value', ascending=False).reset_index()[:10]

def get_color_gradient(values):
    normalized = (values - values.min()) / (values.max() - values.min())
    colors = [
        f'rgba({int(150 - 100*v)}, {int(100 - 50*v)}, {int(200)}, 0.8)' 
        for v in normalized
    ]
    return colors[::-1]

orders_colors = get_color_gradient(products_by_order['order_id'])
monetary_colors = get_color_gradient(product_by_payment_value['payment_value'])

fig3 = make_subplots(rows=1, cols=2, subplot_titles=(
    "Top 10 Product Categories by Orders",
    "Top 10 Product Categories by Monetary Value"
))

fig3.add_trace(
    go.Bar(
        x=products_by_order['order_id'],
        y=products_by_order['product_category_name_english'],
        orientation='h',
        marker=dict(color=orders_colors),
        name='Total Orders',
        hovertemplate='Category: %{y}<br>Total Orders: %{x}<extra></extra>'
    ),
    row=1, col=1
)

fig3.add_trace(
    go.Bar(
        x=product_by_payment_value['payment_value'],
        y=product_by_payment_value['product_category_name_english'],
        orientation='h',
        marker=dict(color=monetary_colors),
        name='Total Monetary',
        hovertemplate='Category: %{y}<br>Total Monetary: R$ %{x:,.2f}<extra></extra>'
    ),
    row=1, col=2
)

fig3.update_layout(
    height=600,
    width=1150,
    showlegend=False,
    plot_bgcolor='white',
    margin=dict(t=100, l=50, r=50, b=50)
)

fig3.update_yaxes(autorange="reversed", row=1, col=1)
fig3.update_yaxes(autorange="reversed", row=1, col=2)

st.plotly_chart(fig3)

st.subheader("Review Scores Distribution")
st.write("This section analyzes the distribution of review scores given by customers. We will visualize the data using a donut chart to show the percentage of each review score category (1 to 5).")
st.write("The donut chart provides a clear visual representation of the review scores, allowing us to quickly assess customer satisfaction levels across different orders.If the majority of scores are in the 4 and 5 range, it indicates high customer satisfaction. Conversely, a significant number of low scores (1 and 2) may suggest areas for improvement in product quality or service.")

st.write("A higher percentage of scores in the 4 and 5 range indicates better customer satisfaction, while a significant number of low scores (1 and 2) may suggest areas for improvement in product quality or service.")
print("\nReview Scores Distribution (% of total):")
print((final_df_clean['review_score'].value_counts(normalize=True) * 100).round(2))

review_scores_distribution = (final_df_clean['review_score'].value_counts(normalize=True) * 100).round(2)

review_scores_distribution = (final_df_clean['review_score'].value_counts(normalize=True) * 100)

fig8 = px.pie(review_scores_distribution, 
             values=review_scores_distribution.values, 
             names=review_scores_distribution.index,
             hole=0.5,
             color_discrete_sequence=px.colors.qualitative.Pastel)

fig8.update_layout(
    margin=dict(l=30, r=30, t=50, b=30),
    showlegend=True,
    height=500,
    width=500
)

fig8.update_traces(
    textposition='inside',
    textinfo='percent+label',
    textfont=dict(size=16),
    hovertemplate='<b>Score %{label}</b><br>Percentage: %{percent:.1%}<extra></extra>'
)

st.plotly_chart(fig8)

st.subheader("Delivery Performance Analysis")
st.write("In this section, we will analyze the delivery performance of Olist by calculating the actual delivery time and comparing it with the estimated delivery time. We will visualize the results using histograms and scatter plots to understand the distribution of delivery times and their relationship with review scores.")
st.write("We will calculate the actual delivery days as the difference between the order purchase timestamp and the order delivered customer date. We will also calculate the estimated delivery days as the difference between the order purchase timestamp and the order estimated delivery date. Finally, we will compute the delivery difference as the difference between actual and estimated delivery days.")

final_df_clean['order_purchase_timestamp'] = pd.to_datetime(final_df_clean['order_purchase_timestamp'])
final_df_clean['order_delivered_customer_date'] = pd.to_datetime(final_df_clean['order_delivered_customer_date'])
final_df_clean['order_estimated_delivery_date'] = pd.to_datetime(final_df_clean['order_estimated_delivery_date'])

final_df_clean['actual_delivery_days'] = (
    final_df_clean['order_delivered_customer_date'] - final_df_clean['order_purchase_timestamp']
).dt.days

final_df_clean['estimated_delivery_days'] = (
    final_df_clean['order_estimated_delivery_date'] - final_df_clean['order_purchase_timestamp']
).dt.days

final_df_clean['delivery_difference'] = (
    final_df_clean['actual_delivery_days'] - final_df_clean['estimated_delivery_days']
)

print('\nDelivery Performance Summary:')
print('-' * 40)

stats = final_df_clean[['actual_delivery_days', 'estimated_delivery_days', 'delivery_difference']].describe().round(3)

print(stats.to_string(float_format='%.3f'))
print('-' * 40)

plt.figure(figsize=(12,6))
sns.histplot(final_df_clean['actual_delivery_days'].dropna(), bins=30, kde=True)
plt.figure(figsize=(12, 6))
sns.histplot(final_df_clean['actual_delivery_days'].dropna(), bins=30, kde=True)

plt.xlabel('Delivery Days')
plt.ylabel('Frequency')

st.pyplot(plt)

st.subheader("Delivery Time vs Review Score")
st.write("This scatter plot visualizes the relationship between actual delivery days and review scores. Each point represents an order, with the x-axis showing the actual delivery days and the y-axis showing the review score given by the customer. The color of each point indicates the review score, allowing us to see how delivery times relate to customer satisfaction.")
st.write("The plot helps us understand whether there is a correlation between delivery times and customer review scores. A trend where shorter delivery times lead to higher review scores may indicate that timely deliveries positively impact customer satisfaction.")


fig4= px.scatter(final_df_clean,
                x='actual_delivery_days',
                y='review_score',
                color='review_score',
                size_max=40,
                opacity=0.6,
                labels={
                    'actual_delivery_days': 'Actual Delivery Days',
                    'review_score': 'review_score (1-5)'
                    })

fig4.add_vline(x=final_df_clean['actual_delivery_days'].median(),
              line_dash='dash', line_color='green')
fig4.update_layout(
    hovermode='closest',
    xaxis_range=[0, final_df_clean['actual_delivery_days'].max()*1.1],
    yaxis_range=[0.5, 5.5],
    showlegend=False)

st.plotly_chart(fig4)

print(final_df_clean.columns)


st.subheader("Percentage of Orders Delivered On Time")
final_df_clean['on_time'] = (final_df_clean['delivery_difference'] <= 0).astype(int)
on_time_percentage = final_df_clean['on_time'].mean() * 100

late_percentage = 100 - on_time_percentage

print(f"\nOn-time Delivery Percentage: {on_time_percentage:.2f}%")

labels=['On-time', 'Late']
sizes=[on_time_percentage, late_percentage]
colors=['#66c2a5', '#fc8d62']
explode=(0.1, 0)  
plt.figure(figsize=(8, 6))  
plt.pie(sizes, explode=explode, labels=labels, colors=colors,
        autopct='%1.1f%%', shadow=True, startangle=140)  
plt.axis('equal') 

st.write("This pie chart illustrates the percentage of orders delivered on time versus those that were late. The 'On-time' segment represents orders that were delivered within the estimated delivery timeframe, while the 'Late' segment indicates orders that exceeded the estimated delivery date.")
st.write(f"On-time Delivery Percentage: {on_time_percentage:.2f}%")
st.write("This metric is crucial for understanding Olist's delivery performance and customer satisfaction. A higher on-time delivery percentage indicates efficient logistics and fulfillment processes, which are essential for maintaining customer trust and loyalty.")

st.pyplot(plt)