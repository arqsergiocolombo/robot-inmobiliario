import requests
from bs4 import BeautifulSoup
import re

def scrape_all():
    # URL de búsqueda (Versión simplificada)
    target_url = "https://inmuebles.mercadolibre.com.ar/departamentos/venta/capital-federal/"
    api_key = "eab02f8eb7f617cb6bfd3c2173ed197d" 
    
    # Cambiamos la estrategia: Sin renderizado (para que no se apague) 
    # pero con IP Argentina y Ultra-disfraz
    proxy_url = f"http://api.scraperapi.com?api_key={api_key}&url={target_url}&country_code=ar&device_type=mobile"

    try:
        print(f"🚀 Iniciando búsqueda ultra-liviana...")
        res = requests.get(proxy_url, timeout=30)
        
        # Si ScraperAPI nos da un error, lo vemos acá
        if res.status_code != 200:
            print(f"❌ Error de conexión: {res.status_code}")
            return []

        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Buscamos enlaces de publicaciones (MLA)
        # En la versión móvil, los links son la clave
        links = []
        for a in soup.find_all('a', href=True):
            if 'articulo.mercadolibre.com.ar/MLA-' in a['href']:
                links.append(a['href'].split('#')[0])
        
        # Eliminamos duplicados
        links = list(set(links))
        print(f"🔎 Enlaces crudos encontrados: {len(links)}")

        results = []
        for link in links:
            # Para cada link, buscamos un precio en el texto de la página
            # Buscamos el bloque que contiene este link
            elemento = soup.find('a', href=re.compile(re.escape(link)))
            if not elemento: continue
            
            # Buscamos el texto alrededor del link (donde suele estar el precio)
            contenedor = elemento.find_parent(['div', 'li'])
            texto = contenedor.get_text() if contenedor else ""
            
            # Buscamos números con punto (ej: 115.000)
            precios = re.findall(r'\d+(?:\.\d+)+', texto)
            
            if precios:
                valor = int(precios[0].replace('.', ''))
                if valor > 10000:
                    results.append({
                        "precio_usd": valor,
                        "link": link,
                        "zona": "CABA",
                        "metros": 0,
                        "ambientes": "3+"
                    })

        print(f"✅ Proceso terminado. Propiedades listas: {len(results)}")
        return results

    except Exception as e:
        print(f"❌ Error: {e}")
        return []
