import time
import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
CREDS = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json", SCOPE
)
client = gspread.authorize(CREDS)
sheet = client.open("Oportunidades inmobiliarias").sheet1

URL = "https://inmuebles.mercadolibre.com.ar/departamentos/venta/capital-federal/"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def ya_existe(link):
    return link in sheet.col_values(9)

def buscar():
    r = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")
    avisos = soup.select("li.ui-search-layout__item")

    for a in avisos:
        try:
            link = a.find("a")["href"]
            if ya_existe(link):
                continue

            texto = a.text.lower()

            if "estrenar" in texto:
                continue
            if "frente" not in texto:
                continue

            precio = a.find(
                "span", class_="price-tag-fraction"
            ).text.replace(".", "")

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
        except:
            pass

if __name__ == "__main__":
    while True:
        buscar()
        time.sleep(3600)
