import requests
from bs4 import BeautifulSoup
import re

def scrape_all():
    target_url = "https://inmuebles.mercadolibre.com.ar/departamentos/venta/mas-de-2-dormitorios/capital-federal/departamento_NoIndex_True"
    api_key = "eab02f8eb7f617cb6bfd3c2173ed197d" 
    proxy_url = f"http://api.scraperapi.com?api_key={api_key}&url={target_url}"

    try:
        print(f"🚀 Iniciando búsqueda invisible via ScraperAPI...")
        res = requests.get(proxy_url, timeout=60)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Estas son las tarjetas que ya detectamos (las 48)
        items = soup.select('div.ui-search-result__wrapper') or soup.select('li.ui-search-layout__item')
        print(f"🔎 Propiedades reales detectadas: {len(items)}")

        results = []
        for item in items:
            try:
                # 1. Extraer Precio (buscamos cualquier número con la clase fraction)
                p_elem = item.find('span', class_=re.compile(r'price-tag-fraction|fraction'))
                if not p_elem: continue
                precio = int(p_elem.text.replace('.', '').strip())
                
                # 2. Extraer Link
                link_tag = item.find('a', class_=re.compile(r'ui-search-link|ui-search-result__content'))
                link = link_tag['href'] if link_tag else ""
                
                # 3. Extraer Zona/Título
                title_tag = item.find(['h2', 'h3'])
                zona = title_tag.text.strip() if title_tag else "CABA"

                if link and precio > 0:
                    results.append({
                        "precio_usd": precio,
                        "link": link,
                        "zona": zona,
                        "metros": 0, 
                        "ambientes": "3+"
                    })
            except:
                continue
        
        # IMPORTANTE: Si llegamos acá y hay resultados, el mensaje de error de abajo no debe salir
        if len(results) > 0:
            print(f"✅ Se procesaron {len(results)} propiedades correctamente.")
        
        return results

    except Exception as e:
        print(f"❌ Error crítico: {e}")
        return []
