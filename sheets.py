import os
import json
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

def export_to_sheets(data):
    if not data:
        print("⚠️ No hay datos que cumplan los filtros.")
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
            sup = int(d['superficie'])
            p_m2 = round(d['precio'] / sup, 2) if sup > 0 else 0
            
            # --- LÓGICA DE DETECCIÓN DE BARRIO ---
            texto_busqueda = (d['direccion'] + d['link']).lower()
            if "palermo" in texto_busqueda:
                barrio_limpio = "Palermo"
            elif "belgrano" in texto_busqueda:
                barrio_limpio = "Belgrano"
            elif "recoleta" in texto_busqueda:
                barrio_limpio = "Recoleta"
            else:
                barrio_limpio = "CABA"

            # MAPEO DE COLUMNAS (A: Fecha | B: Barrio | C: Precio | ...)
            fila = [
                hoy,                # A: Fecha
                barrio_limpio,      # B: Barrio (YA NO SE REPITE LA DIRECCIÓN)
                d['precio'],        # C: Precio (FILTRADO 30k-100k)
                "USD",              # D: Moneda
                sup,                # E: Superficie
                p_m2,               # F: Precio x m2
                d['ambientes'],     # G: Ambientes
                d['direccion'],     # H: Direccion Completa
                d['link']           # I: Link
            ]
            values.append(fila)

        body = {'values': values}
        service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME,
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        
        print(f"📊 ¡Excel actualizado! Barrio y Precios corregidos.")

    except Exception as e:
        print(f"❌ Error en Sheets: {e}")
