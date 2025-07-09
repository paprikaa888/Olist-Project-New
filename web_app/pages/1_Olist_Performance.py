import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import requests
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os
import locale 

st.image("https://miro.medium.com/v2/resize:fit:4800/format:webp/1*1k72mg1_CZvLptX77zzKTg.png")

customers = pd.read_csv('./download/olistbr_brazilian-ecommerce/olist_customers_dataset.csv', sep=",")
locations = pd.read_csv('./download/olistbr_brazilian-ecommerce/olist_geolocation_dataset.csv', sep=",")
order_items = pd.read_csv('./download/olistbr_brazilian-ecommerce/olist_order_items_dataset.csv', sep=",")
order_payments = pd.read_csv('./download/olistbr_brazilian-ecommerce/olist_order_payments_dataset.csv', sep=",")
order_reviews = pd.read_csv('./download/olistbr_brazilian-ecommerce/olist_order_reviews_dataset.csv', sep=",")
orders = pd.read_csv('./download/olistbr_brazilian-ecommerce/olist_orders_dataset.csv', sep=",")
products = pd.read_csv('./download/olistbr_brazilian-ecommerce/olist_products_dataset.csv', sep=",")
sellers = pd.read_csv('./download/olistbr_brazilian-ecommerce/olist_sellers_dataset.csv', sep=",")
product_category_name = pd.read_csv('./download/olistbr_brazilian-ecommerce/product_category_name_translation.csv', sep=",")

order_items = order_items.merge(orders[['order_id', 'order_purchase_timestamp']], on='order_id', how='left')
if 'order_purchase_timestamp_x' in order_items.columns:
    order_items.rename(columns={'order_purchase_timestamp_x': 'order_purchase_timestamp'}, inplace=True)
order_items['order_purchase_timestamp'] = pd.to_datetime(order_items['order_purchase_timestamp'])
order_items['year'] = order_items['order_purchase_timestamp'].dt.year
order_items['gmv'] = order_items['price'] * order_items['order_item_id']
gmv_by_year = order_items.groupby('year')['gmv'].sum().loc[2016:2018].round(2)

st.header("Olist Performance Overview")
st.write("""
    This page provides an overview of the performance of Olist, a Brazilian e-commerce platform, focusing on the growth of sellers and gross merchandise value (GMV) from 2016 to 2018.
    The data highlights the significant increase in both the number of sellers and GMV during this period, indicating a thriving e-commerce environment.
    """)

DATA_DIR = '.'
EUR_EXCHANGE_RATE = 0.15
DATA_FILES = {
    "orders": os.path.join(DATA_DIR, 'olist_orders_dataset.csv'),
    "order_payments": os.path.join(DATA_DIR, 'olist_order_payments_dataset.csv')
}

try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'English_United States.1252')
    except locale.Error:
        st.warning("Konnte kein passendes Locale für Tausendertrennzeichen setzen. Zahlen könnten ohne Trennzeichen erscheinen.")


DATA_DIR = '.'
EUR_EXCHANGE_RATE = 0.15
DATA_FILES = {
    "orders": os.path.join(DATA_DIR, '../data/olist_orders_dataset.csv'),
    "order_payments": os.path.join(DATA_DIR, '../data/olist_order_payments_dataset.csv')
}

def load_data(file_paths_dict):
    loaded_data = {}
    try:
        loaded_data["orders"] = pd.read_csv(file_paths_dict["orders"])
        loaded_data["order_payments"] = pd.read_csv(file_paths_dict["order_payments"])
        return loaded_data
    except FileNotFoundError as e:
        st.error(f"ERROR: File not found: {e}. Ensure CSVs are in the directory.")
        return None
    except Exception as e:
        st.error(f"ERROR reading files: {e}")
        return None

