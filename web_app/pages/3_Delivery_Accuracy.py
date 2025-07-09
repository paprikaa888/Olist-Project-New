import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from matplotlib import cm

st.image("https://miro.medium.com/v2/resize:fit:4800/format:webp/1*1k72mg1_CZvLptX77zzKTg.png")

df_6 = pd.read_csv('../Data/Olist_delivery_and_volume_.csv')

conditions = [
    df_6['prod_mean_volume'] <= 5516,
    (df_6['prod_mean_volume'] > 5516) & (df_6['prod_mean_volume'] < 16583),
    (df_6['prod_mean_volume'] >= 16583) & (df_6['prod_mean_volume'] <= 19398),
    df_6['prod_mean_volume'] > 19398
]

choices = ['XS', 'S', 'M', 'L']

df_6['product_volume_category'] = np.select(conditions, choices, default='unknown')

df_6['prod_mean_volume'].describe()

counts = df_6['product_category_name_english'].value_counts()

average_review = (
    df_6.groupby('delivery_time_category')['review_score']
    .mean()
    .round(2)
    .sort_values()
)


review_stats = (
    df_6.groupby('delivery_time_category')['review_score']
    .agg(
        average_review='mean',
        number_of_reviews='count'
    )
)

review_stats['percentage_of_reviews'] = (
    review_stats['number_of_reviews'] / review_stats['number_of_reviews'].sum() * 100
).round(2)

review_stats['average_review'] = review_stats['average_review'].round(2)


review_stats = review_stats.sort_values(by='average_review')

review_stats = (
    df_6.groupby('delivery_time_category')['review_score']
    .agg(
        average_review='mean',
        number_of_reviews='count'
    )
)

review_stats['percentage_of_reviews'] = (
    review_stats['number_of_reviews'] / review_stats['number_of_reviews'].sum() * 100
).round(2)

review_stats['average_review'] = review_stats['average_review'].round(2)

review_stats = review_stats.drop(columns='number_of_reviews')

review_stats = review_stats.sort_values(by='average_review')

category_order = ['very early', 'early', 'on time', 'late', 'very late']
stats = (
    df_6
    .groupby('delivery_time_category', as_index=False)
    .agg(
        average_rating=('review_score', 'mean'),
        count_reviews=('review_score', 'count')
    )
)
stats['percentage_reviews'] = stats['count_reviews'] / stats['count_reviews'].sum() * 100

stats['delivery_time_category'] = pd.Categorical(
    stats['delivery_time_category'],
    categories=category_order,
    ordered=True
)
stats = stats.sort_values('delivery_time_category')

norm = (stats['average_rating'] - stats['average_rating'].min()) / (
    stats['average_rating'].max() - stats['average_rating'].min()
)
cmap = cm.get_cmap('RdYlGn')
bar_colors = [
    f'rgba({int(r*255)}, {int(g*255)}, {int(b*255)}, 1)'
    for r, g, b, _ in cmap(norm)
]

st.write("## Delivery Accuracy and Customer Ratings")

st.write(
    "This section provides insights into how delivery times impact customer ratings. "
    "We analyze the average ratings given by customers based on the delivery time categories, "
    "which are classified as 'very early', 'early', 'on time', 'late', and 'very late'. "
    "The analysis includes the average rating for each category and the percentage of total reviews that fall into each category."
)

fig = go.Figure()

st.subheader("Average Rating and Percentage of Reviews by Delivery Time Category")
st.write(
    "The following chart displays the average customer ratings and the percentage of reviews for each delivery time category. "
    "The average ratings are shown as bars, while the percentage of reviews is represented by a line graph. "
    "This visualization helps to understand how delivery performance correlates with customer satisfaction."
)

for idx, row in stats.iterrows():
    fig.add_trace(go.Bar(
        x=[row['delivery_time_category']],
        y=[row['average_rating']],
        marker_color=bar_colors[idx],
        name='Avg Rating',
        showlegend=False,
        yaxis='y1'
    ))

fig.add_trace(go.Scatter(
    x=stats['delivery_time_category'],
    y=stats['percentage_reviews'],
    mode='lines+markers',
    marker=dict(color='black'),
    name='Percentage of Reviews',
    yaxis='y2'
))

fig.update_layout(
    xaxis_title='Delivery Time Category',
    yaxis=dict(
        title='Average Rating',
        range=[1, 5],
        showgrid=False
    ),
    yaxis2=dict(
        title='Percentage of Reviews (%)',
        overlaying='y',
        side='right',
        range=[0, 60]
    ),
    bargap=0.2,
    template='plotly_white',
    height=500,
    legend=dict(x=0.5, y=-0.2, orientation='h', xanchor='center')
)

st.plotly_chart(fig)

st.subheader("Top 10 Product Categories by Average Review Score")
st.write("This visual compares two snapshots of the top-rated product categories based on average customer reviews and number of reviews. Books and Small appliances consistently rank high in both lists. New entries like Furniture bedroom and Musical instruments appear in the updated data. Minor shifts in average ratings and review counts suggest changes in customer sentiment or data updates.")

st.write("")
st.write("")
st.write("")
st.write("")

st.image('images/New_Top_10.png', caption="Top 10 Product Categories by Average Review Score", use_container_width=True)
df_8 = df_6[~df_6['delivery_time_category'].isin(['late', 'very late'])].copy()


