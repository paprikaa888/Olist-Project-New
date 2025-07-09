import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots 
import numpy as np
import statsmodels.api as sm
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
# Load the dataset
customers = pd.read_csv('../Data/olist_customers_dataset.csv', sep=",")
locations = pd.read_csv('../Data/olist_geolocation_dataset.csv', sep=",")
order_items = pd.read_csv('../Data/olist_order_items_dataset.csv', sep=",")
order_payments = pd.read_csv('../Data/olist_order_payments_dataset.csv', sep=",")
order_reviews = pd.read_csv('../Data/olist_order_reviews_dataset.csv', sep=",")
orders = pd.read_csv('../Data/olist_orders_dataset.csv', sep=",")
products = pd.read_csv('../Data/olist_products_dataset.csv', sep=",")
sellers = pd.read_csv('../Data/olist_sellers_dataset.csv', sep=",")
product_category_name = pd.read_csv('../Data/product_category_name_translation.csv', sep=",")
# Merge the datasets
merged_df1 = pd.merge(orders, order_items, on='order_id', how='left')
merged_df2 = pd.merge(merged_df1, products, on='product_id', how='inner')
merged_df3 = pd.merge(merged_df2, order_payments, on='order_id', how='left')
merged_df4 = pd.merge(merged_df3, order_reviews, on='order_id', how='left')
merged_df5 = pd.merge(merged_df4, customers, on='customer_id', how='right')
final_df = pd.merge(merged_df5, product_category_name, on='product_category_name', how='inner')
#Dataframes
#final_df_filtered
final_df_filtered = final_df.drop(columns=['order_approved_at','order_delivered_carrier_date','shipping_limit_date','review_id', 'product_name_lenght','payment_installments', 'product_description_lenght', 'review_comment_title', 'review_comment_message', 'review_creation_date', 'review_answer_timestamp','order_item_id', 'customer_id'])

import copy


final_df_capped = copy.deepcopy(final_df_filtered)

def capping_outlier(col):
    
    lwr_limit = final_df_capped[col].quantile(0.03)
    upr_limit = final_df_capped[col].quantile(0.97)

    print(str(col).upper())
    print("lwr:", lwr_limit, "upr:", upr_limit)
    print()
    
    final_df_capped[col] = np.where(final_df_capped[col]> upr_limit, upr_limit, 
               
                                    np.where(final_df_capped[col]< lwr_limit, lwr_limit, final_df_capped[col]))
outlier_col = ['price', 'freight_value', 'payment_value']

for col in outlier_col:
    capping_outlier(col)
#final_df_clean
final_df_clean = copy.deepcopy(final_df_capped)

#dropping the last month to have a clean visulization
final_df_clean['order_month'] = final_df_clean['order_purchase_timestamp'].dt.to_period('M')
monthly_orders = final_df_clean.groupby('order_month').size().iloc[:-1] 

#1. Fig. Monthly Orders Volume
plt.figure(figsize=(12,6))
monthly_orders.plot()
plt.title('Monthly Orders Volume')
plt.ylabel('Number of Orders')
plt.show()

#2. Fig. Customer Distribution by State
state_counts = final_df_clean['customer_state'].value_counts().reset_index()
state_counts.columns = ['State', 'Customer Count']

fig=px.bar(
    state_counts,
    x='State',
    y='Customer Count',
    title='Customer Distribution by State',
    labels={'State': 'State', 'Customer Count': 'Customer Count'},
    color='State',
    text='Customer Count')

fig.update_layout(
    title_font_size=20,
    xaxis_title='State',
    yaxis_title='Number of Customers',
    showlegend=False,
    plot_bgcolor='white',
    height=600,
    width=1000)

fig.update_xaxes(tickangle=45)
fig.show()

#3. Fig. Monthly Revenues by Top Five Cities
sales_by_state = final_df_clean.groupby('customer_state').agg({'price':'sum', 'order_id': 'nunique'}).rename(columns={'order_id':'order_count', 'price':'total_revenue'})

print('\nTop 10 Sales by State:')
print(sales_by_state.sort_values('total_revenue', ascending=False).head(10))

final_df_filtered['order_month'] = final_df_filtered['order_purchase_timestamp'].dt.to_period('M')

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

city_abbreviations = {city: city[:2].upper() for city in top_cities}

filtered_df = final_df_filtered[final_df_filtered['customer_city'].isin(top_cities)].copy()

filtered_df['city_abbr'] = filtered_df['customer_city'].map(city_abbreviations)

filtered_df['order_month'] = filtered_df['order_month'].astype(str)

df = (
    filtered_df
    .groupby(['city_abbr', 'customer_city', 'order_month'])['revenue']
    .sum()
    .reset_index()
)

fig = px.bar(
    df,
    x="city_abbr",
    y="revenue",
    color="customer_city",  
    animation_frame="order_month",
    hover_name="customer_city",
    title="<b>Monthly Revenue by Top 10 Cities</b>",
    labels={
        "city_abbr": "City",
        "revenue": "Total Revenue (R$)",
        "order_month": "Month",
        "customer_city": "City" 
    }
)

