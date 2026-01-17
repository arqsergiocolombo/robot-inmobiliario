import requests
from bs4 import BeautifulSoup
import re

def scrape_all():
    # URL de Argenprop: Departamentos en Venta, 3 ambientes, CABA
    target_url = "https://www.argenprop.com/departamento-venta-localidad-capital-federal-3-ambientes"
    
    # Tu API Key de ScraperAPI
    api_key = "eab02f8eb7f617cb6bfd3c2173ed197d" 
    proxy_url = f"http://api.scraperapi.com?api_key={api_key}&url={target_url}&country_code=ar"

    try:
        print(f"🚀 Iniciando búsqueda en ARGENPROP...")
        res = requests.get(proxy_url, timeout=60)
        
        if res.status_code != 200:
            print(f"❌ Error de conexión con Argenprop: {res.status_code}")
            return []

        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Argenprop usa una clase específica para sus tarjetas
        items = soup.find_all('div', class_='listing__item')
        
        results = []
        for item in items:
            try:
                # 1. PRECIO
                precio_tag = item.find('p', class_='card__price')
                if not precio_tag: continue
                precio_text = precio_tag.get_text().strip()
                
                # Extraemos solo los números (ej: USD 150.000 -> 150000)
                precio_nums = re.findall(r'\d+', precio_text.replace('.', ''))
                if not precio_nums: continue
                precio = int(precio_nums[0])

                # 2. LINK
                a_tag = item.find('a', href=True)
                if not a_tag: continue
                link = "https://www.argenprop.com" + a_tag['href']

                # 3. DIRECCIÓN / ZONA
                direccion = item.find('p', class_='card__address')
                zona = direccion.get_text().strip() if direccion else "CABA"

                # 4. METROS (Opcional, lo intentamos sacar)
                detalles = item.find('ul', class_='card__main-features')
                metros = 0
                if detalles:
                    m2_text = re.search(r'(\d+)\s*m²', detalles.get_text())
                    if m2_text: metros = int(m2_text.group(1))

                if precio > 10000: # Filtro básico
                    results.append({
                        "precio_usd": precio,
                        "link": link,
                        "zona": zona,
                        "metros": metros,
                        "ambientes": "3"
                    })
            except Exception as e:
                continue
        
        print(f"✅ ¡ÉXITO EN ARGENPROP! Se encontraron {len(results)} propiedades.")
        return results

    except Exception as e:
        print(f"❌ Error crítico en scraper: {e}")
        return []