def preprocess_revenue_data(orders_df, payments_df):
    try:
        merged_df = pd.merge(
            orders_df[['order_id', 'order_purchase_timestamp']],
            payments_df[['order_id', 'payment_value']],
            on='order_id',
            how='inner'
        )
        merged_df['order_purchase_timestamp'] = pd.to_datetime(merged_df['order_purchase_timestamp'], errors='coerce')
        merged_df.dropna(subset=['order_purchase_timestamp', 'payment_value'], inplace=True)
        merged_df = merged_df[merged_df['payment_value'] > 0]
        if merged_df.empty:
            st.error("No valid data after cleaning.")
            return None
        merged_df['year'] = merged_df['order_purchase_timestamp'].dt.year
        return merged_df
    except Exception as e:
        st.error(f"ERROR during data preprocessing: {e}")
        return None

def calculate_yearly_revenue(processed_data, exchange_rate):
    try:
        yearly_revenue = processed_data.groupby('year')['payment_value'].sum().reset_index()
        yearly_revenue.rename(columns={'payment_value': 'revenue_brl'}, inplace=True)
        yearly_revenue['revenue_eur'] = (yearly_revenue['revenue_brl'] * exchange_rate).round(2)
        if yearly_revenue.empty:
             st.warning("No yearly revenue data calculated.")
             return None
        return yearly_revenue
    except Exception as e:
        st.error(f"ERROR calculating yearly revenue: {e}")
        return None

def create_eur_revenue_plot(yearly_revenue_df):
    """Creates ONLY the plot for EUR revenue (in English) and returns the figure."""
    if yearly_revenue_df is None or yearly_revenue_df.empty:
        st.warning("No data available for plotting.")
        return None

    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        years = yearly_revenue_df['year']
        revenue_eur = yearly_revenue_df['revenue_eur']
        bars_eur = ax.bar(years, revenue_eur, color="blue", alpha=0.8)

        ax.set_xlabel("Year")
        ax.set_ylabel("Revenue (EUR)")
        ax.set_title(f"Yearly Revenue (EUR, Rate: {EUR_EXCHANGE_RATE})", fontweight="bold")

        ax.set_xticks(years)
        ax.set_xticklabels(years.astype(str))
        ax.ticklabel_format(style='plain', axis='y')

        for bar in bars_eur:
             height = bar.get_height()
             try:
                 label_text = locale.format_string("€ %.2f", height, grouping=True)
             except NameError:
                 label_text = f"€ {height:,.2f}"

             ax.annotate(label_text,
                         xy=(bar.get_x() + bar.get_width() / 2, height),
                         xytext=(0, 3),
                         textcoords="offset points",
                         ha='center', va='bottom', fontsize=8)

        plt.tight_layout()
        return fig
    except Exception as e:
        st.error(f"Error creating plot: {e}")
        return None

data = load_data(DATA_FILES)
if data:
    processed_data = preprocess_revenue_data(data['orders'], data['order_payments'])
    if processed_data is not None:
        yearly_revenue = calculate_yearly_revenue(processed_data, EUR_EXCHANGE_RATE)
        if yearly_revenue is not None:

            fig_to_show = create_eur_revenue_plot(yearly_revenue)
            if fig_to_show:
                st.pyplot(fig_to_show)
            else:
                st.warning("Plot could not be created.")

st.write("""
    The Olist marketplace has experienced significant growth in the number of sellers and gross merchandise value (GMV) over the years. The data shows a substantial increase in both metrics from 2016 to 2018, indicating a thriving e-commerce environment.
    """)
st.write("""
    The number of sellers on the Olist platform has grown from 145 in 2016 to 2383 in 2018, reflecting a remarkable increase in seller participation. This growth is accompanied by a corresponding rise in GMV, which increased from €14,703 in 2016 to €1,922,581 in 2018. This trend suggests that Olist has successfully attracted more sellers and facilitated higher sales volumes over the years.
    The data highlights the platform's ability to scale and adapt to the evolving e-commerce landscape, making it an attractive option for both sellers and buyers.
    """)
st.write("""
    The growth in the number of sellers and GMV underscores Olist's position as a key player in the Brazilian e-commerce market, providing valuable opportunities for businesses to reach a wider audience and drive sales.
    The data also suggests that Olist has effectively leveraged its marketplace model to create a win-win situation for sellers and buyers, fostering a vibrant ecosystem that benefits all stakeholders.
    """)
