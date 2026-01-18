import requests
from bs4 import BeautifulSoup
import re

def scrape_all():
    # URL filtrada: 2 ambientes, Palermo/Belgrano/Recoleta, hasta 100k
    base_url = "https://www.argenprop.com/departamento-venta-barrio-palermo-barrio-belgrano-barrio-recoleta-2-ambientes-hasta-100000-dolares"
    api_key = "eab02f8eb7f617cb6bfd3c2173ed197d" 
    results = []

    # RECORREMOS LAS HOJAS (de la 1 a la 14)
    for page in range(1,1 ):
        target_url = f"{base_url}-pagina-{page}"
        proxy_url = f"http://api.scraperapi.com?api_key={api_key}&url={target_url}&render=true&country_code=ar"

        try:
            print(f"🔎 Buscando en Página {page}...")
            res = requests.get(proxy_url, timeout=120)
            soup = BeautifulSoup(res.text, 'html.parser')
            items = soup.select('div.listing__item')
            
            if not items: 
                print("✅ No hay más páginas.")
                break

            for item in items:
                try:
                    # PRECIO
                    p_tag = item.select_one('.card__price')
                    if not p_tag: continue
                    full_text = p_tag.get_text(strip=True)
                    solo_precio = re.search(r'USD\s*([\d\.]+)', full_text)
                    if not solo_precio: continue
                    precio_final = int(solo_precio.group(1).replace('.', ''))

                    # FILTRO DE PRECIO EXTRA
                    if precio_final > 100000: continue

                    # TEXTO COMPLETO PARA BUSCAR M2 Y AMBIENTES
                    texto_tarjeta = item.get_text(" ").lower()
                    
                    # --- MEJORA: DETECCIÓN DE M2 CON DECIMALES ---
                    # Esta Regex busca números que pueden tener coma o punto (ej: 30,91 o 33.81)
                    m2_search = re.search(r'(\d+([.,]\d+)?)\s*m²', texto_tarjeta)
                    if m2_search:
                        # Reemplazamos coma por punto para que Python lo procese como número
                        valor_limpio = m2_search.group(1).replace(',', '.')
                        superficie = float(valor_limpio)
                    else:
                        superficie = 0.0
                    
                    # FILTRO SUPERFICIE (Mínimo 40m2 reales)
                    if superficie < 40.0: continue 

                    # AMBIENTES (Doble chequeo para 2 amb)
                    amb_search = re.search(r'(\d+)\s*(amb|dorm|cuarto)', texto_tarjeta)
                    cant_ambientes = amb_search.group(1) if amb_search else "2"

                    # DIRECCIÓN Y LINK
                    dir_tag = item.select_one('.card__address')
                    direccion = dir_tag.get_text(strip=True) if dir_tag else "CABA"
                    a_tag = item.find('a', href=True)
                    link = "https://www.argenprop.com" + a_tag['href'] if a_tag else ""

                    results.append({
                        "precio": precio_final,
                        "link": link,
                        "direccion": direccion,
                        "superficie": int(superficie), # Guardamos como entero para el Excel
                        "ambientes": cant_ambientes
                    })
                except: continue
        except Exception as e:
            print(f"❌ Error en página {page}: {e}")
            break

    print(f"🎯 Total de oportunidades reales encontradas (+40m2): {len(results)}")
    return results
