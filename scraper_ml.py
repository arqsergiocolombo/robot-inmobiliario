import requests
from bs4 import BeautifulSoup
import re

def scrape_all():
    # URL de Argenprop (Venta CABA)
    target_url = "https://www.argenprop.com/departamento-venta-localidad-capital-federal"
    api_key = "eab02f8eb7f617cb6bfd3c2173ed197d" 
    
    # Modo Renderizado para cargar precios dinámicos
    proxy_url = f"http://api.scraperapi.com?api_key={api_key}&url={target_url}&render=true&country_code=ar"

    try:
        print(f"🚀 Iniciando navegación real en Argenprop...")
        res = requests.get(proxy_url, timeout=120)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Buscamos las tarjetas de propiedades
        items = soup.select('div.listing__item')
        results = []
        
        for item in items:
            try:
                # Extraer Link
                a_tag = item.find('a', href=True)
                if not a_tag: continue
                link = "https://www.argenprop.com" + a_tag['href']

                # Extraer Precio (buscamos números con puntos)
                texto = item.get_text(separator=' ')
                precios = re.findall(r'\d+(?:\.\d+)+', texto)
                if not precios: continue
                valor = int(precios[0].replace('.', ''))

                if valor > 10000:
                    results.append({
                        "precio_usd": valor,
                        "link": link,
                        "zona": "CABA",
                        "metros": 0,
                        "ambientes": "3"
                    })
            except:
                continue

        print(f"✅ Se detectaron {len(results)} propiedades reales.")
        return results
    except Exception as e:
        print(f"❌ Error en el scraper: {e}")
        return []
