import requests
from bs4 import BeautifulSoup
import re

def scrape_all():
    # URL de búsqueda (puedes cambiarla por la que prefieras)
    url = "https://listado.mercadolibre.com.ar/inmuebles/departamentos/venta/capital-federal/"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        res = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Buscamos los bloques de cada propiedad
        items = soup.find_all('li', class_='ui-search-layout__item')
        results = []

        for item in items:
            try:
                # Precio
                p_text = item.find('span', class_='andes-money-amount__fraction')
                precio = int(p_text.text.replace('.', '')) if p_text else 0
                
                # Link y Zona
                link_tag = item.find('a', class_='ui-search-link')
                link = link_tag['href'] if link_tag else ""
                zona = item.find('h2', class_='ui-search-item__title').text if item.find('h2') else "Sin zona"

                # Metros y Ambientes
                attrs = item.find_all('li', class_='ui-search-card-attributes__attribute')
                m2, amb = 0, ""
                for a in attrs:
                    if "m²" in a.text:
                        m2 = int(re.search(r'\d+', a.text.replace('.','')).group())
                    elif "ambiente" in a.text.lower():
                        amb = a.text

                results.append({"precio_usd": precio, "link": link, "zona": zona, "metros": m2, "ambientes": amb})
            except:
                continue
        
        return results
    except Exception as e:
        print(f"❌ Error en scraper_ml.py: {e}")
        return []
