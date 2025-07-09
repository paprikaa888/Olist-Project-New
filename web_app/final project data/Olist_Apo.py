#!/usr/bin/env python
# coding: utf-8

# In[100]:


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


# In[118]:


import plotly.graph_objects as go
import pandas as pd
import numpy as np
from matplotlib import cm

# Reset index (if necessary)
#review_stats = review_stats.reset_index()

# Sort and set category order
category_order = ['very early', 'early', 'on time', 'late', 'very late']
review_stats['delivery_time_category'] = pd.Categorical(
    review_stats['delivery_time_category'],
    categories=category_order,
    ordered=True
)
review_stats = review_stats.sort_values('delivery_time_category')

# Normalize scores for color mapping (between 0 and 1)
norm_scores = (review_stats['average_review'] - review_stats['average_review'].min()) / \
              (review_stats['average_review'].max() - review_stats['average_review'].min())

# Get colors from red-yellow-green colormap (using matplotlib's colormap)
cmap = cm.get_cmap('RdYlGn')
colors = [f'rgba({int(r*255)}, {int(g*255)}, {int(b*255)}, 1)' for r, g, b, _ in cmap(norm_scores)]

# Plot
fig = go.Figure()

# Bar chart with gradient color
for i, row in review_stats.iterrows():
    fig.add_trace(go.Bar(
        x=[row['delivery_time_category']],
        y=[row['average_review']],
        name=row['delivery_time_category'],
        marker_color=colors[i],
        yaxis='y1',
        showlegend=False
    ))

# Line chart for percentage of reviews
fig.add_trace(go.Scatter(
    x=review_stats['delivery_time_category'],
    y=review_stats['percentage_of_reviews'],
    name='Prozentanteil der Bewertungen',
    mode='lines+markers',
    marker_color='black',
    yaxis='y2'
))

# Layout
fig.update_layout(
    title='Average rating & Percentile per delivery time category',
    xaxis_title='Lieferzeit-Kategorie',
    yaxis=dict(
        title=dict(
            text='Average rating',
            font=dict(color='black')
        ),
        range=[1, 5],
        showgrid=False,
        tickfont=dict(color='black')
    ),
    yaxis2=dict(
        title=dict(
            text='Prozentanteil der Bewertungen (%)',
            font=dict(color='black')
        ),
        overlaying='y',
        side='right',
        range=[0, 100],
        tickfont=dict(color='black')
    ),
    legend=dict(x=0.5, xanchor='center', y=-0.2, orientation='h'),
    bargap=0.4,
    template='plotly_white',
    height=500
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


# In[ ]:




