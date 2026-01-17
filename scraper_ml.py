import requests
from bs4 import BeautifulSoup
import re

def scrape_all():
    # URL de ejemplo: Departamentos en venta en CABA. 
    # TIP: Podés cambiar esta URL por la búsqueda exacta con tus filtros.
    url = "https://listado.mercadolibre.com.ar/inmuebles/departamentos/venta/capital-federal/"
    
    # Headers vitales para que Mercado Libre no te bloquee
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept-Language": "es-AR,es;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    print(f"Buscando en: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscamos todos los contenedores de publicaciones
        items = soup.find_all('li', {'class': 'ui-search-layout__item'})
        
        results = []
        for item in items:
            try:
                # Extraer Precio
                price_section = item.find('span', {'class': 'andes-money-amount__fraction'})
                price = int(price_section.text.replace('.', '')) if price_section else None
                
                # Extraer Link
                link_section = item.find('a', {'class': 'ui-search-link'})
                link = link_section['href'] if link_section else ""
                
                # Extraer Título/Zona
                title = item.find('h2', {'class': 'ui-search-item__title'}).text if item.find('h2', {'class': 'ui-search-item__title'}) else ""
                
                # Extraer Metros y Ambientes (Suelen estar en una lista de atributos)
                attributes = item.find_all('li', {'class': 'ui-search-card-attributes__attribute'})
                metros = None
                ambientes = None
                
                for attr in attributes:
                    txt = attr.text.lower()
                    if 'm²' in txt:
                        # Extrae solo los números
                        metros_match = re.search(r'\d+', txt.replace('.', ''))
                        if metros_match:
                            metros = int(metros_match.group())
                    elif 'ambiente' in txt or 'dorm' in txt:
                        ambientes = txt

                results.append({
                    "fuente": "Mercado Libre",
                    "zona": title,
                    "precio_usd": price,
                    "metros": metros,
                    "ambientes": ambientes,
                    "link": link
                })
            except Exception as e:
                print(f"Error procesando una propiedad: {e}")
                continue
                
        return results

    except Exception as e:
        print(f"Error de conexión con Mercado Libre: {e}")
        return []
