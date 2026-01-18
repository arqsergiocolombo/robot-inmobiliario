import requests
from bs4 import BeautifulSoup
import re

def scrape_all():
    target_url = "https://www.argenprop.com/departamento-venta-localidad-capital-federal"
    api_key = "eab02f8eb7f617cb6bfd3c2173ed197d" 
    proxy_url = f"http://api.scraperapi.com?api_key={api_key}&url={target_url}&render=true&country_code=ar"

    try:
        print(f"🚀 Iniciando extracción quirúrgica de precios...")
        res = requests.get(proxy_url, timeout=120)
        soup = BeautifulSoup(res.text, 'html.parser')
        items = soup.select('div.listing__item')
        results = []
        
        for item in items:
            try:
                # 1. LINK
                a_tag = item.find('a', href=True)
                link = "https://www.argenprop.com" + a_tag['href'] if a_tag else ""

                # 2. PRECIO (FILTRO ANTI-EXPENSAS MEJORADO)
                p_tag = item.select_one('.card__price')
                if not p_tag: continue
                
                # Buscamos el texto que contiene 'USD' y tomamos solo la primera cifra
                full_text = p_tag.get_text(strip=True) # Trae ej: "USD130.000+$160.000expensas"
                
                # Esta expresión regular busca solo el primer número largo después de USD
                solo_precio = re.search(r'USD\s*([\d\.]+)', full_text)
                if solo_precio:
                    precio_final = int(solo_precio.group(1).replace('.', ''))
                else:
                    # Si no encuentra USD, intentamos solo con el primer grupo de números
                    precio_final = int(re.findall(r'\d+', full_text.replace('.', ''))[0])

                # 3. DIRECCIÓN
                dir_tag = item.select_one('.card__address')
                direccion = dir_tag.get_text(strip=True) if dir_tag else "CABA"

                # 4. CARACTERÍSTICAS
                feat_tag = item.select_one('.card__main-features')
                features = feat_tag.get_text(" ") if feat_tag else ""
                
                m2 = re.search(r'(\d+)\s*m²', features)
                amb = re.search(r'(\d+)\s*amb', features)
                
                results.append({
                    "precio": precio_final,
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
