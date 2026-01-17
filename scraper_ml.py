import requests
from bs4 import BeautifulSoup
import re

def scrape_all():
    # URL de Argenprop (Departamentos en Venta, CABA)
    target_url = "https://www.argenprop.com/departamento-venta-localidad-capital-federal"
    api_key = "eab02f8eb7f617cb6bfd3c2173ed197d" 
    
    # Usamos ScraperAPI con IP de Argentina
    proxy_url = f"http://api.scraperapi.com?api_key={api_key}&url={target_url}&country_code=ar"

    try:
        print(f"🚀 Iniciando búsqueda en ARGENPROP...")
        res = requests.get(proxy_url, timeout=60)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Buscamos cualquier enlace que lleve a un detalle de propiedad
        # Argenprop usa links que contienen "/departamento-venta-"
        anuncios = soup.find_all('a', href=re.compile(r'/departamento-venta-'))
        
        results = []
        links_vistos = set()

        for a in anuncios:
            link_relativo = a['href']
            if link_relativo in links_vistos: continue
            links_vistos.add(link_relativo)
            
            link_completo = "https://www.argenprop.com" + link_relativo

            # Intentamos rescatar el precio del texto del anuncio
            texto_tarjeta = a.get_text(separator=' ')
            # Busca números grandes (ej: 120.000)
            precios = re.findall(r'\d+(?:\.\d+)+', texto_tarjeta)
            
            if precios:
                valor = int(precios[0].replace('.', ''))
                if valor > 10000:
                    results.append({
                        "precio_usd": valor,
                        "link": link_completo,
                        "zona": "CABA",
                        "metros": 0,
                        "ambientes": "Detectado"
                    })

        if results:
            print(f"✅ ¡ÉXITO! Se extrajeron {len(results)} propiedades de Argenprop.")
        else:
            print("⚠️ Argenprop cargó pero no pudimos leer los precios. Reintentando...")
            
        return results

    except Exception as e:
        print(f"❌ Error en Argenprop: {e}")
        return []
