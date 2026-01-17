import requests
from bs4 import BeautifulSoup
import re

def scrape_all():
    # URL específica de tu búsqueda
    url = "https://inmuebles.mercadolibre.com.ar/departamentos/venta/mas-de-2-dormitorios/capital-federal/departamento_NoIndex_True"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "es-AR,es;q=0.9",
        "Referer": "https://www.google.com/"
    }

    try:
        session = requests.Session()
        res = session.get(url, headers=headers, timeout=20)
        
        print(f"DEBUG - Status: {res.status_code}")
        
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # BUSQUEDA AGRESIVA: Buscamos todos los links que lleven a un anuncio
        # ML usa el patron /MLA- para sus publicaciones
        anuncios = soup.find_all('a', href=re.compile(r'articulo.mercadolibre.com.ar/MLA-'))
        
        # Eliminamos duplicados manteniendo el orden
        links_unicos = []
        for a in anuncios:
            l = a['href'].split('#')[0]
            if l not in links_unicos:
                links_unicos.append(l)

        print(f"🔎 Enlaces de propiedades detectados: {len(links_unicos)}")

        results = []
        # Solo procesamos los primeros para no saturar si hay muchos
        for link in links_unicos[:40]:
            try:
                # Buscamos el contenedor donde esta este link para sacar el precio
                # Subimos hasta encontrar el div que envuelve la tarjeta
                tarjeta = soup.find('a', href=re.compile(re.escape(link))).find_parent(['div', 'li'], class_=re.compile(r'search-result|layout__item'))
                
                if not tarjeta:
                    continue

                # Extraer Precio
                precio_raw = tarjeta.find('span', class_=re.compile(r'fraction|price'))
                if not precio_raw: continue
                precio = int(re.sub(r'\D', '', precio_raw.text))
                
                # Extraer Título/Zona
                titulo = tarjeta.find(['h2', 'h3'])
                zona = titulo.text.strip() if titulo else "CABA"

                # Extraer Metros (buscamos el texto que tenga m²)
                metros = 0
                m2_elem = tarjeta.find(text=re.compile(r'm²'))
                if m2_elem:
                    m_match = re.search(r'\d+', m2_elem.replace('.', ''))
                    if m_match: metros = int(m_match.group())

                results.append({
                    "precio_usd": precio,
                    "link": link,
                    "zona": zona,
                    "metros": metros,
                    "ambientes": "3+ amb"
                })
            except:
                continue
        
        return results

    except Exception as e:
        print(f"❌ Error en el scraper: {e}")
        return []
