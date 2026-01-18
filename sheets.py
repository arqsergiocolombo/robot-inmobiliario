import os
import json
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

def export_to_sheets(data):
    if not data: return
    SPREADSHEET_ID = '1fCjrsBqdjDvkwi7ROKiKcKdAFfDvmetyrP-xsqcFjRg' 
    RANGE_NAME = 'Sheet1!A2'

    try:
        env_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON') or os.environ.get('GOOGLE_JSON')
        info = json.loads(env_json)
        creds = service_account.Credentials.from_service_account_info(info)
        service = build('sheets', 'v4', credentials=creds)

        hoy = datetime.now().strftime("%d/%m/%Y")
        values = []

        for d in data:
            # Cálculo de Precio por m2
            p_m2 = round(d['precio'] / int(d['superficie']), 2) if int(d['superficie']) > 0 else 0
            
            # ORDEN ESTRICTO SEGÚN TU EXCEL:
            fila = [
                hoy,            # A: Fecha
                "CABA",         # B: Barrio
                d['precio'],    # C: Precio
                "USD",          # D: Moneda
                d['superficie'],# E: Superficie_m2
                p_m2,           # F: Precio_m2
                d['ambientes'], # G: Ambientes
                d['direccion'], # H: Direccion
                d['link']       # I: Link
            ]
            values.append(fila)

        body = {'values': values}
        service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME,
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        print("📊 ¡Excel mapeado correctamente!")
    except Exception as e:
        print(f"❌ Error en Sheets: {e}")
