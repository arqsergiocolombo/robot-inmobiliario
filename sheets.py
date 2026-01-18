import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

def export_to_sheets(data):
    if not data:
        print("⚠️ No hay datos para exportar.")
        return

    # ID limpio extraído de tu link
    SPREADSHEET_ID = '1fCjrsBqdjDvkwi7ROKiKcKdAFfDvmetyrP-xsqcFjRg' 
    RANGE_NAME = 'Sheet1!A2'

    try:
        # Leemos la variable de Railway
        env_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON') or os.environ.get('GOOGLE_JSON')
        
        if not env_json:
            print("❌ ERROR: No se encontró la credencial en Railway.")
            return

        info = json.loads(env_json)
        creds = service_account.Credentials.from_service_account_info(info)
        service = build('sheets', 'v4', credentials=creds)

        # Formato de datos: Precio, Zona, Link
        values = [[d['precio_usd'], d['zona'], d['link']] for d in data]
        body = {'values': values}

        # Escritura en la planilla
        service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME,
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        
        print("📊 ¡VICTORIA! Los datos ya están en tu Google Sheets.")
        
    except Exception as e:
        print(f"❌ Error al exportar: {e}")
