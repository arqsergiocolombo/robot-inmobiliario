import os
import json
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

def export_to_sheets(data):
    if not data: return

    SPREADSHEET_ID = '1fCjrsBqdjDvkwi7ROKiKcKdAFfDvmetyrP-xsqcFjRg'

    try:
        env_json = os.environ.get('GOOGLE_JSON')
        info = json.loads(env_json)
        creds = service_account.Credentials.from_service_account_info(info)
        service = build('sheets', 'v4', credentials=creds)

        # Usamos la columna I para chequear duplicados (donde está el Link)
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID, range='Sheet1!I:I'
        ).execute()
        links_viejos = [item[0] for item in result.get('values', []) if item]

        fecha_hoy = datetime.now().strftime("%d/%m/%Y")
        hora_ahora = datetime.now().strftime("%H:%M")
        
        nuevas_filas = []

        for d in data:
            if d['link'] in links_viejos: continue

            sup = int(d['superficie'])
            p_m2 = round(d['precio'] / sup, 2) if sup > 0 else 0
            
            # Detectar barrio
            txt = (d['direccion'] + d['link']).lower()
            barrio = "Palermo" if "palermo" in txt else "Belgrano" if "belgrano" in txt else "Recoleta" if "recoleta" in txt else "CABA"

            # ORDEN DE COLUMNAS: A:Fecha | B:Hora | C:Barrio | D:Precio | E:Moneda | F:Sup | G:P_m2 | H:Amb | I:Link
            fila = [
                fecha_hoy,      # A
                hora_ahora,     # B (HORA CORREGIDA)
                barrio,         # C
                d['precio'],    # D
                "USD",          # E
                sup,            # F
                p_m2,           # G
                d['ambientes'], # H (AMBIENTES CORREGIDOS)
                d['link']       # I
            ]
            nuevas_filas.append(fila)

        if nuevas_filas:
            # Renglón vacío para separar tandas
            nuevas_filas.append([""] * 9)
            
            service.spreadsheets().values().append(
                spreadsheetId=SPREADSHEET_ID,
                range='Sheet1!A2',
                valueInputOption='USER_ENTERED',
                body={'values': nuevas_filas}
            ).execute()
            print(f"✅ ¡Excel actualizado con Hora y Ambientes!")

    except Exception as e:
        print(f"❌ Error Sheets: {e}")
