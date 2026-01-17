import requests
from bs4 import BeautifulSoup
import re

def scrape_all():
    # URL con filtros aplicados (Ayuda a saltar bloqueos)
    target_url = "https://inmuebles.mercadolibre.com.ar/departamentos/venta/3-ambientes/capital-federal/belgrano/"
    
    # Tu API Key (de tu imagen image_f398a6.png)
    api_key = "eab02f8eb7f617cb6bfd3c2173ed197d" 
    
    # Configuramos para que use IP de Argentina (AR) para ser menos sospechoso
    proxy_url = f"http://api.scraperapi.com?api_key={api_key}&url={target_url}&country_code=ar"

    try:
        print(f"🚀 Iniciando búsqueda táctica en Belgrano...")
        res = requests.get(proxy_url, timeout=60)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Buscamos cualquier bloque que parezca una tarjeta de propiedad
        items = soup.find_all(['div', 'li', 'section'], class_=re.compile(r'result|item'))
        
        results = []
        for item in items:
            try:
                # Buscamos el link del anuncio
                link_tag = item.find('a', href=re.compile(r'articulo.mercadolibre.com.ar/MLA'))
                if not link_tag: continue
                link = link_tag['href'].split('#')[0]

                # Buscamos el precio (cualquier número con punto cerca de un '$')
                texto_tarjeta = item.get_text()
                # Busca formatos como 120.000 o 1.500.000
                precios = re.findall(r'\d+(?:\.\d+)+', texto_tarjeta)
                
                if not precios: continue
                precio = int(precios[0].replace('.', ''))

                if precio > 10000: # Evitamos traer solo el valor de expensas
                    results.append({
                        "precio_usd": precio,
                        "link": link,
                        "zona": "Belgrano",
                        "metros": 0,
                        "ambientes": "3"
                    })
            except:
                continue
        
        print(f"✅ ¡ÉXITO! Enlaces encontrados: {len(results)}")
        return results

    except Exception as e:
        print(f"❌ Error: {e}")
        return []
