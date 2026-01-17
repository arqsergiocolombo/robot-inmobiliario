import os
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_NAME = "Oportunidades inmobiliarias"
WORKSHEET_NAME = "Sheet1"

CREDS_ENV = "GOOGLE_SERVICE_ACCOUNT_JSON"
CREDS_FILE = "service_account.json"


def _ensure_creds_file():
    if not os.path.exists(CREDS_FILE):
        raw = os.getenv(CREDS_ENV)
        if not raw:
            raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_JSON not found")
        with open(CREDS_FILE, "w") as f:
            f.write(raw)


def append_rows(rows):
    _ensure_creds_file()

    creds = Credentials.from_service_account_file(
        CREDS_FILE, scopes=SCOPES
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
