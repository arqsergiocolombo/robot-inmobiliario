import requests
from bs4 import BeautifulSoup
import re

def scrape_all():
    # URL de departamentos que copiaste
    url = "https://inmuebles.mercadolibre.com.ar/departamentos/venta/mas-de-2-dormitorios/capital-federal/departamento_NoIndex_True"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "es-AR,es;q=0.9",
        "Referer": "https://www.google.com/"
    }

    try:
        session = requests.Session()
        res = session.get(url, headers=headers, timeout=20)
        
        # Log de diagnóstico para Railway
        print(f"DEBUG - Status: {res.status_code}")
        
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Buscamos todos los bloques que contienen una propiedad
        # En Inmuebles, suelen ser 'ui-search-result__wrapper' o 'ui-search-result__content'
        items = soup.find_all('div', class_=re.compile(r'ui-search-result__(wrapper|content)'))
        
        # Si falla, buscamos etiquetas de lista (plan B)
        if not items:
            items = soup.find_all('li', class_=re.compile(r'ui-search-layout__item'))

        print(f"🔎 Analizando {len(items)} propiedades encontradas...")

        results = []
        for item in items:
            try:
                # 1. Extraer Precio (buscamos la fracción numérica)
                price_text = item.find('span', class_='andes-money-amount__fraction')
                if not price_text: continue
                precio = int(price_text.text.replace('.', ''))
                
                # 2. Extraer Link
                link_tag = item.find('a', class_='ui-search-link')
                link = link_tag['href'] if link_tag else ""
                
                # 3. Título / Zona
                title_tag = item.find('h2', class_=re.compile(r'title'))
                zona = title_tag.text.strip() if title_tag else "CABA"

                # 4. Atributos (Metros y Ambientes)
                # Buscamos etiquetas <li> que contengan "m²" o "amb"
                m2, amb = 0, ""
                attrs = item.find_all(['li', 'span'], class_=re.compile(r'attributes__attribute'))
                for a in attrs:
                    txt = a.text.lower()
                    if "m²" in txt:
                        match = re.search(r'\d+', txt.replace('.',''))
                        if match: m2 = int(match.group())
                    elif "amb" in txt:
                        amb = txt.strip()

                if link and precio > 0:
                    results.append({
                        "precio_usd": precio,
                        "link": link,
                        "zona": zona,
                        "metros": m2,
                        "ambientes": amb
                    })
            except:
                continue
        
        return results

    except Exception as e:
        print(f"❌ Error crítico: {e}")
        return []
