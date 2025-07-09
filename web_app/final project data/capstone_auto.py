
import os
import json
import requests
import zipfile
from dotenv import dotenv_values

# ===============================
# 1. Lade API-Zugangsdaten & Datasetnamen aus .env
# ===============================
config = dotenv_values()  # Lese .env-Datei

# Token auslesen und prüfen
if 'KAGGLE_TOKEN' not in config:
    raise ValueError("Fehlender KAGGLE_TOKEN in der .env-Datei!")

# Versuche Token als JSON zu interpretieren
try:
    api_token = json.loads(config['KAGGLE_TOKEN'])
except json.JSONDecodeError:
    raise ValueError("KAGGLE_TOKEN ist kein gültiger JSON-String!")

# Datasetnamen auslesen
datasetname = config.get("KAGGLE_DATASET")
if not datasetname:
    raise ValueError("Fehlender KAGGLE_DATASET in der .env-Datei!")

# ===============================
# 2. Pfade und URL vorbereiten
# ===============================
filename = datasetname.replace('/', '_')  # z. B. olistbr_brazilian-ecommerce
dataset_url = f'https://www.kaggle.com/api/v1/datasets/download/{datasetname}'
headers = {'Content-Type': 'application/json'}

# Zielverzeichnisse
download_dir = 'download'
extracted_dir = os.path.join(download_dir, 'extracted')
os.makedirs(download_dir, exist_ok=True)
os.makedirs(extracted_dir, exist_ok=True)

# ===============================
# 3. Download vom Dataset über die Kaggle-API
# ===============================
print(f"Lade Dataset: {datasetname}")
response = requests.get(
    dataset_url,
    headers=headers,
    auth=(api_token['username'], api_token['key'])  # Authentifizierung mit API-Token
)

# Fehlerprüfung
if response.status_code != 200:
    raise Exception(f"Fehler beim Herunterladen ({response.status_code}): {response.text}")

# ZIP-Datei speichern
dataset_path = os.path.join(download_dir, f"{filename}.zip")
with open(dataset_path, 'wb') as f:
    f.write(response.content)

print(f"ZIP-Datei gespeichert unter: {dataset_path}")

# ===============================
# 4. Entpacken der ZIP-Datei
# ===============================
with zipfile.ZipFile(dataset_path, 'r') as zip_ref:
    zip_ref.extractall(extracted_dir)
    
print(f"Dataset entpackt nach: {extracted_dir}")



