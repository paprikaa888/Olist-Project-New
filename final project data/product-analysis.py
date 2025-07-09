#!/usr/bin/env python
# coding: utf-8

# # Produktanalyse (Olist Dataset)

# ## 1. Importieren der notwendigen Bibliotheken
# Stellen Sie sicher, dass diese Bibliotheken installiert sind:
# pip install pandas numpy plotly

import pandas as pd
import numpy as np
import plotly.express as px
import os
import sys

print("Bibliotheken importiert.")

# ## 2. Konstanten und Konfiguration
N_TOP = 20  # Anzahl der Top-Produkte/Kategorien, die angezeigt werden sollen
DATA_DIR = '.'  # Verzeichnis, in dem die CSV-Dateien erwartet werden

DATA_FILES = {
    "customers": os.path.join(DATA_DIR, 'olist_customers_dataset.csv'),
    "locations": os.path.join(DATA_DIR, 'olist_geolocation_dataset.csv'),
    "order_items": os.path.join(DATA_DIR, 'olist_order_items_dataset.csv'),
    "order_payments": os.path.join(DATA_DIR, 'olist_order_payments_dataset.csv'),
    "order_reviews": os.path.join(DATA_DIR, 'olist_order_reviews_dataset.csv'),
    "orders": os.path.join(DATA_DIR, 'olist_orders_dataset.csv'),
    "products": os.path.join(DATA_DIR, 'olist_products_dataset.csv'),
    "sellers": os.path.join(DATA_DIR, 'olist_sellers_dataset.csv'),
    "product_category_name": os.path.join(DATA_DIR, 'product_category_name_translation.csv')
}

# ## 3. Funktionen

def load_data(file_paths):
    """Lädt alle benötigten CSV-Dateien in DataFrames."""
    print("\n--- Lade Datensätze ---")
    loaded_data = {}
    all_files_loaded = True
    required_files = ['order_items', 'products', 'product_category_name'] # Mindestens benötigte Dateien

    for name, path in file_paths.items():
        try:
            loaded_data[name] = pd.read_csv(path, sep=",")
            print(f"'{path}' erfolgreich geladen.")
        except FileNotFoundError:
            print(f"FEHLER: Datei nicht gefunden: '{path}'. Bitte Pfad prüfen.")
            if name in required_files:
                all_files_loaded = False
        except Exception as e:
            print(f"FEHLER beim Laden von '{path}': {e}")
            if name in required_files:
                all_files_loaded = False

    if not all_files_loaded:
        print("\nNicht alle für die Analyse benötigten Datensätze konnten geladen werden. Skript wird beendet.")
        sys.exit(1)

    return loaded_data

def translate_categories(products_df, category_translation_df):
    """Fügt englische Kategorienamen zum 'products'-DataFrame hinzu."""
    print("\nFüge englische Kategorienamen zu 'products' hinzu...")
    try:
        if 'product_category_name_english' not in products_df.columns:
            if 'product_category_name' in products_df.columns and 'product_category_name' in category_translation_df.columns:
                # Sicherstellen, dass keine NaN im Key sind vor dem Merge
                products_df['product_category_name'] = products_df['product_category_name'].fillna('unknown_category_original')
                # Merge durchführen
                products_df = pd.merge(products_df, category_translation_df[['product_category_name', 'product_category_name_english']],
                                       on='product_category_name', how='left')
                # Fehlende Übersetzungen und ursprüngliche NaNs behandeln
                products_df['product_category_name_english'] = products_df['product_category_name_english'].fillna('unknown')
                print("'products'-DataFrame mit englischen Namen aktualisiert.")
            else:
                print("Warnung: Spalte 'product_category_name' fehlt in 'products' oder 'product_category_name_translation'. Setze Kategorie auf 'unknown'.")
                products_df['product_category_name_english'] = 'unknown'
        else:
            print("Englische Kategorienamen bereits vorhanden oder hinzugefügt.")

        # Sicherstellen, dass die Spalte existiert, auch wenn alles fehlschlug
        if 'product_category_name_english' not in products_df.columns:
             products_df['product_category_name_english'] = 'unknown'

    except KeyError as e:
        print(f"FEHLER beim Zugriff auf Spalte während der Übersetzung: {e}. Setze Kategorie auf 'unknown'.")
        products_df['product_category_name_english'] = 'unknown'
    except Exception as e:
        print(f"FEHLER beim Mergen der Kategorienamen: {e}. Setze Kategorie auf 'unknown'.")
        if 'product_category_name_english' not in products_df.columns:
             products_df['product_category_name_english'] = 'unknown'

    return products_df

