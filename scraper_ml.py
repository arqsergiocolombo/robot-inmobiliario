import requests
from bs4 import BeautifulSoup
import re
import os
import psycopg2
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

def conectar_sheets():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_json = os.getenv('GOOGLE_JSON')
        creds_dict = json.loads(creds_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        # Usamos la ID exacta que me pasaste
        return client.open_by_key("1fCjrsBqdjDvkwi7ROKiKcKdAFfDvmetyrP-xsqcFjRg").get_worksheet(0)
    except Exception as e:
        print(f"❌ Error conexión Sheets: {e}")
        return None

def scrape_all():
    base_url = "https://www.argenprop.com/departamento-venta-barrio-palermo-barrio-belgrano-barrio-recoleta-2-ambientes-hasta-100000-dolares"
    api_key = "eab02f8eb7f617cb6bfd3c2173ed197d" 
    results = []
    
    # Recorremos las 15 páginas como pediste
    for page in range(1, 16):
        target_url = f"{base_url}-pagina-{page}"
        # Usamos render=true para asegurar que cargue todo Argenprop
        proxy_url = f"http://api.scraperapi.com?api_key={api_key}&url={target_url}&render=true&country_code=ar"
        
        try:
            print(f"Buscando en página {page}...")
            res = requests.get(proxy_url, timeout=120)
            soup = BeautifulSoup(res.text, 'html.parser')
            items = soup.select('div.listing__item')
            
            if not items: break

            for item in items:
                try:
                    p_tag = item.select_one('.card__price')
                    if not p_tag: continue
                    precio_texto = p_tag.get_text()
                    solo_precio = re.search(r'USD\s*([\d\.]+)', precio_texto)
                    if not solo_precio: continue
                    precio_final = int(solo_precio.group(1).replace('.', ''))

                    texto = item.get_text(" ").lower()
                    # Filtros de 2 ambientes y 40m2
                    if "1 amb" in texto or "monoambiente" in texto: continue
                    if not re.search(r'(2\s*amb|1\s*dorm)', texto): continue
                    
                    m2_search = re.search(r'(\d+)\s*m²', texto)
                    m2 = int(m2_search.group(1)) if m2_search else 0
                    if m2 < 40: continue

                    dir_tag = item.select_one('.card__address')
                    direccion = dir_tag.get_text(strip=True) if dir_tag else "CABA"
                    link = "https://www.argenprop.com" + item.find('a', href=True)['href']
                    
                    results.append({"precio": precio_final, "link": link, "dir": direccion, "m2": m2})
                except: continue
        except Exception as e:
            print(f"Error en página {page}: {e}")
            continue
    return results

def procesar(datos):
    sheet = conectar_sheets()
    db_url = os.getenv('DATABASE_URL')
    if not db_url: return
    
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS propiedades (id_link TEXT PRIMARY KEY, precio INT)")
    
    fecha = datetime.now().strftime("%d/%m/%Y")
    
    for d in datos:
        cur.execute("SELECT precio FROM propiedades WHERE id_link = %s", (d['link'],))
        row = cur.fetchone()
        
        subir = False
        nota = ""
        
        if not row:
            cur.execute("INSERT INTO propiedades (id_link, precio) VALUES (%s, %s)", (d['link'], d['precio']))
            subir = True
        elif d['precio'] < row[0]:
            nota = f"📉 BAJÓ (Era {row[0]})"
            cur.execute("UPDATE propiedades SET precio = %s WHERE id_link = %s", (d['precio'], d['link']))
            subir = True
            
        if subir and sheet:
            # Formato de columnas para tu Sheets
            fila = [fecha, "Palermo/Bel/Rec", d['precio'], d['m2'], d['dir'], d['link'], nota]
            sheet.append_row(fila)
            print(f"✅ Subido: {d['dir']}")

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    lista = scrape_all()
    if lista:
        procesar(lista)
