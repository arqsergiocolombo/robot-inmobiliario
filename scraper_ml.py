import requests
from bs4 import BeautifulSoup
import re

def scrape_all():
    # URL de búsqueda (Departamentos en CABA)
    url = "https://listado.mercadolibre.com.ar/inmuebles/departamentos/venta/capital-federal/"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "es-AR,es;q=0.9",
        "Referer": "https://www.google.com/"
    }

    print(f"Buscando en: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"Error de acceso: Código {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Selectores actualizados 2024/2025
        # Buscamos por la clase que envuelve cada tarjeta de propiedad
        items = soup.select('li.ui-search-layout__item') or soup.select('div.ui-search-result__wrapper')
        
        results = []
        for item in items:
            try:
                # 1. PRECIO (Buscamos el símbolo $ y el número)
                price_elem = item.select_one('.andes-money-amount__fraction')
                price = int(price_elem.text.replace('.', '')) if price_elem else None
                
                # 2. LINK Y TÍTULO
                link_elem = item.select_one('a.ui-search-link')
                link = link_elem['href'] if link_elem else ""
                title = link_elem.get('title', '') if link_elem else ""
                
                # Si no hay título en el link, buscamos en el h2
                if not title:
                    h2 = item.select_one('h2.ui-search-item__title')
                    title = h2.text if h2 else "Sin título"

                # 3. METROS Y AMBIENTES (Atributos)
                attrs = item.select('.ui-search-card-attributes__attribute')
                metros = None
                ambientes = None
                
                for a in attrs:
                    text = a.text.lower()
                    if 'm²' in text:
                        m_match = re.search(r'\d+', text.replace('.', ''))
                        if m_match: metros = int(m_match.group())
                    elif 'ambiente' in text:
                        amb_match = re.search(r'\d+', text)
                        if amb_match: ambientes = amb_match.group()

                if link: # Solo agregamos si encontramos al menos el link
                    results.append({
                        "fuente": "Mercado Libre",
                        "zona": title,
                        "precio_usd": price,
                        "metros": metros,
                        "ambientes": ambientes,
                        "link": link
                    })
            except Exception as e:
                continue
                
        return results

    except Exception as e:
        print(f"Error en el scraper: {e}")
        return []import requests
from bs4 import BeautifulSoup
import re

def scrape_all():
    # URL de búsqueda (Departamentos en CABA)
    url = "https://listado.mercadolibre.com.ar/inmuebles/departamentos/venta/capital-federal/"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "es-AR,es;q=0.9",
        "Referer": "https://www.google.com/"
    }

    print(f"Buscando en: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"Error de acceso: Código {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Selectores actualizados 2024/2025
        # Buscamos por la clase que envuelve cada tarjeta de propiedad
        items = soup.select('li.ui-search-layout__item') or soup.select('div.ui-search-result__wrapper')
        
        results = []
        for item in items:
            try:
                # 1. PRECIO (Buscamos el símbolo $ y el número)
                price_elem = item.select_one('.andes-money-amount__fraction')
                price = int(price_elem.text.replace('.', '')) if price_elem else None
                
                # 2. LINK Y TÍTULO
                link_elem = item.select_one('a.ui-search-link')
                link = link_elem['href'] if link_elem else ""
                title = link_elem.get('title', '') if link_elem else ""
                
                # Si no hay título en el link, buscamos en el h2
                if not title:
                    h2 = item.select_one('h2.ui-search-item__title')
                    title = h2.text if h2 else "Sin título"

                # 3. METROS Y AMBIENTES (Atributos)
                attrs = item.select('.ui-search-card-attributes__attribute')
                metros = None
                ambientes = None
                
                for a in attrs:
                    text = a.text.lower()
                    if 'm²' in text:
                        m_match = re.search(r'\d+', text.replace('.', ''))
                        if m_match: metros = int(m_match.group())
                    elif 'ambiente' in text:
                        amb_match = re.search(r'\d+', text)
                        if amb_match: ambientes = amb_match.group()

                if link: # Solo agregamos si encontramos al menos el link
                    results.append({
                        "fuente": "Mercado Libre",
                        "zona": title,
                        "precio_usd": price,
                        "metros": metros,
                        "ambientes": ambientes,
                        "link": link
                    })
            except Exception as e:
                continue
                
        return results

    except Exception as e:
        print(f"Error en el scraper: {e}")
        return []
