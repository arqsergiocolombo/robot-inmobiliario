import requests
from bs4 import BeautifulSoup

URL = "https://listado.mercadolibre.com.ar/inmuebles/departamentos/venta/capital-federal/"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def scrape_all():
    print(f"Buscando en: {URL}")
    response = requests.get(URL, headers=HEADERS, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.select("li.ui-search-layout__item")

    rows = []

    for item in items:
        try:
            precio = item.select_one(".andes-money-amount__fraction")
            precio_usd = (
                float(precio.text.replace(".", ""))
                if precio else None
            )

            zona = item.select_one(".ui-search-item__group__element")
            zona = zona.text.strip() if zona else None

            link = item.find("a", href=True)
            link = link["href"] if link else None

            rows.append({
                "fuente": "MercadoLibre",
                "zona": zona,
                "precio_usd": precio_usd,
                "metros": None,
                "ambientes": None,
                "link": link
            })

        except Exception:
            continue

    return rows
