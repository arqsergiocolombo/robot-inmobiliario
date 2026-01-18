import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

def export_to_sheets(data):
    if not data:
        print("⚠️ No hay datos para exportar.")
        return

    # 1. ID DE TU PLANILLA (Solo el código entre /d/ y /edit)
    # Ejemplo: '1FjcJrsBqdjDvkwI7ROKiKcKdAFfDvmet...'
    SPREADSHEET_ID = '1fCjrsBqdjDvkwi7ROKiKcKdAFfDvmetyrP-xsqcFjRg/edit?gid=0#gid=0' 
    RANGE_NAME = 'Sheet1!A2'

    try:
        # Buscamos las credenciales en Railway
        env_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON') or os.environ.get('GOOGLE_JSON')
        
        if not env_json:
            print("❌ ERROR: No se encontró la variable de credenciales en Railway.")
            return

        info = json.loads(env_json)
        creds = service_account.Credentials.from_service_account_info(info)
        service = build('sheets', 'v4', credentials=creds)

        # Preparamos las filas: Precio, Zona, Link
        values = [[d['precio_usd'], d['zona'], d['link']] for d in data]
        body = {'values': values}

        # Escribimos en el Excel
        service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME,
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        
        print("📊 ¡VICTORIA TOTAL! Los 20 departamentos ya están en tu Google Sheets.")
        
    except Exception as e:
        print(f"❌ Error al exportar a Sheets: {e}")
