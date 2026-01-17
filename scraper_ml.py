import requests
from bs4 import BeautifulSoup

BASE_URL = "https://listado.mercadolibre.com.ar/inmuebles/departamentos/venta/capital-federal/"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def scrape_all():
    print(f"Buscando en: {BASE_URL}")

    resp = requests.get(BASE_URL, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(resp.text, "html.parser")

    items = soup.select("li.ui-search-layout__item")

    rows = []

    for item in items[:10]:  # limitamos para pruebas
        try:
            title = item.select_one("h2").text.strip()
            link = item.select_one("a")["href"]

            price_tag = item.select_one("span.andes-money-amount__fraction")
            price = int(price_tag.text.replace(".", "")) if price_tag else None

            rows.append({
                "fuente": "MercadoLibre",
                "zona": "Capital Federal",
                "precio_usd": price,
                "metros": None,
                "ambientes": None,
                "link": link
            })

        except Exception:
            continue

    return rows
