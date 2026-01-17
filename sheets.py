import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_NAME = "Oportunidades inmobiliarias"   # exacto
WORKSHEET_NAME = "Sheet1"                  # exacto
CREDS_FILE = "service_account.json"        # ya la tenés

def append_rows(rows):
    creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
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
            None,   # score (si ya lo tenés, pasalo)
            None    # decision
        ])

    if values:
        ws.append_rows(values, value_input_option="RAW")
