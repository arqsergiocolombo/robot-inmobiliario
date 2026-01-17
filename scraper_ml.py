import requests
from bs4 import BeautifulSoup
import re

def scrape_all():
    # URL de búsqueda base
    target_url = "https://inmuebles.mercadolibre.com.ar/departamentos/venta/capital-federal/"
    
    # Tu API Key de la imagen f398a6
    api_key = "eab02f8eb7f617cb6bfd3c2173ed197d" 
    
    # --- MODO HUMANO (Anti-Bloqueo Total) ---
    # render=true: Abre un Chrome real para cargar todo el contenido (JS)
    # country_code=ar: Nos posiciona en Argentina para evitar sospechas
    proxy_url = f"http://api.scraperapi.com?api_key={api_key}&url={target_url}&render=true&country_code=ar"

    try:
        print(f"🚀 Iniciando MODO HUMANO via ScraperAPI (esto puede tardar)...")
        # El renderizado tarda más, subimos el tiempo de espera a 90 segundos
        res = requests.get(proxy_url, timeout=120)
        
        if res.status_code != 200:
            print(f"❌ Error de ScraperAPI: {res.status_code}")
            return []

        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Buscamos cualquier enlace que lleve a una propiedad (identificados por MLA-)
        anuncios = soup.find_all('a', href=re.compile(r'articulo.mercadolibre.com.ar/MLA-'))
        
        results = []
        links_vistos = set()

        for a in anuncios:
            link = a['href'].split('#')[0]
            if link in links_vistos: continue
            links_vistos.add(link)

            # Buscamos el precio en el texto que rodea al enlace
            contenedor = a.find_parent(['div', 'li', 'section'])
            texto = contenedor.get_text(separator=' ') if contenedor else a.get_text()
            
            # Buscamos números con puntos (ej: 120.000)
            precios = re.findall(r'\d+(?:\.\d+)+', texto)
            
            if precios:
                # El primer número grande suele ser el precio en USD
                valor = int(precios[0].replace('.', ''))
                if valor > 10000:
                    results.append({
                        "precio_usd": valor,
                        "link": link,
                        "zona": "CABA",
                        "metros": 0,
                        "ambientes": "Detectado"
                    })

        # Eliminamos duplicados finales
        final_list = list({v['link']: v for v in results}.values())
        
        print(f"✅ ¡ÉXITO! Enlaces únicos detectados: {len(links_vistos)}")
        print(f"✅ Propiedades reales capturadas: {len(final_list)}")
        
        return final_list

    except Exception as e:
        print(f"❌ Error crítico: {e}")
        return []
