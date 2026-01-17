import requests
from bs4 import BeautifulSoup
import re

def scrape_all():
    # Tu URL específica
    url = "https://inmuebles.mercadolibre.com.ar/departamentos/venta/mas-de-2-dormitorios/capital-federal/departamento_NoIndex_True"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "es-AR,es;q=0.9",
        "referer": "https://www.google.com/"
    }

    try:
        session = requests.Session()
        res = session.get(url, headers=headers, timeout=20)
        
        print(f"DEBUG - Status: {res.status_code}")
        
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # --- CAMBIO CLAVE AQUÍ ---
        # Buscamos la clase 'ui-search-result__content-wrapper' que es el estándar actual de Inmuebles
        items = soup.find_all('div', class_='ui-search-result__content-wrapper')
        
        if not items:
            # Plan B: buscar por el contenedor principal de la tarjeta
            items = soup.find_all('div', class_='ui-search-result__wrapper')

        print(f"🔎 Analizando {len(items)} propiedades encontradas...")

        results = []
        for item in items:
            try:
                # 1. Precio (ahora buscamos dentro de la clase de dinero)
                price_elem = item.find('span', class_='andes-money-amount__fraction')
                precio = int(price_elem.text.replace('.', '')) if price_elem else 0
                
                # 2. Link (buscamos el anchor que envuelve el título)
                # Subimos un nivel para encontrar el link si no está en el content-wrapper
                parent = item.parent
                link_tag = parent.find('a', class_='ui-search-link') if parent else None
                if not link_tag:
                    link_tag = item.find_all_previous('a', class_='ui-search-link', limit=1)[0]
                
                link = link_tag['href'] if link_tag else ""
                
                # 3. Zona / Título
                zona_tag = item.find('h2', class_='ui-search-item__title')
                zona = zona_tag.text if zona_tag else "CABA"

                # 4. Metros y Ambientes
                attrs = item.find_all('li', class_='ui-search-card-attributes__attribute')
                m2, amb = 0, ""
                for a in attrs:
                    txt = a.text.lower()
                    if "m²" in txt:
                        m_match = re.search(r'\d+', txt.replace('.',''))
                        if m_match: m2 = int(m_match.group())
                    elif "ambiente" in txt:
                        amb = a.text

                if precio > 0:
                    results.append({
                        "precio_usd": precio,
                        "link": link,
                        "zona": zona,
                        "metros": m2,
                        "ambientes": amb
                    })
            except Exception:
                continue
        
        return results

    except Exception as e:
        print(f"❌ Error: {e}")
        return []
