import requests
from bs4 import BeautifulSoup
import re
import os
import psycopg2

def scrape_all():
    base_url = "https://www.argenprop.com/departamento-venta-barrio-palermo-barrio-belgrano-barrio-recoleta-2-ambientes-hasta-100000-dolares"
    api_key = "eab02f8eb7f617cb6bfd3c2173ed197d" 
    results = []

    for page in range(1, 15):
        target_url = f"{base_url}-pagina-{page}"
        proxy_url = f"http://api.scraperapi.com?api_key={api_key}&url={target_url}&render=true&country_code=ar"

        try:
            print(f"🔎 Buscando en Página {page}...")
            res = requests.get(proxy_url, timeout=120)
            soup = BeautifulSoup(res.text, 'html.parser')
            items = soup.select('div.listing__item')
            
            if not items: break

            for item in items:
                try:
                    p_tag = item.select_one('.card__price')
                    if not p_tag: continue
                    full_text = p_tag.get_text(strip=True)
                    solo_precio = re.search(r'USD\s*([\d\.]+)', full_text)
                    if not solo_precio: continue
                    precio_final = int(solo_precio.group(1).replace('.', ''))
                    if precio_final > 100000: continue

                    texto_tarjeta = item.get_text(" ").lower()
                    
                    # Filtro estricto de 2 ambientes
                    if "1 amb" in texto_tarjeta or "monoambiente" in texto_tarjeta:
                        continue
                    
                    es_2_amb = re.search(r'(2\s*amb|1\s*dorm|1\s*cuarto)', texto_tarjeta)
                    if not es_2_amb:
                        continue

                    # Filtro de superficie (+40m2)
                    m2_search = re.search(r'(\d+([.,]\d+)?)\s*m²', texto_tarjeta)
                    superficie = float(m2_search.group(1).replace(',', '.')) if m2_search else 0.0
                    if superficie < 40.0: continue 

                    dir_tag = item.select_one('.card__address')
                    direccion = dir_tag.get_text(strip=True) if dir_tag else "CABA"
                    a_tag = item.find('a', href=True)
                    link = "https://www.argenprop.com" + a_tag['href'] if a_tag else ""

                    results.append({
                        "precio": precio_final,
                        "link": link,
                        "direccion": direccion,
                        "superficie": int(superficie)
                    })
                except: continue
        except Exception as e:
            print(f"❌ Error en página {page}: {e}")
            break
    return results

def actualizar_base_datos(deptos):
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ Error: No se encontró DATABASE_URL.")
        return

    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS propiedades (
            id_link TEXT PRIMARY KEY,
            direccion TEXT,
            precio INT,
            superficie INT,
            fecha_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    nuevos = 0
    rebajas = 0

    for d in deptos:
        cur.execute("SELECT precio FROM propiedades WHERE id_link = %s", (d['link'],))
        resultado = cur.fetchone()
        
        if resultado:
            precio_anterior = resultado[0]
            if d['precio'] < precio_anterior:
                print(f"📉 REBAJA DETECTADA: {d['direccion']} bajó de {precio_anterior} a {d['precio']}")
                cur.execute("UPDATE propiedades SET precio = %s, fecha_update = CURRENT_TIMESTAMP WHERE id_link = %s", 
                            (d['precio'], d['link']))
                rebajas += 1
        else:
            cur.execute("INSERT INTO propiedades (id_link, direccion, precio, superficie) VALUES (%s, %s, %s, %s)",
                        (d['link'], d['direccion'], d['precio'], d['superficie']))
            nuevos += 1
