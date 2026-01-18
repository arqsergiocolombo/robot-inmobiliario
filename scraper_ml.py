import requests
from bs4 import BeautifulSoup
import re

def scrape_all():
    target_url = "https://www.argenprop.com/departamento-venta-barrio-palermo-barrio-belgrano-barrio-recoleta-hasta-150000-dolares"
    api_key = "eab02f8eb7f617cb6bfd3c2173ed197d" 
    proxy_url = f"http://api.scraperapi.com?api_key={api_key}&url={target_url}&render=true&country_code=ar"

    try:
        print(f"🚀 Buscando... (Filtro Ambientes mejorado)")
        res = requests.get(proxy_url, timeout=120)
        soup = BeautifulSoup(res.text, 'html.parser')
        items = soup.select('div.listing__item')
        results = []
        
        for item in items:
            try:
                p_tag = item.select_one('.card__price')
                if not p_tag: continue
                full_text = p_tag.get_text(strip=True)
                solo_precio = re.search(r'USD\s*([\d\.]+)', full_text)
                
                if solo_precio:
                    precio_final = int(solo_precio.group(1).replace('.', ''))
                    if precio_final > 150000: continue
                else: continue

                dir_tag = item.select_one('.card__address')
                direccion = dir_tag.get_text(strip=True) if dir_tag else "CABA"
                a_tag = item.find('a', href=True)
                link = "https://www.argenprop.com" + a_tag['href'] if a_tag else ""

                # --- MEJORA EN AMBIENTES ---
                feat_tag = item.select_one('.card__main-features')
                features = feat_tag.get_text(" ").lower() if feat_tag else ""
                
                m2 = re.search(r'(\d+)\s*m²', features)
                # Buscamos 'amb' o 'ambiente'
                amb = re.search(r'(\d+)\s*amb', features)
                
                results.append({
                    "precio": precio_final,
                    "link": link,
                    "direccion": direccion,
                    "superficie": m2.group(1) if m2 else "0",
                    "ambientes": amb.group(1) if amb else "1" # Si no dice, suele ser monoambiente (1)
                })
            except: continue
        return results
    except Exception as e:
        print(f"❌ Error: {e}")
        return []
