import requests
from bs4 import BeautifulSoup
import re

def scrape_all():
    # URL de búsqueda (Versión simplificada)
    target_url = "https://inmuebles.mercadolibre.com.ar/departamentos/venta/capital-federal/departamento_NoIndex_True"
    api_key = "eab02f8eb7f617cb6bfd3c2173ed197d" 
    proxy_url = f"http://api.scraperapi.com?api_key={api_key}&url={target_url}"

    try:
        print(f"🚀 Iniciando extracción cruda via ScraperAPI...")
        res = requests.get(proxy_url, timeout=60)
        
        # Guardamos todo el texto de la página para analizarlo
        html_content = res.text
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 1. Buscamos todos los links que sean de propiedades (MLA)
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if 'articulo.mercadolibre.com.ar/MLA-' in href:
                clean_link = href.split('#')[0]
                if clean_link not in links:
                    links.append(clean_link)

        print(f"DEBUG: Se encontraron {len(links)} enlaces de propiedades.")

        results = []
        # 2. Para cada link, intentamos rescatar el precio que está "cerca" en el HTML
        for link in links:
            # Buscamos el elemento que contiene este link
            anchor = soup.find('a', href=re.compile(re.escape(link)))
            if not anchor: continue
            
            # Subimos al contenedor padre para buscar el precio de esa tarjeta
            parent = anchor.find_parent(['div', 'li'], class_=re.compile(r'result|item'))
            if not parent: parent = anchor.parent.parent # Fallback si no hay clase
            
            texto_busqueda = parent.get_text()
            # Buscamos números con puntos (ej: 125.000)
            precios = re.findall(r'\d+(?:\.\d+)+', texto_busqueda)
            
            if precios:
                # El primer número suele ser el precio en USD
                valor = int(precios[0].replace('.', ''))
                if valor > 10000: # Filtro para ignorar basura
                    results.append({
                        "precio_usd": valor,
                        "link": link,
                        "zona": "CABA",
                        "metros": 0,
                        "ambientes": "3+"
                    })

        # Eliminamos duplicados por link
        final_results = {v['link']: v for v in results}.values()
        
        print(f"✅ ¡ÉXITO! Se extrajeron {len(final_results)} propiedades reales.")
        return list(final_results)

    except Exception as e:
        print(f"❌ Error crítico: {e}")
        return []
