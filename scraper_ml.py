import requests
from bs4 import BeautifulSoup
import re

def scrape_all():
    # URL de búsqueda (CABA - Venta)
    target_url = "https://inmuebles.mercadolibre.com.ar/departamentos/venta/capital-federal/"
    
    # Tu API Key de la imagen f398a6
    api_key = "eab02f8eb7f617cb6bfd3c2173ed197d" 
    
    # --- CONFIGURACIÓN PREMIUN ---
    # render=true: Abre un navegador real para que ML no sospeche
    # premium=true: Usa IPs residenciales (más difíciles de bloquear)
    # country_code=ar: Nos posiciona en Argentina
    proxy_url = f"http://api.scraperapi.com?api_key={api_key}&url={target_url}&render=true&premium=true&country_code=ar"

    try:
        print(f"🚀 Iniciando MODO TANQUE (Navegador Real + IP Residencial)...")
        # El renderizado tarda más, por eso subimos el timeout a 120
        res = requests.get(proxy_url, timeout=120)
        
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Buscamos los anuncios por su patrón de ID (MLA)
        anuncios = soup.find_all('a', href=re.compile(r'articulo.mercadolibre.com.ar/MLA-'))
        
        results = []
        links_vistos = set()

        for a in anuncios:
            link = a['href'].split('#')[0]
            if link in links_vistos: continue
            links_vistos.add(link)

            # Buscamos el precio en el texto de la tarjeta
            contenedor = a.find_parent(['div', 'li', 'section'])
            texto = contenedor.get_text(separator=' ') if contenedor else a.get_text()
            
            # Buscamos números con formato 120.000 o similares
            precios = re.findall(r'\d+(?:\.\d+)+', texto)
            
            if precios:
                valor = int(precios[0].replace('.', ''))
                if valor > 20000: # Filtro para evitar avisos falsos
                    results.append({
                        "precio_usd": valor,
                        "link": link,
                        "zona": "CABA",
                        "metros": 0,
                        "ambientes": "Detectado"
                    })

        print(f"✅ ¡RESULTADO REAL! Enlaces encontrados: {len(links_vistos)}")
        print(f"✅ Propiedades listas para enviar al Excel: {len(results)}")
        
        return results

    except Exception as e:
        print(f"❌ Error crítico en el scraper: {e}")
        return []
