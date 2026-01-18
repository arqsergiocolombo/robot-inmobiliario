import os
import json
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

def export_to_sheets(data):
    if not data:
        print("⚠️ Sin datos nuevos bajo el filtro de 150k.")
        return

    SPREADSHEET_ID = '1fCjrsBqdjDvkwi7ROKiKcKdAFfDvmetyrP-xsqcFjRg'

    try:
        env_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON') or os.environ.get('GOOGLE_JSON')
        info = json.loads(env_json)
        creds = service_account.Credentials.from_service_account_info(info)
        service = build('sheets', 'v4', credentials=creds)

        # 1. OBTENER LINKS YA EXISTENTES (Columna I)
        sheet_metadata = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID, range='Sheet1!I:I'
        ).execute()
        links_en_excel = [item[0] for item in sheet_metadata.get('values', []) if item]

        hoy = datetime.now().strftime("%d/%m/%Y %H:%M")
        nuevas_filas = []

        for d in data:
            # EVITAR DUPLICADOS
            if d['link'] in links_en_excel:
                continue

            sup = int(d['superficie'])
            p_m2 = round(d['precio'] / sup, 2) if sup > 0 else 0
            
            # Limpieza de barrio
            txt = (d['direccion'] + d['link']).lower()
            barrio = "Palermo" if "palermo" in txt else "Belgrano" if "belgrano" in txt else "Recoleta" if "recoleta" in txt else "CABA"

            nuevas_filas.append([hoy, barrio, d['precio'], "USD", sup, p_m2, d['ambientes'], d['direccion'], d['link']])

        if not nuevas_filas:
            print("✨ No se encontraron propiedades nuevas en esta vuelta.")
            return

        # 2. AGREGAR FILA VACÍA AL FINAL DE LA TANDA
        nuevas_filas.append(["", "", "", "", "", "", "", "", ""])

        # 3. INSERTAR
        service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range='Sheet1!A2',
            valueInputOption='USER_ENTERED',
            body={'values': nuevas_filas}
        ).execute()
        
        print(f"📊 ¡Éxito! {len(nuevas_filas)-1} propiedades nuevas agregadas.")

    except Exception as e:
        print(f"❌ Error en Sheets: {e}")