fig.update_layout(
    title={'x': 0.5, 'font': {'size': 24}},
    xaxis_title="<b>City</b>",
    yaxis_title="<b>Total Revenue (R$)</b>",
    plot_bgcolor='white',
    height=600,
    width=1000,
    hovermode='closest',
    updatemenus=[{
        'buttons': [
            {
                'args': [None, {'frame': {'duration': 500, 'redraw': True}, 'fromcurrent': True}],
                'label': '▶ Play',
                'method': 'animate'
            },
            {
                'args': [[None], {'frame': {'duration': 0, 'redraw': True}, 'mode': 'immediate', 'transition': {'duration': 0}}],
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
        x=1.02,
        title_text="City"  
    )
)

fig.update_xaxes(tickangle=45)
fig.update_yaxes(tickprefix="R$", gridcolor='lightgrey')

fig.update_traces(
    hovertemplate="<b>%{customdata[1]}</b><br>Month: %{frame.name}<br>Revenue: R$ %{y:,.2f}<extra></extra>",
    customdata=df[['order_month', 'customer_city']]
)

fig.show()

#4. Fig. Top Ten Categories by Orders and Monetary

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

fig = make_subplots(rows=1, cols=2, subplot_titles=(
    "Top 10 Product Categories by Orders",
    "Top 10 Product Categories by Monetary Value"
))

fig.add_trace(
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

fig.add_trace(
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

fig.update_layout(
    height=600,
    width=1150,
    showlegend=False,
    title_text="Top 10 Product Categories by Orders and Monetary Value",
    title_x=0.5,
    plot_bgcolor='white',
    margin=dict(t=70)
)

fig.update_yaxes(autorange="reversed", row=1, col=1)
fig.update_yaxes(autorange="reversed", row=1, col=2)

fig.show()

#5. Fig. Review Score Distribution
final_df_clean
print("\nReview Scores Distribution (% of total):")
print((final_df_clean['review_score'].value_counts(normalize=True) * 100).round(2))

review_scores_distribution = (final_df_clean['review_score'].value_counts(normalize=True) * 100).round(2)

plt.figure(figsize=(8, 8))
colors = sns.color_palette('pastel')[0:5]
plt.pie(review_scores_distribution, labels=review_scores_distribution.index, autopct='%1.1f%%', colors=colors, startangle=90)
plt.gca().add_artist(plt.Circle((0, 0), 0.70, fc='white'))  
plt.title('Review Scores Distribution')
plt.show()

#6. Fig. Actual Delivery Time
final_df_clean['actual_delivery_days']=(final_df_clean['order_delivered_customer_date']-final_df_clean['order_purchase_timestamp']).dt.days
final_df_clean['estimated_delivery_days']=(final_df_clean['order_estimated_delivery_date']-final_df_clean['order_purchase_timestamp']).dt.days
final_df_clean['delivery_difference']=final_df_clean['actual_delivery_days']- final_df_clean['estimated_delivery_days']
final_df_clean['actual_delivery_days'] = final_df_clean['actual_delivery_days']
final_df_clean['delivery_difference'] = final_df_clean['delivery_difference']

print('\nDelivery Performance Summary:')
print('-' * 40)

stats = final_df_clean[['actual_delivery_days', 'estimated_delivery_days', 'delivery_difference']].describe().round(3)

print(stats.to_string(float_format='%.3f'))
print('-' * 40)

plt.figure(figsize=(12,6))
sns.histplot(final_df_clean['actual_delivery_days'].dropna(), bins=30, kde=True)
plt.title('Actual Delivery Time Distribution')
plt.show()

#7. Fig. Delivery Time vs Review Score

fig= px.scatter(final_df_clean,
                x='actual_delivery_days',
                y='review_score',
                color='review_score',
                size_max=40,
                opacity=0.6,
                title='Delivery Time vs Review Score',
                labels={
                    'actual_delivery_days': 'Actual Delivery Days',
                    'review_score': 'review_score (1-5)'
                    })

fig.add_vline(x=final_df_clean['actual_delivery_days'].median(),
              line_dash='dash', line_color='green')
fig.update_layout(
    hovermode='closest',
    xaxis_range=[0, final_df_clean['actual_delivery_days'].max()*1.1],
    yaxis_range=[0.5, 5.5],
    showlegend=False)
fig.show()

#8. Fig. Delivery Time Distribution by Month
final_df_clean = final_df_clean.sort_values(by='order_month')
final_df_clean_filtered = final_df_clean[final_df_clean['actual_delivery_days'] <= 50].copy()

max_day_count_filtered = 0
for month in final_df_clean_filtered['order_month_str'].unique():
    temp_df = final_df_clean_filtered[final_df_clean_filtered['order_month_str'] == month]
    day_counts = temp_df['actual_delivery_days'].value_counts()
    if not day_counts.empty:
        max_day_count_filtered = max(max_day_count_filtered, day_counts.max())

fig = px.histogram(
    final_df_clean_filtered,
    x="actual_delivery_days",
    animation_frame="order_month_str",
    title="Delivery Time Distribution by Month",
    opacity=0.7,
    color_discrete_sequence=["#2ca02c"], 
    range_x=[0, 50],
    range_y=[0, max_day_count_filtered * 1.1] if max_day_count_filtered > 0 else [0, 1],
    labels={'actual_delivery_days': 'Delivery Days', 'order_month_str': 'Month', 'count': 'Number of Orders'} 
)

fig.update_layout(
    xaxis_title="Delivery Days",
    yaxis_title="Number of Orders",
    bargap=0.1,  
    plot_bgcolor="rgba(245, 245, 245, 1)", 
    font_family="Arial",
    font_size=12,
    title_font_size=16,
    xaxis=dict(tickmode='linear', tick0=0, dtick=5), 
)

fig.show()


#9. Fig. Percentage of Order on Time
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
plt.title('Percentage of Orders Delivered On Time')
plt.show() 











