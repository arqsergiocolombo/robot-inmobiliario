# scraper_ml.py
# Scraper simple de Mercado Libre (HTML) – 1 página por búsqueda
# Devuelve lista de dicts normalizados (listos para subir a Sheets)

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode
import re

BASE_URL = "https://listado.mercadolibre.com.ar"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "es-AR,es;q=0.9"
}

# Ajustar si ya tenés barrios/valores definidos en tu proyecto
BARRIOS = [
    "belgrano",
    "palermo",
    "recoleta",
    "nuñez",
]

def _to_int(text):
    if not text:
        return None
    nums = re.sub(r"[^\d]", "", text)
    return int(nums) if nums else None

def scrape_busqueda(barrio: str, pagina: int = 1):
    """
    barrio: string (ej 'belgrano')
    pagina: int (1 = primera página)
    """
    path = f"/inmuebles/departamentos/venta/{barrio}"
    params = {}
    if pagina > 1:
        params["page"] = pagina

    url = f"{BASE_URL}{path}"
    if params:
        url = f"{url}?{urlencode(params)}"

    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")
    cards = soup.select("li.ui-search-layout__item")

    resultados = []
    for c in cards:
        # Link
        a = c.select_one("a.ui-search-link")
        link = a["href"] if a and a.has_attr("href") else None

        # Precio
        precio_el = c.select_one("span.andes-money-amount__fraction")
        precio = _to_int(precio_el.get_text()) if precio_el else None

        # Metros (puede no estar)
        metros = None
        for li in c.select("ul.ui-search-card-attributes li"):
            t = li.get_text(strip=True).lower()
            if "m²" in t or "m2" in t:
                metros = _to_int(t)
                break

        # Ambientes (puede no estar)
        ambientes = None
        for li in c.select("ul.ui-search-card-attributes li"):
            t = li.get_text(strip=True).lower()
            if "amb" in t:
                ambientes = _to_int(t)
                break

        if not link or not precio:
            continue

        resultados.append({
            "fuente": "Mercado Libre",
            "zona": barrio.title(),
            "precio_usd": precio,
            "metros": metros,
            "ambientes": ambientes,
            "link": link
        })

    return resultados

def scrape_all():
    """
    Ejecuta 1 página por barrio (simple y seguro).
    Devuelve lista consolidada.
    """
    all_rows = []
    for b in BARRIOS:
        rows = scrape_busqueda(barrio=b, pagina=1)
        all_rows.extend(rows)
    return all_rows

# Uso directo (opcional para prueba local)
if __name__ == "__main__":
    data = scrape_all()
    print(f"Items: {len(data)}")
    for x in data[:3]:
        print(x)
