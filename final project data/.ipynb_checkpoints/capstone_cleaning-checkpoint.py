#!/usr/bin/env python
# coding: utf-8

# In[60]:


import pandas as pd
import numpy as np
import seaborn as sb
sb.set()
import datetime as dt
import matplotlib.pyplot as plt


# In[61]:


customers = pd.read_csv('./archive/olist_customers_dataset.csv', sep=",")
locations = pd.read_csv('./archive/olist_geolocation_dataset.csv', sep=",")
order_items = pd.read_csv('./archive/olist_order_items_dataset.csv', sep=",")
order_payments = pd.read_csv('./archive/olist_order_payments_dataset.csv', sep=",")
order_reviews = pd.read_csv('./archive/olist_order_reviews_dataset.csv', sep=",")
orders = pd.read_csv('./archive/olist_orders_dataset.csv', sep=",")
products = pd.read_csv('./archive/olist_products_dataset.csv', sep=",")
sellers = pd.read_csv('./archive/olist_sellers_dataset.csv', sep=",")
product_category_name = pd.read_csv('./archive/product_category_name_translation.csv', sep=",")


# # Ich "merge" Schritt für Schritt alle dataframes zu einem großen dataframe zusammen:

# In[62]:


merged_df1 = pd.merge(order_items, orders, on='order_id', how='left')
merged_df2 = pd.merge(merged_df1, customers, on='customer_id', how='left')
merged_df3 = pd.merge(merged_df2, order_payments, on='order_id', how='left')
merged_df4 = pd.merge(merged_df3, order_reviews, on='order_id', how='left')
merged_df5 = pd.merge(merged_df4, products, on='product_id', how='left')
merged_df6 = pd.merge(merged_df5, product_category_name, on='product_category_name', how='left')
final_df = pd.merge(merged_df6, sellers, on='seller_id', how='left')


# In[11]:


pd.set_option('display.max_columns', None)  # Zeige alle Spalten
pd.set_option('display.expand_frame_repr', False)  # Verhindere Zeilenumbruch


# In[12]:


# der data frame behinhaltet jetzt die Infos aus allen 7 csv dateien


# In[ ]:





# In[63]:


# Jetzt folgt der Data Cleaning Prozess. Suche nach fehlenden Werten (missing values) und oder doppelten werten (duplicates)


# In[64]:


missing_values = final_df.isnull().sum()
missing_values


# In[65]:


# Da Anzeige zu groß möchte ich mir nur die Spalten zeigen lassen in denen er null werte gib!


# In[66]:


missing_values = final_df.isnull().sum()
missing_values = missing_values[missing_values > 0]
print(missing_values)


# In[67]:


duplicates_count = final_df['review_comment_title'].value_counts()
duplicates = duplicates_count[duplicates_count > 1]
print(duplicates)


# In[68]:


## Möchte nur die Spalten sehen die duplicates enhalten!


# In[69]:


duplicates = final_df.apply(lambda x: x.duplicated().sum())
duplicates = duplicates[duplicates > 0]

for col, count in duplicates.items():
    print(f"Spalte: {col} → {count} Duplikate")


# In[70]:


# Manche Duplikate wie zB Preis etc. können drin bleiben.

# Dopplungen  wie Bestell-ID, der Kunden-ID, dem Zeitstempel der Bestellung und dem Datum der Bestellung sollen uter Beibehaltung der ersten gelöscht werden!


# In[71]:


final_df = final_df.drop_duplicates(
    subset=['order_id', 'customer_id', 'order_purchase_timestamp', 'order_delivered_customer_date'],
    keep='first'
)


# In[ ]:





# In[72]:


# Jetzt: Missing values auffüllen:


# In[ ]:





# 
# 
# Folgender Code wählt die Spalte review_comment_message aus dem DataFrame final_df
# Verwendet die fillna()-Methode, um alle NaN-Werte durch "nao_reveja" zu ersetzen
#  Weist die geänderte Spalte wieder der ursprünglichen Spalte zu

# In[73]:


final_df['review_comment_message'] = final_df['review_comment_message'].fillna('nao_reveja')


# In[ ]:





# Jetzt: missing values in den anderen Spalten mit dem jeweiligen Median auffüllen:

# In[74]:


final_df['product_weight_g'].fillna(final_df['product_weight_g'].median(), inplace=True)
final_df['product_length_cm'].fillna(final_df['product_length_cm'].median(), inplace=True)
final_df['product_height_cm'].fillna(final_df['product_height_cm'].median(), inplace=True)
final_df['product_width_cm'].fillna(final_df['product_width_cm'].median(), inplace=True)


# In[ ]:





# In[ ]:





# # Es gibt aber noch mehr missing values!!!!!!!!!!!!
# 

# In[75]:


#droppen von spalten die wir nicht brauchen!


# In[76]:


final_df = final_df.drop(columns=['shipping_limit_date','product_category_name', 
                                          'payment_installments','review_creation_date', 'review_answer_timestamp',])


# In[77]:


# sum all missing value in dataset and keep only columns with missing value > 0:


# In[78]:


nan_col = final_df.isnull().sum()[final_df.isnull().sum() > 0]


# In[79]:


# Erstelle einen datafram der aus der summe aller missing values pro spalte bestent und dem prozentualen Anteil!


# In[80]:


nan_col_olist = pd.DataFrame({'NaN_count': nan_col, 'NaN_percentage': nan_col / 
                              len(final_df) * 100}).sort_values(by = 'NaN_percentage', ascending = False)


# In[81]:


nan_col_olist


# In[82]:


# payment_sequential, payment_type, payment_value können als "Missing Value Completely at Random" angesehen werden!


# In[83]:


final_df.dropna(subset=['payment_sequential'], inplace = True)
final_df.dropna(subset=['payment_type'], inplace = True)
final_df.dropna(subset=['payment_value'], inplace = True)


# In[84]:


# beim review_score wird der Modus als Füllwert benutzt:


# In[85]:


# Find mode in review_score columns:


# In[86]:


rev_score_mode = final_df['review_score'].mode()[0]


# In[87]:


# input missing value host_response_time dengan modus


# In[88]:


final_df['review_score'].fillna(rev_score_mode, inplace=True)


# In[89]:


# droppen von review_comment_title, product_name_lenght, review_id weil nicht wichtig für Analyse


# In[90]:


final_df = final_df.drop(columns=['review_comment_title','product_name_lenght', 
                                          'review_id'])


# In[91]:


# Nullwerte in product_category_name_english mit füllwort "unknown" ausfüllen:


# In[92]:


final_df['product_category_name_english'] = final_df['product_category_name_english'].fillna('unknown')


# In[93]:


# fill out with 0 (zero) product_photos_qty


# In[94]:


final_df['product_photos_qty'] = final_df['product_photos_qty'].fillna(0)


# In[95]:


# drop von product_description_lenght


# In[96]:


final_df.dropna(subset=['product_description_lenght'], inplace = True)


# In[97]:


final_df.isnull().sum()


# In[ ]:





# In[ ]:





# In[98]:


#Datentyp ändern von Spalten mit Datum:


# In[99]:


#Change Data Type
final_df['order_purchase_timestamp'] = pd.to_datetime(final_df['order_purchase_timestamp'])
final_df['order_approved_at'] = pd.to_datetime(final_df['order_approved_at'])
final_df['order_delivered_carrier_date'] = pd.to_datetime(final_df['order_delivered_carrier_date'])
final_df['order_delivered_customer_date'] = pd.to_datetime(final_df['order_delivered_customer_date'])
final_df['order_estimated_delivery_date'] = pd.to_datetime(final_df['order_estimated_delivery_date'])

