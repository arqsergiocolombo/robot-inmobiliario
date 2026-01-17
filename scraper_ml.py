import requests
from bs4 import BeautifulSoup
import re

def scrape_all():
    # USAMOS LA VERSIÓN MÓVIL DEL SITIO (m.mercadolibre...)
    url = "https://inmuebles.mercadolibre.com.ar/departamentos/venta/capital-federal/departamentos-venta-capital-federal_NoIndex_True"
    
    # Headers de iPhone para despistar el bloqueo de servidores
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "es-AR,es;q=0.9",
        "Referer": "https://www.google.com/"
    }

    try:
        session = requests.Session()
        res = session.get(url, headers=headers, timeout=20)
        
        print(f"DEBUG - Status: {res.status_code}")
        
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # En la version movil, las propiedades suelen estar en etiquetas 'a' con esta clase:
        items = soup.find_all('a', class_=re.compile(r'ui-search-result__content|ui-search-link'))
        
        if not items:
            # Plan B: Buscar cualquier enlace que contenga el precio adentro
            items = soup.select('ol.ui-search-layout li')

        print(f"🔎 Analizando {len(items)} posibles resultados...")

        results = []
        for item in items:
            try:
                # Buscar precio
                price_elem = item.find('span', class_='andes-money-amount__fraction')
                if not price_elem: continue
                precio = int(price_elem.text.replace('.', ''))

                # Buscar link
                link = item.get('href', '')
                if not link or 'MLA' not in link:
                    # Si el item no es el link, buscamos el link adentro
                    link_tag = item.find('a')
                    link = link_tag['href'] if link_tag else ""

                # Zona y Titulo
                title_elem = item.find(['h2', 'h3'])
                zona = title_elem.text.strip() if title_elem else "CABA"

                if precio > 0 and link:
                    results.append({
                        "precio_usd": precio,
                        "link": link,
                        "zona": zona,
                        "metros": 0,
                        "ambientes": "S/D"
                    })
            except:
                continue
        
        return results

    except Exception as e:
        print(f"❌ Error: {e}")
        return []
