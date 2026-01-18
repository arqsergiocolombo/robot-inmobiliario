import os
import json
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

def export_to_sheets(data):
    if not data:
        print("⚠️ No hay propiedades nuevas para exportar.")
        return

    SPREADSHEET_ID = '1fCjrsBqdjDvkwi7ROKiKcKdAFfDvmetyrP-xsqcFjRg'

    try:
        # Usamos la llave que ya cargaste en GitHub Secrets
        env_json = os.environ.get('GOOGLE_JSON') or os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
        info = json.loads(env_json)
        creds = service_account.Credentials.from_service_account_info(info)
        service = build('sheets', 'v4', credentials=creds)

        # 1. LEER LINKS EXISTENTES (Ahora en Columna J)
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID, range='Sheet1!J:J'
        ).execute()
        links_viejos = [item[0] for item in result.get('values', []) if item]

        # 2. CAPTURAR FECHA Y HORA POR SEPARADO
        ahora = datetime.now()
        fecha_hoy = ahora.strftime("%d/%m/%Y")
        hora_ahora = ahora.strftime("%H:%M")
        
        nuevas_filas = []

        for d in data:
            # Filtro anti-duplicados
            if d['link'] in links_viejos:
                continue

            sup = int(d['superficie'])
            p_m2 = round(d['precio'] / sup, 2) if sup > 0 else 0
            
            # Limpieza de barrio
            txt = (d['direccion'] + d['link']).lower()
            barrio = "Palermo" if "palermo" in txt else "Belgrano" if "belgrano" in txt else "Recoleta" if "recoleta" in txt else "CABA"

            # 3. ARMAR FILA (10 columnas: A hasta J)
            fila = [
                fecha_hoy,      # A: Fecha
                hora_ahora,     # B: Hora (NUEVA)
                barrio,         # C: Barrio
                d['precio'],    # D: Precio
                "USD",          # E: Moneda
                sup,            # F: Superficie
                p_m2,           # G: Precio x m2
                d['ambientes'], # H: Ambientes
                d['direccion'], # I: Direccion
                d['link']       # J: Link
            ]
            nuevas_filas.append(fila)

        if not nuevas_filas:
            print("✨ Búsqueda terminada: No se encontraron links nuevos.")
            return

        # 4. AGREGAR RENGLÓN VACÍO (10 celdas vacías)
        nuevas_filas.append([""] * 10)

        # 5. GUARDAR EN EL EXCEL
        service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range='Sheet1!A2',
            valueInputOption='USER_ENTERED',
            body={'values': nuevas_filas}
        ).execute()
        
        print(f"📊 ¡Excel actualizado! Se agregaron {len(nuevas_filas)-1} propiedades nuevas.")

    except Exception as e:
        print(f"❌ Error en Sheets: {e}")
