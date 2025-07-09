
import pandas as pd

df_6 = pd.read_csv('Data/Olist_delivery_and_volume_.csv')
df_6.info()


# In[101]:


import numpy as np

conditions = [
    df_6['prod_mean_volume'] <= 5516,
    (df_6['prod_mean_volume'] > 5516) & (df_6['prod_mean_volume'] < 16583),
    (df_6['prod_mean_volume'] >= 16583) & (df_6['prod_mean_volume'] <= 19398),
    df_6['prod_mean_volume'] > 19398
]

choices = ['XS', 'S', 'M', 'L']

df_6['product_volume_category'] = np.select(conditions, choices, default='unknown')


# In[102]:


df_6['prod_mean_volume'].describe()


# In[103]:


counts = df_6['product_category_name_english'].value_counts()
print(counts)


# In[104]:


# Nicely formatted average reviews
average_review = (
    df_6.groupby('delivery_time_category')['review_score']
    .mean()
    .round(2)       # Round to 2 decimals
    .sort_values()  # Sort by average review
)

print(average_review)


# In[106]:


# Group by delivery_time_category and calculate mean and count
review_stats = (
    df_6.groupby('delivery_time_category')['review_score']
    .agg(
        average_review='mean',
        number_of_reviews='count'
    )
)

# Calculate percentage of reviews
review_stats['percentage_of_reviews'] = (
    review_stats['number_of_reviews'] / review_stats['number_of_reviews'].sum() * 100
).round(2)

# Round average review to 2 decimal places
review_stats['average_review'] = review_stats['average_review'].round(2)

# Optional: Drop the absolute count if you don’t need it
# review_stats = review_stats.drop(columns='number_of_reviews')

# Sort by average review if you like
review_stats = review_stats.sort_values(by='average_review')

# Show the result
print(review_stats)


# In[107]:


# Gruppieren nach delivery_time_category und Mittelwert + Anzahl berechnen
review_stats = (
    df_6.groupby('delivery_time_category')['review_score']
    .agg(
        average_review='mean',
        number_of_reviews='count'
    )
)

# Prozentanteil berechnen
review_stats['percentage_of_reviews'] = (
    review_stats['number_of_reviews'] / review_stats['number_of_reviews'].sum() * 100
).round(2)

# Mittelwert runden
review_stats['average_review'] = review_stats['average_review'].round(2)

# Spalte mit der Anzahl der Bewertungen entfernen
review_stats = review_stats.drop(columns='number_of_reviews')

# Nach durchschnittlicher Bewertung sortieren (optional)
review_stats = review_stats.sort_values(by='average_review')

# Ergebnis anzeigen
print(review_stats)


# In[142]:


import plotly.graph_objects as go
import pandas as pd
from matplotlib import cm

# Assume df_6 is already loaded in your environment, e.g.:
# df_6 = pd.read_csv('/mnt/data/Olist_delivery_and_volume_.csv')

# 1. Compute stats per delivery-time category
category_order = ['very early', 'early', 'on time', 'late', 'very late']
stats = (
    df_6
    .groupby('delivery_time_category', as_index=False)
    .agg(
        average_rating=('review_score', 'mean'),
        count_reviews=('review_score', 'count')
    )
)
# Calculate percentage of reviews
stats['percentage_reviews'] = stats['count_reviews'] / stats['count_reviews'].sum() * 100

# 2. Order categories
stats['delivery_time_category'] = pd.Categorical(
    stats['delivery_time_category'],
    categories=category_order,
    ordered=True
)
stats = stats.sort_values('delivery_time_category')

# 3. Generate bar colors: red for low avg, green for high avg
norm = (stats['average_rating'] - stats['average_rating'].min()) / (
    stats['average_rating'].max() - stats['average_rating'].min()
)
cmap = cm.get_cmap('RdYlGn')
bar_colors = [
    f'rgba({int(r*255)}, {int(g*255)}, {int(b*255)}, 1)'
    for r, g, b, _ in cmap(norm)
]

# 4. Create dual-axis figure
fig = go.Figure()

# Bars: average rating
for idx, row in stats.iterrows():
    fig.add_trace(go.Bar(
        x=[row['delivery_time_category']],
        y=[row['average_rating']],
        marker_color=bar_colors[idx],
        name='Avg Rating',
        showlegend=False,
        yaxis='y1'
    ))

# Line: percentage of reviews
fig.add_trace(go.Scatter(
    x=stats['delivery_time_category'],
    y=stats['percentage_reviews'],
    mode='lines+markers',
    marker=dict(color='black'),
    name='Percentage of Reviews',
    yaxis='y2'
))

