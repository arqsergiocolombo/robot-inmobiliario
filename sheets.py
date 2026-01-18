import os
import json
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

def export_to_sheets(data):
    if not data: return

    SPREADSHEET_ID = '1fCjrsBqdjDvkwi7ROKiKcKdAFfDvmetyrP-xsqcFjRg'

    try:
        env_json = os.environ.get('GOOGLE_JSON') or os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
        info = json.loads(env_json)
        creds = service_account.Credentials.from_service_account_info(info)
        service = build('sheets', 'v4', credentials=creds)

        # Leer links para no repetir (Columna J ahora)
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID, range='Sheet1!J:J'
        ).execute()
        links_viejos = [item[0] for item in result.get('values', []) if item]

        # FECHA Y HORA ACTUAL
        fecha_hoy = datetime.now().strftime("%d/%m/%Y")
        hora_ahora = datetime.now().strftime("%H:%M")
        
        nuevas_filas = []

        for d in data:
            if d['link'] in links_viejos: continue

            sup = int(d['superficie'])
            p_m2 = round(d['precio'] / sup, 2) if sup > 0 else 0
            txt = (d['direccion'] + d['link']).lower()
            barrio = "Palermo" if "palermo" in txt else "Belgrano" if "belgrano" in txt else "Recoleta" if "recoleta" in txt else "CABA"

            # ARMAR FILA (A:Fecha, B:Hora, C:Barrio, D:Precio, E:Moneda, F:Sup, G:P_m2, H:Amb, I:Dir, J:Link)
            nuevas_filas.append([
                fecha_hoy, hora_ahora, barrio, d['precio'], "USD", 
                sup, p_m2, d['ambientes'], d['direccion'], d['link']
            ])

        if nuevas_filas:
            nuevas_filas.append([""] * 10) # Renglón vacío
            service.spreadsheets().values().append(
                spreadsheetId=SPREADSHEET_ID,
                range='Sheet1!A2',
                valueInputOption='USER_ENTERED',
                body={'values': nuevas_filas}
            ).execute()
            print(f"✅ ¡Datos cargados con hora y ambientes!")

    except Exception as e:
        print(f"❌ Error en Sheets: {e}")
