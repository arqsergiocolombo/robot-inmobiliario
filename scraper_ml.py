import requests
from bs4 import BeautifulSoup
import re

def scrape_all():
    # URL de búsqueda
    url = "https://inmuebles.mercadolibre.com.ar/departamentos/venta/mas-de-2-dormitorios/capital-federal/departamento_NoIndex_True"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "es-AR,es;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Referer": "https://www.google.com/"
    }

    try:
        session = requests.Session()
        res = session.get(url, headers=headers, timeout=20)
        
        print(f"DEBUG - Status: {res.status_code}")
        
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # BUSQUEDA UNIVERSAL: Buscamos todos los links que parecen ser de una propiedad
        # Generalmente contienen '/MLA-' o son links de inmuebles
        all_links = soup.find_all('a', href=re.compile(r'articulo.mercadolibre.com.ar/MLA-|/inmuebles/'))
        
        # Filtramos links duplicados y nos quedamos con los contenedores que tienen precio
        results = []
        processed_links = set()

        print(f"🔎 Analizando {len(all_links)} enlaces encontrados...")

        for link_tag in all_links:
            link = link_tag.get('href', '')
            if link in processed_links or 'click1' in link:
                continue
            
            # Buscamos el bloque de información más cercano al link
            # ML suele envolver el precio y el titulo en un contenedor padre
            container = link_tag.find_parent('div', class_=re.compile(r'result|content|wrapper'))
            if not container:
                container = link_tag # Si no hay padre claro, usamos el tag mismo

            try:
                # 1. Precio (Buscamos cualquier número grande con formato de moneda)
                price_text = container.find('span', class_=re.compile(r'price|fraction'))
                if not price_text: continue
                
                precio = int(re.sub(r'\D', '', price_text.text))
                
                # 2. Título / Zona
                title_elem = container.find(['h2', 'h3', 'span'], class_=re.compile(r'title'))
                zona = title_elem.text.strip() if title_elem else "CABA"

                # 3. Atributos (Metros/Ambientes)
                # Buscamos elementos que contengan "m²" o "amb"
                m2, amb = 0, ""
                attr_elements = container.find_all(['li', 'span'], text=re.compile(r'm²|amb|dorm', re.IGNORECASE))
                for attr in attr_elements:
                    txt = attr.text.lower()
                    if "m²" in txt:
                        m_match = re.search(r'\d+', txt.replace('.',''))
                        if m_match: m2 = int(m_match.group())
                    elif "amb" in txt:
                        amb = txt.strip()

                if precio > 5000: # Filtro para evitar avisos basura
                    results.append({
                        "precio_usd": precio,
                        "link": link,
                        "zona": zona,
                        "metros": m2,
                        "ambientes": amb
                    })
                    processed_links.add(link)
            except:
                continue
        
        return results

    except Exception as e:
        print(f"❌ Error crítico: {e}")
        return []