review_stats_6 = (
    df_6[df_6['product_volume_category'] != 'unknown']
    .groupby('product_volume_category', as_index=False)
    .agg(avg_review_score=('review_score', 'mean'))
)
review_stats_6['avg_review_score'] = review_stats_6['avg_review_score'].round(2)

review_stats_6 = (
    df_6[df_6['product_volume_category'] != 'unknown']
    .groupby('product_volume_category', as_index=False)
    .agg(avg_review_score=('review_score', 'mean'))
)
review_stats_6['avg_review_score'] = review_stats_6['avg_review_score'].round(2)

fig3 = px.bar(
    review_stats_6,
    x='product_volume_category',
    y='avg_review_score',
    text='avg_review_score',
    labels={
        'product_volume_category': 'Volume Category',
        'avg_review_score': 'Average Review Score'
    },
    color='avg_review_score',
    color_continuous_scale='Cividis'
)

fig3.update_traces(textposition='outside')
fig3.update_layout(
    yaxis=dict(range=[0, 5]),
    uniformtext_minsize=8,
    uniformtext_mode='hide',
    plot_bgcolor='white',
    height=400
)

st.subheader("Average Review Score by Product Volume Category With Late Deliveries")
st.write("This chart shows the average review scores for different product volume categories, including those with late deliveries. The scores are color-coded to enhance visibility and understanding of customer satisfaction across various product categories.")
st.plotly_chart(fig3)

review_stats_8 = (
    df_8[df_8['product_volume_category'] != 'unknown']
    .groupby('product_volume_category', as_index=False)
    .agg(avg_review_score=('review_score', 'mean'))
)
review_stats_8['avg_review_score'] = review_stats_8['avg_review_score'].round(2)

review_stats_8 = (
    df_8[df_8['product_volume_category'] != 'unknown']
    .groupby('product_volume_category', as_index=False)
    .agg(avg_review_score=('review_score', 'mean'))
)
review_stats_8['avg_review_score'] = review_stats_8['avg_review_score'].round(2)

fig4 = px.bar(
    review_stats_8,
    x='product_volume_category',
    y='avg_review_score',
    text='avg_review_score',
    labels={
        'product_volume_category': 'Volume Category',
        'avg_review_score': 'Average Review Score'
    },
    color='avg_review_score',
    color_continuous_scale='Cividis'
)

fig4.update_traces(textposition='outside')
fig4.update_layout(
    yaxis=dict(range=[0, 5]),
    uniformtext_minsize=8,
    uniformtext_mode='hide',
    plot_bgcolor='white',
    height=400
)

st.subheader("Average Review Score by Product Volume Category Without Late Deliveries")
st.write("This chart shows the average review scores for different product volume categories, excluding late deliveries. The scores are color-coded to enhance visibility and understanding of customer satisfaction across various product categories.")

st.plotly_chart(fig4)

review_stats_6 = (
    df_6[df_6['product_volume_category'] != 'unknown']
    .groupby('product_volume_category', as_index=False)
    .agg(avg_review_score=('review_score', 'mean'))
)
review_stats_6['avg_review_score'] = review_stats_6['avg_review_score'].round(2)

review_stats_8 = (
    df_8[df_8['product_volume_category'] != 'unknown']
    .groupby('product_volume_category', as_index=False)
    .agg(avg_review_score=('review_score', 'mean'))
)
review_stats_8['avg_review_score'] = review_stats_8['avg_review_score'].round(2)

review_comparison = review_stats_6.merge(
    review_stats_8,
    on='product_volume_category',
    suffixes=('_df6', '_df8')
)

review_comparison['avg_review_diff'] = (
    review_comparison['avg_review_score_df8'] - review_comparison['avg_review_score_df6']
).round(2)

fig5 = px.bar(
    review_comparison,
    x='product_volume_category',
    y='avg_review_diff',
    text='avg_review_diff',
    labels={
        'product_volume_category': 'Product Volume Category',
        'avg_review_diff': 'Difference in Avg Review Score'
    },
    color='avg_review_diff',
    color_continuous_scale='RdBu',
)

fig5.update_traces(textposition='outside')
fig5.update_layout(
    yaxis=dict(title='Avg Review Score Difference', zeroline=True),
    plot_bgcolor='white',
    height=470
)
st.subheader("Difference in Average Review Score by Product Volume Category")
st.write("This chart illustrates the difference in average review scores between two datasets: one including late deliveries and the other excluding them. The color gradient helps to visualize the magnitude of change in customer satisfaction across different product volume categories.")

st.plotly_chart(fig5)


review_stats = (
    df_6.groupby('product_volume_category', as_index=False)
        .agg(
            avg_review_score=('review_score', 'mean'),
            review_count=('review_score', 'count')
        )
)
review_stats['avg_review_score'] = review_stats['avg_review_score'].round(2)
review_stats['percentage'] = (review_stats['review_count'] / review_stats['review_count'].sum()) * 100
review_stats['percentage'] = review_stats['percentage'].round(2)

review_stats = (
    df_8.groupby('product_volume_category', as_index=False)
        .agg(
            avg_review_score=('review_score', 'mean'),
            review_count=('review_score', 'count')
        )
)
review_stats['avg_review_score'] = review_stats['avg_review_score'].round(2)
review_stats['percentage'] = (review_stats['review_count'] / review_stats['review_count'].sum()) * 100
review_stats['percentage'] = review_stats['percentage'].round(2)



