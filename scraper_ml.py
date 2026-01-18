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
                link = "https://www.argenprop.com" + a_tag['href'] if a_tag else ""

                # 2. PRECIO (Solo números)
                p_tag = item.select_one('.card__price')
                precio_raw = p_tag.get_text(strip=True) if p_tag else "0"
                precio = "".join(re.findall(r'\d+', precio_raw.replace('.', '')))
                
                # 3. DIRECCIÓN
                dir_tag = item.select_one('.card__address')
                direccion = dir_tag.get_text(strip=True) if dir_tag else "CABA"

                # 4. CARACTERÍSTICAS (m2 y Ambientes)
                feat_tag = item.select_one('.card__main-features')
                features = feat_tag.get_text(" ") if feat_tag else ""
                
                m2 = re.search(r'(\d+)\s*m²', features)
                amb = re.search(r'(\d+)\s*amb', features)
                
                results.append({
                    "precio": int(precio) if precio else 0,
                    "link": link,
                    "direccion": direccion,
                    "superficie": m2.group(1) if m2 else "0",
                    "ambientes": amb.group(1) if amb else "0"
                })
            except:
                continue
        return results
    except Exception as e:
        print(f"❌ Error: {e}")
        return []