st.write("""
    The table below summarizes the growth of Olist sellers from 2016 to 2018:
    - **Number of Sellers**: The number of sellers on the Olist platform has increased significantly over the years, indicating a growing interest from businesses to join the marketplace.
    - **Gross Merchandise Value (GMV)**: GMV represents the total sales value of merchandise sold through the Olist platform. The increase in GMV reflects the growing popularity and success of the marketplace.
    - **Year**: The data covers the years 2016 to 2018, showcasing the growth trajectory of Olist during this period.
    """)
    
data = {
    "Year": [2016, 2017, 2018],
    "Number of Sellers": [145, 1784, 2383],
    "Gross Merchandise Value": ["14 703 €", "1 885 179 €", "1 922 581 €"]
}
df = pd.DataFrame(data)

st.dataframe(df.style.hide(axis="index"), use_container_width=True)

st.subheader("Estimated Profit")
st.write("""
    The estimated profit for Olist in 2018 is calculated based on the GMV and the commission rate. The commission rate is set at 10% and 15% of the GMV, which is a common practice in e-commerce platforms to generate revenue from sales made through their marketplace. 
         
    The monthly subscription fee for sellers is also included in the revenue estimation, which is set at 80 BRL per month (20 EUR).
    """)

gmv_eur = pd.Series([14703, 1885179, 1922581], index=[2016, 2017, 2018])
seller_count_by_year = pd.Series([145, 1784, 2383], index=[2016, 2017, 2018])

def estimate_profit(gmv_series, seller_series, commission_rate, subscription_fee_per_year):
    return (gmv_series * commission_rate) + (seller_series * subscription_fee_per_year)

subscription_fee = 240 
scenarios = {
    '10%': 0.10,
    '15%': 0.15
}

profit_estimates_eur = pd.DataFrame(index=gmv_eur.index)
for label, rate in scenarios.items():
    profit_estimates_eur[label] = estimate_profit(
        gmv_series=gmv_eur,
        seller_series=seller_count_by_year,
        commission_rate=rate,
        subscription_fee_per_year=subscription_fee
    ).round(0)

selected_scenario = st.selectbox(
    "Choose a commission rate scenario:",
    profit_estimates_eur.columns
)

fig = px.line(
    profit_estimates_eur,
    x=profit_estimates_eur.index,
    y=selected_scenario,
    title=f"Estimated Profit With Commission Rate: {selected_scenario}",
    markers=True,
    labels={'x': 'Year', selected_scenario: 'Estimated Profit (€)'}
)
fig.update_layout(yaxis_tickprefix="€", xaxis_title="Year", yaxis_title="Profit")

st.plotly_chart(fig, use_container_width=True)


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

st.subheader("Monthly Orders Volume")
st.write("""
    The monthly orders volume is a key metric that reflects the number of orders placed on the Olist platform each month. This data provides insights into the overall performance and growth of the marketplace over time.
    The graph below shows the monthly orders volume from 2016 to 2018, highlighting the trends and patterns in customer purchasing behavior. The data indicates a steady increase in the number of orders over the years, suggesting a growing customer base and increasing demand for products on the Olist platform.
    The monthly orders volume is calculated based on the order purchase timestamps, which are converted to a datetime format for accurate analysis. The data is then grouped by month to provide a clear view of the order trends over time.
    This metric is crucial for understanding the seasonality and fluctuations in customer demand, allowing Olist to optimize its inventory management, marketing strategies, and overall business operations.
    The graph also helps to identify peak periods of activity, which can inform promotional campaigns and resource allocation to meet customer needs effectively.
    """)
st.write("")

for col in outlier_col:
    capping_outlier(col)

final_df_clean = final_df_capped.copy()

final_df_clean['order_purchase_timestamp'] = pd.to_datetime(final_df_clean['order_purchase_timestamp'])

