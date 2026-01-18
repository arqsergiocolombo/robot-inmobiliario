import requests
from bs4 import BeautifulSoup
import re

def scrape_all():
    target_url = "https://www.argenprop.com/departamento-venta-localidad-capital-federal"
    api_key = "eab02f8eb7f617cb6bfd3c2173ed197d" 
    proxy_url = f"http://api.scraperapi.com?api_key={api_key}&url={target_url}&render=true&country_code=ar"

    try:
        print(f"🚀 Extrayendo precios limpios (sin expensas)...")
        res = requests.get(proxy_url, timeout=120)
        soup = BeautifulSoup(res.text, 'html.parser')
        items = soup.select('div.listing__item')
        results = []
        
        for item in items:
            try:
                # 1. LINK
                a_tag = item.find('a', href=True)
                link = "https://www.argenprop.com" + a_tag['href'] if a_tag else ""

                # 2. PRECIO (Solo el valor de venta principal)
                # Buscamos el elemento que contiene el precio específicamente
                p_tag = item.select_one('p.card__price')
                if not p_tag: continue
                
                # Limpiamos el texto para quedarnos solo con el número de arriba
                # Argenprop suele poner las expensas en un <span> o texto secundario
                precio_raw = p_tag.contents[0] if p_tag.contents else p_tag.get_text()
                precio_limpio = "".join(re.findall(r'\d+', str(precio_raw).replace('.', '')))
                
                # 3. DIRECCIÓN
                dir_tag = item.select_one('.card__address')
                direccion = dir_tag.get_text(strip=True) if dir_tag else "CABA"

                # 4. CARACTERÍSTICAS
                feat_tag = item.select_one('.card__main-features')
                features = feat_tag.get_text(" ") if feat_tag else ""
                
                m2 = re.search(r'(\d+)\s*m²', features)
                amb = re.search(r'(\d+)\s*amb', features)
                
                if precio_limpio:
                    results.append({
                        "precio": int(precio_limpio),
                        "link": link,
                        "direccion": direccion,
                        "superficie": m2.group(1) if m2 else "0",
                        "ambientes": amb.group(1) if amb else "0"
                    })
            except Exception as e:
                continue
        return results
    except Exception as e:
        print(f"❌ Error: {e}")
        return []
