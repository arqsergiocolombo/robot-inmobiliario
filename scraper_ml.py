import requests
from bs4 import BeautifulSoup
import re
import time

def scrape_all():
    # URL específica que copiaste de tu navegador
    url = "https://inmuebles.mercadolibre.com.ar/departamentos/venta/mas-de-2-dormitorios/capital-federal/departamento_NoIndex_True"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "es-AR,es;q=0.9",
        "referer": "https://www.google.com/"
    }

    try:
        session = requests.Session()
        print(f"🚀 Iniciando petición a: {url}")
        
        res = session.get(url, headers=headers, timeout=20)
        
        # --- BLOQUE DE DIAGNÓSTICO (Líneas de chequeo) ---
        print(f"DEBUG - Status Code: {res.status_code}")
        print(f"DEBUG - Primeros 300 caracteres del HTML: {res.text[:300].strip()}")
        # ------------------------------------------------
        
        if res.status_code != 200:
            print(f"❌ Error de conexión: Código {res.status_code}")
            return []

        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Selectores actualizados para buscar las tarjetas de propiedades
        items = soup.find_all('li', class_=re.compile(r'ui-search-layout__item'))
        
        # Si el selector anterior falla, probamos con uno alternativo
        if not items:
            items = soup.select('div.ui-search-result__wrapper')

        print(f"🔎 Analizando {len(items)} posibles resultados...")

        results = []
        for item in items:
            try:
                # 1. Extraer Precio
                price_elem = item.find('span', class_='andes-money-amount__fraction')
                precio = int(price_elem.text.replace('.', '')) if price_elem else 0
                
                # 2. Extraer Link
                link_tag = item.find('a', class_='ui-search-link')
                link = link_tag['href'] if link_tag else ""
                
                # 3. Extraer Zona (Desde el título)
                zona_tag = item.find('h2', class_='ui-search-item__title')
                zona = zona_tag.text if zona_tag else "CABA"

                # 4. Extraer Atributos (Metros y Ambientes)
                attrs = item.find_all('li', class_='ui-search-card-attributes__attribute')
                m2, amb = 0, ""
                for a in attrs:
                    txt = a.text.lower()
                    if "m²" in txt:
                        match = re.search(r'\d+', txt.replace('.',''))
                        if match: m2 = int(match.group())
                    elif "ambiente" in txt:
                        amb = a.text

                # Solo guardamos si tiene datos mínimos
                if link and precio > 0:
                    results.append({
                        "precio_usd": precio,
                        "link": link,
                        "zona": zona,
                        "metros": m2,
                        "ambientes": amb
                    })
            except Exception:
                continue # Si falla una propiedad, sigue con la siguiente
        
        return results

    except Exception as e:
        print(f"❌ Error crítico en el scraper: {e}")
        return []
