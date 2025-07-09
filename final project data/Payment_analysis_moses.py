#!/usr/bin/env python
# coding: utf-8

# # Analyse der Zahlungsarten (Olist Dataset)

# ## 1. Importieren der notwendigen Bibliotheken
# Stellen Sie sicher, dass diese Bibliotheken installiert sind:
# pip install pandas numpy seaborn matplotlib

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os # Wird für die Pfadprüfung verwendet
import sys # Wird für sys.exit verwendet

print("Bibliotheken importiert.")

# ## 2. Definition der Dateipfade
# Passen Sie diese Pfade an, falls sich Ihre Daten an einem anderen Ort befinden.
# Standardmäßig wird das aktuelle Verzeichnis (.) verwendet.
DATA_DIR = '.' # Verzeichnis, in dem die CSV-Dateien erwartet werden

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

# ## 3. Laden der Datensätze mit Fehlerbehandlung
print("\n--- Lade Datensätze ---")
loaded_data = {}
all_files_loaded = True
for name, path in DATA_FILES.items():
    try:
        loaded_data[name] = pd.read_csv(path, sep=",")
        print(f"'{path}' erfolgreich geladen.")
    except FileNotFoundError:
        print(f"FEHLER: Datei nicht gefunden: '{path}'. Bitte Pfad prüfen.")
        all_files_loaded = False
    except Exception as e:
        print(f"FEHLER beim Laden von '{path}': {e}")
        all_files_loaded = False

# Beenden, wenn nicht alle Dateien geladen werden konnten (besonders Zahlungsdaten sind wichtig)
if not all_files_loaded or 'order_payments' not in loaded_data:
    print("\nNicht alle benötigten Datensätze konnten geladen werden. Skript wird beendet.")
    sys.exit(1) # Beendet das Skript mit einem Fehlercode

# Zugriff auf die wichtigsten DataFrames
order_payments = loaded_data['order_payments']
# Weitere DataFrames können bei Bedarf verwendet werden:
# customers = loaded_data['customers']
# orders = loaded_data['orders']
# ... usw.

print("\n--- Erste Erkundung der Zahlungsarten ---")

# ## 4. Analyse nach Zahlungsart
try:
    # Berechne Statistiken pro Zahlungsart
    payment_type_analysis = order_payments.groupby('payment_type')['payment_value'].agg(
        average_payment_value='mean', # Durchschnittlicher Zahlungswert pro Typ
        number_of_payments='count',   # Anzahl der Zahlungen pro Typ
        total_payment_value='sum'     # Gesamter Zahlungswert pro Typ
    ).reset_index().sort_values(by='average_payment_value', ascending=False) # Sortieren nach Durchschnittswert

    print("\nDurchschnittlicher Zahlungswert und Anzahl pro Zahlungsart:")
    print(payment_type_analysis)

    # --- Visualisierung nach Zahlungsart (Speichern als Datei) ---
    plt.figure(figsize=(10, 6))
    sns.barplot(data=payment_type_analysis, x='payment_type', y='average_payment_value', palette='viridis')
    plt.title('Average payment value per payment type')
    plt.xlabel('Payment method')
    plt.ylabel('Average payment value (BRL)')
    plt.xticks(rotation=45) # Verbessert Lesbarkeit der Labels
    plt.tight_layout() # Passt Layout an
    plot_filename_type = 'payment_types_avg_value.png'
    plt.savefig(plot_filename_type)
    print(f"\nPlot gespeichert als: {plot_filename_type}")
    plt.close() # Schließt die Plot-Figur, um Speicher freizugeben

except KeyError as e:
    print(f"\nFEHLER bei der Zahlungsart-Analyse: Spalte {e} nicht im 'order_payments' DataFrame gefunden.")
except Exception as e:
    print(f"\nFEHLER bei der Zahlungsart-Analyse oder Visualisierung: {e}")


# ## 5. Detailanalyse für Ratenzahlungen (Kreditkarte)
print("\n--- Detailanalyse der Kreditkarten-Ratenzahlungen ---")
try:
    # Filtere nur Zahlungen, die per Kreditkarte erfolgten
    # .copy() verhindert SettingWithCopyWarning, falls das DataFrame später geändert wird
    credit_card_payments = order_payments[order_payments['payment_type'] == 'credit_card'].copy()

    if not credit_card_payments.empty:
        # Berechne Statistiken pro Anzahl der Raten
        installments_analysis = credit_card_payments.groupby('payment_installments')['payment_value'].agg(
            average_payment_value='mean', # Durchschnittlicher Zahlungswert pro Ratenanzahl
            number_of_payments='count',   # Anzahl der Zahlungen pro Ratenanzahl
            total_payment_value='sum'     # Gesamter Zahlungswert pro Ratenanzahl
        ).reset_index()

        print("\nDurchschnittlicher Zahlungswert und Anzahl pro Ratenanzahl (nur Kreditkarte):")
        print(installments_analysis)

        # --- Visualisierung nach Ratenanzahl (Speichern als Datei) ---
        plt.figure(figsize=(12, 7))
        sns.barplot(data=installments_analysis, x='payment_installments', y='average_payment_value', palette='magma')
        plt.title('Average payment value per number of installments (credit card only)')
        plt.xlabel('Number of installments')
        plt.ylabel('Average payment value (BRL)')
        plt.tight_layout()
        plot_filename_installments = 'installments_avg_value.png'
        plt.savefig(plot_filename_installments)
        print(f"\nPlot gespeichert als: {plot_filename_installments}")
        plt.close() # Schließt die Plot-Figur
    else:
        print("\nKeine Kreditkartenzahlungen im Datensatz gefunden.")

except KeyError as e:
    print(f"\nFEHLER bei der Raten-Analyse: Spalte {e} nicht im 'order_payments' DataFrame gefunden.")
except Exception as e:
    print(f"\nFEHLER bei der Raten-Analyse oder Visualisierung: {e}")


print("\n--- Analyse abgeschlossen ---")




