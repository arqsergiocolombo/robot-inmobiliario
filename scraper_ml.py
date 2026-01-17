import requests
from bs4 import BeautifulSoup
import re

def scrape_all():
    # Tu URL específica (mantenela tal cual la tenías)
    url = "https://inmuebles.mercadolibre.com.ar/departamentos/venta/mas-de-2-dormitorios/capital-federal/departamento_NoIndex_True"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "es-AR,es;q=0.9",
        "referer": "https://www.google.com/"
    }

    try:
        session = requests.Session()
        res = session.get(url, headers=headers, timeout=20)
        
        # --- DIAGNÓSTICO ---
        if "captcha" in res.text.lower() or "robot" in res.text.lower():
            print("⚠️ BLOQUEO: Mercado Libre detectó el bot y pide Captcha.")
            return []
        
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Intentamos buscar por varios selectores conocidos
        items = soup.find_all('li', class_=re.compile(r'ui-search-layout__item'))
        if not items:
            items = soup.find_all('div', class_='ui-search-result__wrapper')
        if not items:
            items = soup.select('.ui-search-layout__item')

        print(f"🔎 Analizando {len(items)} posibles resultados...")

        results = []
        for item in items:
            try:
                # Precio
                p_text = item.find('span', class_='andes-money-amount__fraction')
                precio = int(p_text.text.replace('.', '')) if p_text else 0
                
                # Link
                link_tag = item.find('a', class_='ui-search-link')
                link = link_tag['href'] if link_tag else ""
                
                # Zona (Extraída del título)
                zona_tag = item.find('h2', class_='ui-search-item__title')
                zona = zona_tag.text if zona_tag else "CABA"

                # Atributos
                attrs = item.find_all('li', class_='ui-search-card-attributes__attribute')
                m2, amb = 0, ""
                for a in attrs:
                    if "m²" in a.text:
                        m2 = int(re.search(r'\d+', a.text.replace('.','')).group())
                    elif "ambiente" in a.text.lower():
                        amb = a.text

                if link and precio > 0:
                    results.append({"precio_usd": precio, "link": link, "zona": zona, "metros": m2, "ambientes": amb})
            except:
                continue
        
        return results

    except Exception as e:
        print(f"❌ Error: {e}")
        return []
print(f"DEBUG - Status Code: {res.status_code}")
print(f"DEBUG - Primeros 200 caracteres: {res.text[:200]}")
