import gspread
import os
import json
from google.oauth2.service_account import Credentials
from datetime import datetime

SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
SPREADSHEET_NAME = "Oportunidades inmobiliarias"

def append_rows(rows):
    try:
        # 1. Leer credenciales desde la variable de entorno de Railway
        google_json_str = os.getenv("GOOGLE_JSON")
        if not google_json_str:
            print("❌ Error: Falta la variable GOOGLE_JSON en Railway")
            return

        creds_dict = json.loads(google_json_str, strict=False)
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        client = gspread.authorize(creds)
        
        # 2. Abrir la hoja
        sh = client.open(SPREADSHEET_NAME)
        ws = sh.get_worksheet(0) # Abre la primera pestaña

        # 3. Formatear datos para las columnas
        values = []
        for r in rows:
            precio = r.get("precio_usd")
            metros = r.get("metros")
            m2 = (precio / metros) if (precio and metros and metros > 0) else 0

            values.append([
                datetime.now().strftime("%d/%m/%Y %H:%M"),
                r.get("zona"),
                precio,
                metros,
                round(m2, 2),
                r.get("ambientes"),
                r.get("link")
            ])

        if values:
            ws.append_rows(values, value_input_option="USER_ENTERED")
            print(f"✅ {len(values)} filas enviadas a Google Sheets.")

    except Exception as e:
        print(f"❌ Error en sheets.py: {e}")
