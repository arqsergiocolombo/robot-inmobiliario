import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

def export_to_sheets(data):
    if not data:
        print("⚠️ No hay datos para exportar.")
        return

    # ID de tu planilla (sacalo de la URL de tu Google Sheet)
    # Ejemplo: https://docs.google.com/spreadsheets/d/TU_ID_ACA/edit
    SPREADSHEET_ID = 'https://docs.google.com/spreadsheets/d/1fCjrsBqdjDvkwi7ROKiKcKdAFfDvmetyrP-xsqcFjRg/edit?gid=0#gid=0' 
    RANGE_NAME = 'Sheet1!A2'

    try:
        # Cargamos la credencial desde la variable de entorno de Railway
        info = json.loads(os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON'))
        creds = service_account.Credentials.from_service_account_info(info)
        service = build('sheets', 'v4', credentials=creds)

        # Formateamos los datos para Google Sheets
        values = [[d['precio_usd'], d['zona'], d['link']] for d in data]
        body = {'values': values}

        service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME,
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        
        print("📊 ¡Datos exportados a Google Sheets exitosamente!")
    except Exception as e:
        print(f"❌ Error al exportar a Sheets: {e}")
