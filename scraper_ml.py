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
        
        # Identificamos las 48 tarjetas que ya vimos que el robot detecta
        items = soup.select('div.ui-search-result__wrapper') or soup.select('li.ui-search-layout__item')
        
        results = []
        for item in items:
            try:
                # 1. EXTRAER PRECIO (Buscamos el texto que tenga el formato de moneda)
                texto_tarjeta = item.get_text()
                # Busca patrones como 150.000 o 1.200.000
                precios = re.findall(r'\d+(?:\.\d+)+', texto_tarjeta)
                
                if not precios: continue
                # El primer número grande suele ser el precio
                precio = int(precios[0].replace('.', ''))
                
                # 2. EXTRAER LINK
                link_tag = item.find('a', href=re.compile(r'articulo.mercadolibre.com.ar/MLA'))
                link = link_tag['href'].split('#')[0] if link_tag else ""
                
                # 3. EXTRAER TÍTULO/ZONA
                title_tag = item.find(['h2', 'h3'])
                zona = title_tag.text.strip() if title_tag else "CABA"

                if link and precio > 10000: # Filtro para evitar avisos falsos
                    results.append({
                        "precio_usd": precio,
                        "link": link,
                        "zona": zona,
                        "metros": 0, 
                        "ambientes": "3+"
                    })
            except:
                continue
        
        if results:
            print(f"✅ ¡ÉXITO! Se procesaron {len(results)} propiedades para el Excel.")
        else:
            print("⚠️ Se detectaron los bloques pero no se pudo extraer la info interna.")
            
        return results

    except Exception as e:
        print(f"❌ Error crítico: {e}")
        return []
