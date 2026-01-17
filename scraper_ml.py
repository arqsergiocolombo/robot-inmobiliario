import requests
from bs4 import BeautifulSoup
import re

def scrape_all():
    # La URL de departamentos que querés seguir
    target_url = "https://inmuebles.mercadolibre.com.ar/departamentos/venta/mas-de-2-dormitorios/capital-federal/departamento_NoIndex_True"
    
    # --- CONFIGURACIÓN SCRAPER API (Tu llave ya está puesta) ---
    api_key = "eab02f8eb7f617cb6bfd3c2173ed197d" 
    proxy_url = f"http://api.scraperapi.com?api_key={api_key}&url={target_url}"

    try:
        print(f"🚀 Iniciando búsqueda invisible via ScraperAPI...")
        # Esta petición ahora pasa por los servidores de ScraperAPI para evitar bloqueos
        res = requests.get(proxy_url, timeout=60)
        
        print(f"DEBUG - Status: {res.status_code}")
        
        if res.status_code != 200:
            print(f"❌ Error de ScraperAPI: {res.status_code}")
            return []

        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Buscamos las tarjetas de propiedades (ahora que el HTML vendrá completo)
        items = soup.select('div.ui-search-result__wrapper') or soup.select('li.ui-search-layout__item')

        print(f"🔎 Propiedades reales detectadas: {len(items)}")

        results = []
        for item in items:
            try:
                # 1. Extraer Precio
                p_elem = item.find('span', class_='andes-money-amount__fraction')
                precio = int(p_elem.text.replace('.', '')) if p_elem else 0
                
                # 2. Extraer Link
                link_tag = item.find('a', class_='ui-search-link')
                link = link_tag['href'] if link_tag else ""
                
                # 3. Extraer Zona
                title_tag = item.find(['h2', 'h3'])
                zona = title_tag.text.strip() if title_tag else "CABA"

                # Solo guardamos si hay datos válidos
                if link and precio > 0:
                    results.append({
                        "precio_usd": precio,
                        "link": link,
                        "zona": zona,
                        "metros": 0, 
                        "ambientes": "3+"
                    })
            except:
                continue
        
        return results

    except Exception as e:
        print(f"❌ Error crítico en el scraper: {e}")
        return []
