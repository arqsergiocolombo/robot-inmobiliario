import requests
from bs4 import BeautifulSoup
import re

def scrape_all():
    # URL de búsqueda (Versión limpia)
    target_url = "https://inmuebles.mercadolibre.com.ar/departamentos/venta/capital-federal/departamento_NoIndex_True"
    
    # Tu API Key de ScraperAPI
    api_key = "eab02f8eb7f617cb6bfd3c2173ed197d" 
    
    # --- CONFIGURACIÓN DE ALTA SEGURIDAD ---
    # country_code=ar -> Usa una dirección IP de Argentina
    # device_type=mobile -> Se disfraza de celular (iPhone/Android)
    proxy_url = f"http://api.scraperapi.com?api_key={api_key}&url={target_url}&country_code=ar&device_type=mobile"

    try:
        print(f"🚀 Iniciando extracción MÓVIL (iPhone Mode) via ScraperAPI...")
        res = requests.get(proxy_url, timeout=60)
        
        # Analizamos el contenido buscando enlaces de anuncios (MLA)
        soup = BeautifulSoup(res.text, 'html.parser')
        anuncios = soup.find_all('a', href=re.compile(r'MLA-\d+'))
        
        results = []
        links_vistos = set()

        for a in anuncios:
            link = a['href'].split('#')[0]
            if link in links_vistos: continue
            links_vistos.add(link)

            # Buscamos el precio en el texto de ese link o de su contenedor padre
            texto_contexto = a.get_text(separator=' ')
            if len(texto_contexto) < 5: 
                parent = a.parent
                texto_contexto = parent.get_text(separator=' ') if parent else ""

            # Buscamos números con puntos (ej: 140.000)
            precios = re.findall(r'\d+(?:\.\d+)+', texto_contexto)
            
            if precios:
                # El primer número suele ser el precio en USD
                valor = int(precios[0].replace('.', ''))
                if valor > 15000: # Filtro para ignorar expensas o datos basura
                    results.append({
                        "precio_usd": valor,
                        "link": link,
                        "zona": "CABA",
                        "metros": 0,
                        "ambientes": "3+"
                    })

        print(f"✅ ¡POR FIN! Enlaces únicos detectados: {len(links_vistos)}")
        print(f"✅ Propiedades procesadas para el Excel: {len(results)}")
        
        return results

    except Exception as e:
        print(f"❌ Error crítico: {e}")
        return []
