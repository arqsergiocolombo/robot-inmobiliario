import requests
from bs4 import BeautifulSoup
import re

def scrape_all():
    # Tu URL específica de departamentos
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
        
        # --- SELECTORES REFORZADOS PARA INMUEBLES ---
        # Buscamos las "tarjetas" de las propiedades
        items = soup.find_all('div', class_='ui-search-result__content-wrapper')
        if not items:
            items = soup.find_all('div', class_='ui-search-result__wrapper')
        
        print(f"🔎 Analizando {len(items)} propiedades encontradas...")

        results = []
        for item in items:
            try:
                # 1. PRECIO
                price_elem = item.find('span', class_='andes-money-amount__fraction')
                precio = int(price_elem.text.replace('.', '')) if price_elem else 0
                
                # 2. LINK (Buscamos el enlace que envuelve el título o la imagen)
                # En inmuebles, el link suele estar un nivel arriba o en la clase ui-search-link
                link_tag = item.find('a', class_='ui-search-link')
                if not link_tag:
                    # Buscamos en los contenedores padres si no está adentro
                    link_tag = item.find_parent('div', class_='ui-search-result__wrapper').find('a') if item.find_parent('div', class_='ui-search-result__wrapper') else None
                
                link = link_tag['href'] if link_tag else ""
                
                # 3. TÍTULO / ZONA
                zona_tag = item.find('h2', class_='ui-search-item__title')
                zona = zona_tag.text if zona_tag else "CABA"

                # 4. ATRIBUTOS (Metros y Ambientes)
                # En inmuebles suelen estar en una lista con esta clase
                attrs = item.find_all('li', class_='ui-search-card-attributes__attribute')
                m2, amb = 0, ""
                for a in attrs:
                    txt = a.text.lower()
                    if "m²" in txt:
                        m_match = re.search(r'\d+', txt.replace('.',''))
                        if m_match: m2 = int(m_match.group())
                    elif "ambiente" in txt:
                        amb = a.text

                # Si tenemos link y precio, es una propiedad válida
                if link and precio > 0:
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
        print(f"❌ Error crítico: {e}")
        return []
