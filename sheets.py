import os
import json
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

def export_to_sheets(data):
    if not data:
        print("⚠️ No se encontraron datos nuevos con los filtros aplicados.")
        return

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
            try:
                superficie = int(d['superficie'])
            except:
                superficie = 0
            
            p_m2 = round(d['precio'] / superficie, 2) if superficie > 0 else 0

            fila = [
                hoy, d['direccion'], d['precio'], "USD", 
                superficie, p_m2, d['ambientes'], d['direccion'], d['link']
            ]
            values.append(fila)

        body = {'values': values}
        service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME,
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        
        print(f"📊 ¡ÉXITO! Se cargaron {len(values)} propiedades en las zonas elegidas.")

    except Exception as e:
        print(f"❌ Error al exportar: {e}")