final_df_clean['order_month'] = final_df_clean['order_purchase_timestamp'].dt.to_period('M')
monthly_orders = final_df_clean.groupby('order_month').size().iloc[:-1]

plt.figure(figsize=(12, 6))
monthly_orders.plot()
plt.title('Monthly Orders Volume')
plt.ylabel('Number of Orders')

st.pyplot(plt)

st.subheader("Sellers Cooperation with Olist")
st.write("""
    The Olist marketplace has experienced significant growth in the number of sellers and gross merchandise value (GMV) over the years. The data shows a substantial increase in both metrics from 2016 to 2018, indicating a thriving e-commerce environment.
    The number of sellers on the Olist platform has grown from 145 in 2016 to 2383 in 2018, reflecting a remarkable increase in seller participation. This growth is accompanied by a corresponding rise in GMV, which increased from €14,703 in 2016 to €1,922,581 in 2018. This trend suggests that Olist has successfully attracted more sellers and facilitated higher sales volumes over the years.
    The data highlights the platform's ability to scale and adapt to the evolving e-commerce landscape, making it an attractive option for both sellers and buyers.
    The growth in the number of sellers and GMV underscores Olist's position as a key player in the Brazilian e-commerce market, providing valuable opportunities for businesses to reach a wider audience and drive sales.
    The data also suggests that Olist has effectively leveraged its marketplace model to create a win-win situation for sellers and buyers, fostering a vibrant ecosystem that benefits all stakeholders.
             """)

orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])
order_items_merged = order_items.merge(orders[['order_id', 'order_purchase_timestamp']], on='order_id', how='left')

seller_lifetime = order_items_merged.groupby('seller_id')['order_purchase_timestamp'].agg(['min', 'max'])
seller_lifetime['days_active'] = (seller_lifetime['max'] - seller_lifetime['min']).dt.days

fig2 = px.histogram(
    seller_lifetime,
    x='days_active',
    nbins=50,
    labels={'days_active': 'Active days'},
    template='plotly_white'
)
fig2.update_layout(
    xaxis_title='Cooperation time in days',
    yaxis_title='Numer of sellers',
    bargap=0.1
)
st.plotly_chart(fig2)


st.subheader('Olists Customers Geolocation')
st.write("""
    This section visualizes the geographical distribution of Olist customers across Brazil, providing insights into customer locations based on their zip codes. The map highlights the concentration of customers in different states, allowing for a better understanding of Olist's market reach and customer demographics.
    The map is created using Plotly's scatter_mapbox, which displays customer locations based on their latitude and longitude coordinates. Each point on the map represents a customer, with colors indicating different states. This visualization helps to identify regions with higher customer density and can inform marketing strategies and logistics planning.
    The map also includes hover information, allowing users to see the customer's city and state when hovering over a point. This interactive feature enhances the user experience and provides additional context for the geographical distribution of Olist customers.
    The audio clip of "Minas Gerais" adds a cultural touch to the visualization, connecting the data to the Brazilian context and enhancing the overall presentation.
    """)

df_6 = pd.read_csv('../Data/Olist_delivery_and_volume_.csv')

df_7= pd.read_csv('../Data/Olist_geolocation_dataset.csv')

df_7_unique = df_7.drop_duplicates(
    subset='geolocation_zip_code_prefix',
    keep='first'
)

df_9 = pd.read_csv('../Data/olist_customers_dataset.csv')

df_10 = pd.read_csv('../Data/olist_orders_dataset.csv')

df_11= df_10.merge(df_9, on='customer_id', how='left')

df_12 = df_11.merge(
    df_7_unique,
    how='left',
    left_on='customer_zip_code_prefix',
    right_on='geolocation_zip_code_prefix'
)       

df_12.to_csv('df_12.csv', index=False, encoding='utf-8')

fig3 = px.scatter_mapbox(
    df_12,
    lat='geolocation_lat',
    lon='geolocation_lng',
    color='geolocation_state',
    hover_name='customer_city',
    zoom=3,
    height=800,
    mapbox_style='open-street-map'
    )

st.plotly_chart(fig3)

