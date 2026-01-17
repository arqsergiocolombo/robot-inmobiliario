import time
import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os, json
from datetime import datetime

print("ROBOT INMOBILIARIO INICIADO")

# --- GOOGLE SHEETS ---
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds_dict = json.loads(os.environ["GOOGLE_CREDENTIALS_JSON"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

sheet = client.open("Oportunidades inmobiliarias").sheet1

# --- MERCADOLIBRE ---
URL = "https://inmuebles.mercadolibre.com.ar/departamentos/venta/capital-federal/"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def link_existe(link):
    return link in sheet.col_values(9)

def buscar():
    print("Buscando publicaciones...")
    r = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")
    avisos = soup.select("li.ui-search-layout__item")

    for a in avisos:
        try:
            link = a.find("a")["href"]
            texto = a.text.lower()

            if link_existe(link):
                continue
            if "estrenar" in texto:
                continue
            if "frente" not in texto:
                continue

            precio = a.find("span", class_="price-tag-fraction").text.replace(".", "")
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M")

            sheet.append_row([
                fecha,
                "",
                precio,
                "USD",
                "",
                "",
                "",
                "",
                link,
                ""
            ])

            print(f"Agregado: {link}")

        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    while True:
        buscar()
        print("Ciclo completo. Esperando 1 hora.")
        time.sleep(3600)
