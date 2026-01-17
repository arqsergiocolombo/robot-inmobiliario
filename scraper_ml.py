import requests
from bs4 import BeautifulSoup
import re

def scrape_all():
    # URL de búsqueda (Versión limpia)
    target_url = "https://inmuebles.mercadolibre.com.ar/departamentos/venta/capital-federal/departamento_NoIndex_True"
    
    # Tu API Key de ScraperAPI
    api_key = "eab02f8eb7f617cb6bfd3c2173ed197d" 
    proxy_url = f"http://api.scraperapi.com?api_key={api_key}&url={target_url}"

    try:
        print(f"🚀 Iniciando búsqueda ultra-simple via ScraperAPI...")
        res = requests.get(proxy_url, timeout=60)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Buscamos cualquier bloque que parezca una tarjeta de propiedad
        items = soup.find_all(['div', 'li'], class_=re.compile(r'search-result|ui-search-layout__item'))
        
        results = []
        for item in items:
            try:
                # 1. LINK: Buscamos el primer enlace que tenga 'MLA'
                link_tag = item.find('a', href=re.compile(r'articulo.mercadolibre.com.ar/MLA'))
                if not link_tag: continue
                link = link_tag['href'].split('#')[0]

                # 2. PRECIO: Buscamos cualquier texto con formato de miles (punto en el medio)
                texto = item.get_text()
                # Busca números como 120.000 o 85.500
                numeros = re.findall(r'\d+\.\d+', texto)
                
                if numeros:
                    # Tomamos el primero, le sacamos el punto y lo hacemos número
                    precio = int(numeros[0].replace('.', ''))
                else:
                    continue

                # 3. ZONA: Un valor por defecto si no lo encuentra rápido
                zona = "CABA"
                title_tag = item.find(['h2', 'h3'])
                if title_tag: zona = title_tag.text.strip()

                # Filtro de seguridad para no traer basura
                if precio > 5000:
                    results.append({
                        "precio_usd": precio,
                        "link": link,
                        "zona": zona,
                        "metros": 0,
                        "ambientes": "3+"
                    })
            except:
                continue

        print(f"✅ ¡POR FIN! Se lograron extraer {len(results)} propiedades.")
        return results

    except Exception as e:
        print(f"❌ Error crítico: {e}")
        return []
