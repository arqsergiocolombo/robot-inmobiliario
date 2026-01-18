import requests
from bs4 import BeautifulSoup
import re

def scrape_all():
    target_url = "https://www.argenprop.com/departamento-venta-localidad-capital-federal"
    api_key = "eab02f8eb7f617cb6bfd3c2173ed197d" 
    proxy_url = f"http://api.scraperapi.com?api_key={api_key}&url={target_url}&render=true&country_code=ar"

    try:
        print(f"🚀 Extrayendo datos detallados de Argenprop...")
        res = requests.get(proxy_url, timeout=120)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        items = soup.select('div.listing__item')
        results = []
        
        for item in items:
            try:
                # 1. LINK
                a_tag = item.find('a', href=True)
                if not a_tag: continue
                link = "https://www.argenprop.com" + a_tag['href']

                # 2. PRECIO
                precio_text = item.select_one('.card__price').get_text(strip=True) if item.select_one('.card__price') else ""
                precio = int(re.findall(r'\d+', precio_text.replace('.', ''))[0]) if re.findall(r'\d+', precio_text) else 0

                # 3. DIRECCIÓN / BARRIO
                direccion = item.select_one('.card__address').get_text(strip=True) if item.select_one('.card__address') else "CABA"

                # 4. CARACTERÍSTICAS (m2 y Ambientes)
                # Argenprop pone esto en una lista de iconos
                features = item.select_one('.card__main-features').get_text(" ") if item.select_one('.card__main-features') else ""
                
                # Buscamos metros (ej: 45 m²)
                metros_match = re.search(r'(\d+)\s*m²', features)
                metros = metros_match.group(1) if metros_match else "0"
                
                # Buscamos ambientes (ej: 2 amb.)
                amb_match = re.search(r'(\d+)\s*amb', features)
                ambientes = amb_match.group(1) if amb_match else "3"

                if precio > 10000:
                    results.append({
                        "precio_usd": precio,
                        "link": link,
                        "zona": direccion,
                        "metros": metros,
                        "ambientes": ambientes
                    })
            except:
                continue

        print(f"✅ Se capturaron {len(results)} propiedades con detalles.")
        return results
    except Exception as e:
        print(f"❌ Error en el detallado: {e}")
        return []
