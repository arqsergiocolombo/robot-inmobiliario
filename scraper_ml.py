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
        
        # Estas son las 48 tarjetas que ya vimos que detecta
        items = soup.select('div.ui-search-result__wrapper') or soup.select('li.ui-search-layout__item')
        
        results = []
        for item in items:
            try:
                # 1. PRECIO: Buscamos cualquier número que tenga puntos (ej: 120.000)
                # ML suele poner el precio en spans con clases que cambian, así que buscamos el texto
                texto_item = item.get_text()
                precios_encontrados = re.findall(r'\d+\.\d+', texto_item)
                
                if precios_encontrados:
                    # Tomamos el primero que suele ser el precio principal y le quitamos el punto
                    precio = int(precios_encontrados[0].replace('.', ''))
                else:
                    # Plan B para el precio
                    p_tag = item.find('span', class_=re.compile(r'fraction|price'))
                    if not p_tag: continue
                    precio = int(p_tag.text.replace('.', ''))

                # 2. LINK: Buscamos el enlace al artículo
                link_tag = item.find('a', href=re.compile(r'articulo.mercadolibre.com.ar/MLA'))
                link = link_tag['href'].split('#')[0] if link_tag else ""
                
                # 3. ZONA
                zona_tag = item.find(['h2', 'h3'])
                zona = zona_tag.text.strip() if zona_tag else "CABA"

                if link and precio > 5000: # Filtro para evitar captar expensas o basura
                    results.append({
                        "precio_usd": precio,
                        "link": link,
                        "zona": zona,
                        "metros": 0, 
                        "ambientes": "3+"
                    })
            except:
                continue
        
        print(f"✅ ¡ÉXITO! Se procesaron {len(results)} propiedades para el Excel.")
        return results

    except Exception as e:
        print(f"❌ Error crítico: {e}")
        return []
