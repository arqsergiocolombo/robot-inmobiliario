import requests
from bs4 import BeautifulSoup
import re

def scrape_all():
    # Buscamos en Palermo, Belgrano y Recoleta hasta 150k
    target_url = "https://www.argenprop.com/departamento-venta-barrio-palermo-barrio-belgrano-barrio-recoleta-hasta-150000-dolares"
    api_key = "eab02f8eb7f617cb6bfd3c2173ed197d" 
    proxy_url = f"http://api.scraperapi.com?api_key={api_key}&url={target_url}&render=true&country_code=ar"

    try:
        print(f"🚀 Iniciando navegación con detector de ambientes avanzado...")
        res = requests.get(proxy_url, timeout=120)
        soup = BeautifulSoup(res.text, 'html.parser')
        items = soup.select('div.listing__item')
        results = []
        
        for item in items:
            try:
                # PRECIO
                p_tag = item.select_one('.card__price')
                if not p_tag: continue
                full_text = p_tag.get_text(strip=True)
                solo_precio = re.search(r'USD\s*([\d\.]+)', full_text)
                if not solo_precio: continue
                precio_final = int(solo_precio.group(1).replace('.', ''))

                # DIRECCIÓN Y LINK
                dir_tag = item.select_one('.card__address')
                direccion = dir_tag.get_text(strip=True) if dir_tag else "CABA"
                a_tag = item.find('a', href=True)
                link = "https://www.argenprop.com" + a_tag['href'] if a_tag else ""

                # --- NUEVA LÓGICA DE AMBIENTES Y M2 ---
                # Buscamos en toda la tarjeta de la propiedad
                texto_tarjeta = item.get_text(" ").lower()
                
                # Buscamos m2
                m2_search = re.search(r'(\d+)\s*m²', texto_tarjeta)
                superficie = m2_search.group(1) if m2_search else "0"
                
                # Buscamos ambientes (ej: "3 amb", "2 ambientes", "1 dorm")
                amb_search = re.search(r'(\d+)\s*(amb|dorm|cuarto)', texto_tarjeta)
                cant_ambientes = amb_search.group(1) if amb_search else "1" # Por defecto 1 si no dice

                results.append({
                    "precio": precio_final,
                    "link": link,
                    "direccion": direccion,
                    "superficie": superficie,
                    "ambientes": cant_ambientes
                })
            except: continue
        return results
    except Exception as e:
        print(f"❌ Error Scraper: {e}")
        return []