# 5. Layout settings
fig.update_layout(
    title='Average Rating & Percentage of Reviews by Delivery Time Category',
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

fig.show()


# In[76]:


# Drop all rows where delivery_time_category is 'late' or 'very late'
df_8 = df_6[~df_6['delivery_time_category'].isin(['late', 'very late'])].copy()
df_8.info()


# In[91]:


top_10 = (
    df_8.groupby('product_category_name_english')
    .agg(
        average_review=('review_score', 'mean'),
        number_of_reviews=('review_score', 'count')
    )
    .query('number_of_reviews >= 30')
    .sort_values(by='average_review', ascending=False)
    .head(10)
)

top_10 = top_10.round(2).reset_index()


# In[119]:


import plotly.graph_objects as go

fig = go.Figure(data=[go.Table(
    header=dict(
        values=list(top_10.columns),
        fill_color='#40466e',
        font=dict(color='white', size=14),
        align='center'
    ),
    cells=dict(
        values=[top_10[col] for col in top_10.columns],
        fill_color='#f1f1f2',
        align='center',
        font=dict(size=12)
    )
)])

fig.update_layout(
    title='Top 10 Product Categories by Average Review (≥30 Reviews)',
    title_font_size=16,
    margin=dict(l=20, r=20, t=60, b=20),
    height=400
)

fig.show()


# In[81]:


# From df_6, excluding "unknown"
review_stats_6 = (
    df_6[df_6['product_volume_category'] != 'unknown']
    .groupby('product_volume_category', as_index=False)
    .agg(avg_review_score=('review_score', 'mean'))
)
review_stats_6['avg_review_score'] = review_stats_6['avg_review_score'].round(2)
print(review_stats_6)


# In[110]:


import plotly.express as px

# Create the filtered and grouped DataFrame
review_stats_6 = (
    df_6[df_6['product_volume_category'] != 'unknown']
    .groupby('product_volume_category', as_index=False)
    .agg(avg_review_score=('review_score', 'mean'))
)
review_stats_6['avg_review_score'] = review_stats_6['avg_review_score'].round(2)

# Plot with Plotly using a colorblind-friendly scale
fig = px.bar(
    review_stats_6,
    x='product_volume_category',
    y='avg_review_score',
    text='avg_review_score',
    title='Average Review Score by Product Volume Category',
    labels={
        'product_volume_category': 'Volume Category',
        'avg_review_score': 'Average Review Score'
    },
    color='avg_review_score',
    color_continuous_scale='Cividis'  # Colorblind-friendly!
)

fig.update_traces(textposition='outside')
fig.update_layout(
    yaxis=dict(range=[0, 5]),
    uniformtext_minsize=8,
    uniformtext_mode='hide',
    plot_bgcolor='white',
    height=400
)

fig.show()


# In[112]:


# From df_8, excluding "unknown"
review_stats_8 = (
    df_8[df_8['product_volume_category'] != 'unknown']
    .groupby('product_volume_category', as_index=False)
    .agg(avg_review_score=('review_score', 'mean'))
)
review_stats_8['avg_review_score'] = review_stats_8['avg_review_score'].round(2)


# In[113]:


import plotly.express as px

# Create the filtered and grouped DataFrame
review_stats_8 = (
    df_8[df_8['product_volume_category'] != 'unknown']
    .groupby('product_volume_category', as_index=False)
    .agg(avg_review_score=('review_score', 'mean'))
)
review_stats_8['avg_review_score'] = review_stats_8['avg_review_score'].round(2)

# Plot with Plotly using a colorblind-friendly scale
fig = px.bar(
    review_stats_8,
    x='product_volume_category',
    y='avg_review_score',
    text='avg_review_score',
    title='Average Review Score by Product Volume Category',
    labels={
        'product_volume_category': 'Volume Category',
        'avg_review_score': 'Average Review Score'
    },
    color='avg_review_score',
    color_continuous_scale='Cividis'  # Colorblind-friendly!
)

fig.update_traces(textposition='outside')
fig.update_layout(
    yaxis=dict(range=[0, 5]),
    uniformtext_minsize=8,
    uniformtext_mode='hide',
    plot_bgcolor='white',
    height=400
)

fig.show()


# In[126]:


# From df_6, excluding "unknown"
review_stats_6 = (
    df_6[df_6['product_volume_category'] != 'unknown']
    .groupby('product_volume_category', as_index=False)
    .agg(avg_review_score=('review_score', 'mean'))
)
review_stats_6['avg_review_score'] = review_stats_6['avg_review_score'].round(2)

# From df_8, excluding "unknown"
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

print(review_comparison)


# In[128]:


import plotly.express as px

# Plot the differences
fig = px.bar(
    review_comparison,
    x='product_volume_category',
    y='avg_review_diff',
    text='avg_review_diff',
    title='Difference in Average Review Score (df_8 - df_6)',
    labels={
        'product_volume_category': 'Product Volume Category',
        'avg_review_diff': 'Difference in Avg Review Score'
    },
    color='avg_review_diff',
    color_continuous_scale='RdBu',
)

# Add styling
fig.update_traces(textposition='outside')
fig.update_layout(
    yaxis=dict(title='Avg Review Score Difference', zeroline=True),
    plot_bgcolor='white',
    height=470
)

fig.show()
st.plotly_chart(fig)


# In[88]:


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
print(review_stats)


# In[89]:


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
print(review_stats)



