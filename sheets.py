import os
import json
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

def export_to_sheets(data):
    if not data:
        print("⚠️ No hay datos nuevos para exportar.")
        return

    # Tu ID de planilla (ya confirmado que funciona)
    SPREADSHEET_ID = '1fCjrsBqdjDvkwi7ROKiKcKdAFfDvmetyrP-xsqcFjRg' 
    RANGE_NAME = 'Sheet1!A2'

    try:
        # Autenticación con las variables de Railway
        env_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON') or os.environ.get('GOOGLE_JSON')
        if not env_json:
            print("❌ ERROR: Credenciales de Google no encontradas.")
            return

        info = json.loads(env_json)
        creds = service_account.Credentials.from_service_account_info(info)
        service = build('sheets', 'v4', credentials=creds)

        hoy = datetime.now().strftime("%d/%m/%Y")
        values = []

        for d in data:
            # Convertimos superficie a número para el cálculo
            try:
                superficie = int(d['superficie'])
            except:
                superficie = 0
            
            # Calculamos Precio por m2 (Columna F)
            # Solo si el precio y la superficie son válidos
            if superficie > 0 and d['precio'] > 0:
                p_m2 = round(d['precio'] / superficie, 2)
            else:
                p_m2 = 0

            # MAPEO DE COLUMNAS SEGÚN TU EXCEL:
            # A: Fecha | B: Barrio | C: Precio | D: Moneda | E: Sup | F: P_m2 | G: Amb | H: Dir | I: Link
            fila = [
                hoy,                # A: Fecha
                "CABA",             # B: Barrio
                d['precio'],        # C: Precio (Ya filtrado sin expensas)
                "USD",              # D: Moneda
                superficie,         # E: Superficie_m2
                p_m2,               # F: Precio_m2
                d['ambientes'],     # G: Ambientes
                d['direccion'],     # H: Direccion
                d['link']           # I: Link
            ]
            values.append(fila)

        # Enviamos los datos a Google Sheets
        body = {'values': values}
        service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME,
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        
        print(f"📊 ¡VICTORIA! Se cargaron {len(values)} propiedades correctamente.")

    except Exception as e:
        print(f"❌ Error al exportar a Sheets: {e}")
