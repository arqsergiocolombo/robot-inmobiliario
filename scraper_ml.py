import requests
from bs4 import BeautifulSoup
import re
import time

def scrape_all():
    # URL con filtros aplicados (ejemplo: Departamentos, Venta, CABA)
    url = "https://inmuebles.mercadolibre.com.ar/departamentos/venta/mas-de-2-dormitorios/capital-federal/departamento_NoIndex_True#applied_filter_id%3DBEDROOMS%26applied_filter_name%3DDormitorios%26applied_filter_order%3D2%26applied_value_id%3D%5B2-*%29%26applied_value_name%3D2+dormitorios+o+m%C3%A1s%26applied_value_order%3D3%26applied_value_results%3D30368%26is_custom%3Dfalse"
    
    # Headers mucho más completos para parecer un navegador real
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "es-AR,es;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

    try:
        # Usamos una sesión para manejar cookies automáticamente
        session = requests.Session()
        res = session.get(url, headers=headers, timeout=20)
        
        if res.status_code != 200:
            print(f"❌ ML devolvió error {res.status_code}. Probablemente bloqueo de IP.")
            return []

        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Selector más robusto para los items
        items = soup.find_all('li', class_=re.compile(r'ui-search-layout__item'))
        
        if not items:
            # Si no encuentra por clase, intentamos por selector de jerarquía
            items = soup.select('ol.ui-search-layout li')

        results = []
        print(f"🔎 Analizando {len(items)} posibles resultados...")

        for item in items:
            try:
                # 1. Precio
                p_elem = item.find('span', class_='andes-money-amount__fraction')
                precio = int(p_elem.text.replace('.', '')) if p_elem else 0
                
                # 2. Link
                link_tag = item.find('a', class_='ui-search-link')
                if not link_tag: continue
                link = link_tag['href']
                
                # 3. Título / Zona
                zona = item.find('h2', class_='ui-search-item__title').text if item.find('h2') else "Sin zona"

                # 4. Atributos (Metros y Ambientes)
                attrs = item.find_all('li', class_='ui-search-card-attributes__attribute')
                m2, amb = 0, ""
                for a in attrs:
                    txt = a.text.lower()
                    if "m²" in txt:
                        match = re.search(r'\d+', txt.replace('.',''))
                        if match: m2 = int(match.group())
                    elif "ambiente" in txt:
                        amb = a.text

                if precio > 0: # Filtro básico para evitar basura
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
        print(f"❌ Error en el proceso de scrapeo: {e}")
        return []