def aggregate_product_sales(order_items_df):
    """Aggregiert Verkaufsdaten pro Produkt."""
    print("\nAggregiere Verkaufsdaten pro Produkt...")
    try:
        product_sales_summary = order_items_df.groupby('product_id').agg(
            total_revenue=('price', 'sum'),
            total_units_sold=('order_item_id', 'count'), # Annahme: order_item_id zählt Vorkommen pro Produkt
            avg_selling_price=('price', 'mean'),
            number_of_orders=('order_id', 'nunique')
        ).reset_index()
        print("Aggregation abgeschlossen.")
        return product_sales_summary
    except KeyError as e:
        print(f"FEHLER bei der Aggregation: Spalte {e} nicht in 'order_items' gefunden. Aggregation fehlgeschlagen.")
        return None
    except Exception as e:
        print(f"FEHLER bei der Aggregation: {e}")
        return None

def analyze_and_plot_products(order_items_df, products_df, category_translation_df):
    """Führt die Produktanalyse durch, druckt Ergebnisse und speichert Plots."""

    # Schritt 1: Kategorien übersetzen
    products_df = translate_categories(products_df, category_translation_df)

    # Schritt 2: Verkaufsdaten aggregieren
    product_sales_summary = aggregate_product_sales(order_items_df)
    if product_sales_summary is None:
        print("Produktanalyse kann nicht fortgesetzt werden, da die Aggregation fehlschlug.")
        return

    # Schritt 3: Verkaufsdaten mit Produktinformationen verbinden
    print("\nVerbinde Verkaufsdaten mit Produktinformationen...")
    try:
        # Stelle sicher, dass die Zielspalte für den Merge existiert
        if 'product_category_name_english' not in products_df.columns:
             products_df['product_category_name_english'] = 'unknown'

        product_analysis_df = pd.merge(
            product_sales_summary,
            products_df[['product_id', 'product_category_name_english']], # Nur benötigte Spalten auswählen
            on='product_id',
            how='left')
        # Erneut sicherstellen, dass nach dem Merge keine NaNs in der Kategorie sind
        product_analysis_df['product_category_name_english'] = product_analysis_df['product_category_name_english'].fillna('unknown')
        print("Verbindung abgeschlossen.")
    except KeyError as e:
        print(f"FEHLER beim Verbinden der Daten: Spalte {e} fehlt. Analyse wird abgebrochen.")
        return
    except Exception as e:
        print(f"FEHLER beim Verbinden der Daten: {e}. Analyse wird abgebrochen.")
        return

    # Schritt 4: Top-Produkte identifizieren und ausgeben
    try:
        top_revenue_products = product_analysis_df.sort_values(by='total_revenue', ascending=False).head(N_TOP)
        top_units_products = product_analysis_df.sort_values(by='total_units_sold', ascending=False).head(N_TOP)

        print(f"\n--- Top {N_TOP} Produkte nach Gesamtumsatz ---")
        print(top_revenue_products[['product_id', 'product_category_name_english', 'total_revenue', 'total_units_sold', 'avg_selling_price']])

        print(f"\n--- Top {N_TOP} Produkte nach verkauften Einheiten ---")
        print(top_units_products[['product_id', 'product_category_name_english', 'total_units_sold', 'total_revenue', 'avg_selling_price']])
    except KeyError as e:
        print(f"FEHLER bei der Identifizierung der Top-Produkte: Spalte {e} fehlt.")
    except Exception as e:
        print(f"FEHLER bei der Identifizierung der Top-Produkte: {e}")


    # Schritt 5: Analyse nach Produktkategorien (aggregiert)
    print("\n--- Analyse nach Produktkategorien ---")
    try:
        category_analysis = product_analysis_df.groupby('product_category_name_english').agg(
            total_revenue=('total_revenue', 'sum'),
            total_units_sold=('total_units_sold', 'sum'),
            number_of_products=('product_id', 'nunique') # Anzahl einzigartiger Produkte pro Kategorie
        ).reset_index()

        top_revenue_categories = category_analysis.sort_values(by='total_revenue', ascending=False).head(N_TOP)
        top_units_categories = category_analysis.sort_values(by='total_units_sold', ascending=False).head(N_TOP)

        print(f"\n--- Top {N_TOP} Kategorien nach Gesamtumsatz ---")
        print(top_revenue_categories)

        print(f"\n--- Top {N_TOP} Kategorien nach verkauften Einheiten ---")
        print(top_units_categories)

        # Schritt 6: Visualisierung der Top-Kategorien (Speichern als HTML)
        print("\nErstelle und speichere Plotly-Grafiken für Top-Kategorien...")

        # Plot: Top Kategorien nach Umsatz
        fig_cat_revenue = px.bar(
            data_frame=top_revenue_categories,
            x='product_category_name_english',
            y='total_revenue',
            title=f'Top {N_TOP} Product categories by total sales',
            labels={'product_category_name_english': 'Product category', 'total_revenue': 'Total sales (BRL)'},
            color='total_revenue',
            color_continuous_scale=px.colors.sequential.Viridis,
            text_auto='.2s' # Format der Textlabels auf den Balken
        )
        fig_cat_revenue.update_layout(xaxis_title="Product category", yaxis_title="Total revenue (BRL)", xaxis={'categoryorder':'total descending'})
        fig_cat_revenue.update_traces(textposition='outside')
        revenue_plot_file = 'top_categories_revenue.html'
        fig_cat_revenue.write_html(revenue_plot_file)
        print(f"Plot gespeichert als: {revenue_plot_file}")


        # Plot: Top Kategorien nach verkauften Einheiten
        fig_cat_units = px.bar(
            data_frame=top_units_categories,
            x='product_category_name_english',
            y='total_units_sold',
            title=f'Top {N_TOP} Product categories by units sold',
            labels={'product_category_name_english': 'Product category', 'total_units_sold': 'Units sold'},
            color='total_units_sold',
            color_continuous_scale=px.colors.sequential.Plasma,
            text_auto=True # Zeigt die Werte auf den Balken an
        )
        fig_cat_units.update_layout(xaxis_title="Product category", yaxis_title="Units sold", xaxis={'categoryorder':'total descending'})
        fig_cat_units.update_traces(textposition='outside')
        units_plot_file = 'top_categories_units.html'
        fig_cat_units.write_html(units_plot_file)
        print(f"Plot gespeichert als: {units_plot_file}")

    except KeyError as e:
        print(f"FEHLER bei der Kategorienanalyse oder Visualisierung: Spalte {e} fehlt.")
    except Exception as e:
        print(f"FEHLER bei der Kategorienanalyse oder Visualisierung: {e}")

# ## 4. Hauptausführung
def main():
    """Hauptfunktion zur Steuerung des Skriptablaufs."""
    data = load_data(DATA_FILES)

    # Stelle sicher, dass die benötigten DataFrames geladen wurden
    if 'order_items' in data and 'products' in data and 'product_category_name' in data:
        analyze_and_plot_products(data['order_items'], data['products'], data['product_category_name'])
    else:
        print("Analyse kann nicht durchgeführt werden, da benötigte Daten fehlen ('order_items', 'products', 'product_category_name').")

    print("\n--- Produktanalyse-Skript abgeschlossen ---")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nFATALER FEHLER im Skript: {e}")
        sys.exit(1)