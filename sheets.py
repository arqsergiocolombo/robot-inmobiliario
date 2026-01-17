import gspread
import os
import json
from google.oauth2.service_account import Credentials
from datetime import datetime

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_NAME = "Oportunidades inmobiliarias"
WORKSHEET_NAME = "Sheet1"

def append_rows(rows):
    raw = os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]

    # Normaliza saltos de línea del private_key
    raw = raw.replace("\\n", "\n")

    service_account_info = json.loads(raw)

    creds = Credentials.from_service_account_info(
        service_account_info,
        scopes=SCOPES
    )

    client = gspread.authorize(creds)
    sh = client.open(SPREADSHEET_NAME)
    ws = sh.worksheet(WORKSHEET_NAME)

    values = []
    for r in rows:
        precio = r.get("precio_usd")
        metros = r.get("metros")
        precio_m2 = (precio / metros) if precio and metros else None

        values.append([
            datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            r.get("fuente"),
            r.get("zona"),
            precio,
            metros,
            precio_m2,
            r.get("ambientes"),
            r.get("link"),
            None,
            None
        ])

    if values:
        ws.append_rows(values, value_input_option="RAW")
