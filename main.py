import os
import json
import time
import gspread
from google.oauth2.service_account import Credentials

print("🚀 Robot inmobiliario iniciado")

# ==============================
# 1. CARGAR CREDENCIALES GOOGLE
# ==============================

if "GOOGLE_CREDENTIALS_JSON" not in os.environ:
    raise Exception("❌ Falta la variable GOOGLE_CREDENTIALS_JSON")

creds_json = os.environ["GOOGLE_CREDENTIALS_JSON"]
creds_dict = json.loads(creds_json)

scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

credentials = Credentials.from_service_account_info(
    creds_dict,
    scopes=scopes
)

client = gspread.authorize(credentials)

print("✅ Conectado a Google Sheets")

# ==============================
# 2. ABRIR GOOGLE SHEET
# ==============================

# ⚠️ CAMBIÁ ESTE NOMBRE POR EL REAL
SPREADSHEET_NAME = "robot-inmobiliario"

sheet = client.open(SPREADSHEET_NAME).sheet1

print("✅ Spreadsheet abierto")

# ==============================
# 3. LOOP PRINCIPAL (cada 1 hora)
# ==============================

while True:
    print("🔍 Ejecutando búsqueda (placeholder)")

    # Ejemplo de escritura para probar que funciona
    sheet.append_row([
        time.strftime("%Y-%m-%d %H:%M:%S"),
        "Robot funcionando correctamente"
    ])

    print("⏳ Esperando 1 hora...")
    time.sleep(3600)
