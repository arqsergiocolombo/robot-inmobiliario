import requests
from bs4 import BeautifulSoup
import re

def scrape_all():
    # URL de Argenprop (Venta CABA)
    target_url = "https://www.argenprop.com/departamento-venta-localidad-capital-federal"
    api_key = "eab02f8eb7f617cb6bfd3c2173ed197d" 
    
    # ACTIVAMOS EL RENDERIZADO (render=true)
    # Esto simula un navegador real esperando que cargue el contenido
    proxy_url = f"http://api.scraperapi.com?api_key={api_key}&url={target_url}&render=true&country_code=ar"

    try:
        print(f"🚀 Iniciando NAVEGADOR REAL en Argenprop (puede tardar 40s)...")
        # El renderizado es lento, subimos el timeout a 120 segundos
        res = requests.get(proxy_url, timeout=120)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Buscamos los contenedores de las tarjetas de Argenprop
        # Usamos una búsqueda más amplia por clases comunes
        items = soup.select('div.listing__item') or soup.select('div.card')
        
        results = []
        for item in items:
            try:
                # 1. LINK
                a_tag = item.find('a', href=True)
                if not a_tag: continue
                link = "https://www.argenprop.com" + a_tag['href']

                # 2. PRECIO
                # Buscamos cualquier texto que tenga el formato de precio
                texto = item.get_text(separator=' ')
                precios = re.findall(r'\d+(?:\.\d+)+', texto)
                
                if not precios: continue
                valor = int(precios[0].replace('.', ''))

                if valor > 15000:
                    results.append({
                        "precio_usd": valor,
                        "link": link,
                        "zona": "CABA",
                        "metros": 0,
                        "ambientes": "Detectado"
                    })
            except:
                continue

        print(f"✅ ¡RESULTADO FINAL! Propiedades detectadas: {len(results)}")
        return results

    except Exception as e:
        print(f"❌ Error en Argenprop: {e}")
        return []
