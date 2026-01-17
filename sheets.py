import gspread
import os
import json
from google.oauth2.service_account import Credentials
from datetime import datetime

# Configuraciones
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
SPREADSHEET_NAME = "Oportunidades inmobiliarias"
WORKSHEET_NAME = "Sheet1"

def append_rows(rows):
    try:
        # 1. Intentamos obtener la variable de entorno desde Railway
        raw_json = os.environ.get("GOOGLE_JSON") # Cambié el nombre a uno más simple
        
        if not raw_json:
            print("Error: La variable de entorno GOOGLE_JSON no está configurada en Railway.")
            return

        # Limpieza de caracteres especiales por si acaso
        service_account_info = json.loads(raw_json, strict=False)

        # 2. Autenticación
        creds = Credentials.from_service_account_info(
            service_account_info,
            scopes=SCOPES
        )

        client = gspread.authorize(creds)
        
        # 3. Abrir la hoja de cálculo
        sh = client.open(SPREADSHEET_NAME)
        ws = sh.worksheet(WORKSHEET_NAME)

        # 4. Procesar los datos
        values = []
        for r in rows:
            precio = r.get("precio_usd")
            metros = r.get("metros")
            
            # Cálculo seguro del m2
            try:
                precio_m2 = (float(precio) / float(metros)) if precio and metros else None
            except (ValueError, TypeError):
                precio_m2 = None

            values.append([
                datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                r.get("fuente", "Mercado Libre"),
                r.get("zona", "N/A"),
                precio,
                metros,
                precio_m2,
                r.get("ambientes"),
                r.get("link"),
                "Nuevo", # Estado por defecto
                ""       # Notas
            ])

        # 5. Subir a Google Sheets
        if values:
            ws.append_rows(values, value_input_option="USER_ENTERED")
            print(f"✅ Se han subido {len(values)} nuevas propiedades.")
        else:
            print("⚠️ No hay datos nuevos para subir.")

    except Exception as e:
        print(f"❌ Error crítico en sheets.py: {e}")
