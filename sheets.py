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

    # normaliza saltos de línea del private_key
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
    for r in r