st.subheader("Correct Pronounciation of Minas Gerais")

st.audio("https://github.com/paprikaa888/audio-hosting/raw/refs/heads/main/Minas_Gerais.mp3")


df_13= pd.read_csv('../Data/olist_order_items_dataset.csv')

df_14 = df_12.merge(
    df_13,
    how='left',
    left_on='order_id',
    right_on='order_id'
)       

df_14.to_csv('../Olist_geo_orders.csv', index=False, encoding='utf-8')

df = pd.read_csv('../Olist_geo_orders.csv')

df = df.dropna(subset=['geolocation_lat', 'geolocation_lng', 'price', 'geolocation_state'])

df_state = (
    df
    .groupby('geolocation_state')
    .agg(
        total_price=('price', 'sum'),
        lat=('geolocation_lat', 'mean'),
        lon=('geolocation_lng', 'mean'),
        order_count=('order_id', 'nunique')
    )
    .reset_index()
)

df = df.dropna(subset=['geolocation_lat', 'geolocation_lng', 'price', 'geolocation_state'])

df_state = (
    df
    .groupby('geolocation_state')
    .agg(
        total_price=('price', 'sum'),
        lat=('geolocation_lat', 'mean'),
        lon=('geolocation_lng', 'mean'),
        order_count=('order_id', 'nunique')
    )
    .reset_index()
)

df = df.dropna(subset=['geolocation_state', 'price'])

df_state = (
    df
    .groupby('geolocation_state')
    .agg(total_price=('price', 'sum'),
         order_count=('order_id', 'nunique'))
    .reset_index()
)


geojson_url = (
    'https://raw.githubusercontent.com/'
    'codeforgermany/click_that_hood/master/'
    'public/data/brazil-states.geojson'
)
brazil_states = requests.get(geojson_url).json()

df = df.dropna(subset=['geolocation_state', 'price'])

df_state = (
    df
    .groupby('geolocation_state')
    .agg(total_price=('price', 'sum'))
    .reset_index()
)

geojson_url = (
    'https://raw.githubusercontent.com/'
    'codeforgermany/click_that_hood/master/'
    'public/data/brazil-states.geojson'
)
brazil_states = requests.get(geojson_url).json()

df = df.dropna(subset=['geolocation_state', 'price'])

df_state = (
    df.groupby('geolocation_state')
      .agg(total_price=('price', 'sum'))
      .reset_index()
)

geojson_url = (
    'https://raw.githubusercontent.com/'
    'codeforgermany/click_that_hood/master/'
    'public/data/brazil-states.geojson'
)
brazil_states = requests.get(geojson_url).json()

all_states = [feat['properties']['sigla'] for feat in brazil_states['features']]
df_all = pd.DataFrame({'geolocation_state': all_states})
df_state = (
    df_all
    .merge(df_state, on='geolocation_state', how='left')
    .fillna({'total_price': 0})
)

st.subheader("Olist's Order Value by Revenue")
st.write("""
    The map below shows the total order value by state in Brazil, providing insights into the distribution of sales across different regions. The color intensity represents the total order value, allowing for a quick visual assessment of which states contribute most to Olist's revenue.
    """)

fig4 = px.choropleth(
    df_state,
    geojson=brazil_states,
    locations='geolocation_state',
    featureidkey='properties.sigla',
    color='total_price',
    color_continuous_scale='Viridis',
    hover_name='geolocation_state',
    labels={'total_price': 'Order Value (BRL)'},
    scope='south america',
)


fig4.update_geos(
    visible=False,
    showcountries=True,
    countrycolor='gray',
    showsubunits=True,
    subunitcolor='lightgray'
)

fig4.update_layout(
    margin={"r":50, "t":50, "l":50, "b":50},
    coloraxis_colorbar=dict(
        title="Order Value (BRL)",
        tickprefix="R$ ",
    ),
    legend=dict(
        x=1.05,
        y=0.5,
        xanchor="left",
        yanchor="middle",
        title_text="Legend"
    ),
    width=1200,
    height=800
)

st.plotly_chart(fig4)