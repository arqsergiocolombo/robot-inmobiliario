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
        if not creds_json:
            print("❌ No se encontró GOOGLE_JSON")
            return None
        creds_dict = json.loads(creds_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        # Tu archivo de Google se llama "Inmuebles"
        return client.open("Inmuebles").sheet1 
    except Exception as e:
        print(f"❌ Error Sheets: {e}")
        return None

def scrape_all():
    base_url = "https://www.argenprop.com/departamento-venta-barrio-palermo-barrio-belgrano-barrio-recoleta-2-ambientes-hasta-100000-dolares"
    api_key = "eab02f8eb7f617cb6bfd3c2173ed197d" 
    results = []
    print("🔎 Buscando novedades (5 páginas)...")

    for page in range(1, 6):
        target_url = f"{base_url}-pagina-{page}"
        proxy_url = f"http://api.scraperapi.com?api_key={api_key}&url={target_url}&country_code=ar"
        try:
            res = requests.get(proxy_url, timeout=30)
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
                    if "1 amb" in texto or "monoambiente" in texto: continue
                    if not re.search(r'(2\s*amb|1\s*dorm)', texto): continue
                    
                    m2_search = re.search(r'(\d+)\s*m²', texto)
                    m2 = int(m2_search.group(1)) if m2_search else 0
                    if m2 < 40: continue

                    dir_tag = item.select_one('.card__address')
                    direccion = dir_tag.get_text(strip=True) if dir_tag else "CABA"
                    link = "https://www.argenprop.com" + item.find('a', href=True)['href']
                    
                    results.append({"precio": precio_final, "link": link, "dir": direccion, "m2": m2})
                except:
                    continue
        except Exception as e:
            print(f"Error en pág {page}: {e}")
            break
    return results

def procesar(datos):
    sheet = conectar_sheets()
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ No hay DATABASE_URL")
        return
    
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS propiedades (id_link TEXT PRIMARY KEY, precio INT)")
    
    fecha = datetime.now().strftime("%d/%m/%Y")
    hora = datetime.now().strftime("%H:%M")
    
    for d in datos:
        cur.execute("SELECT precio FROM propiedades WHERE id_link = %s", (d['link'],))
        row = cur.fetchone()
        subir, nota = False, ""
        
        if not row:
            cur.execute("INSERT INTO propiedades (id_link, precio) VALUES (%s, %s)", (d['link'], d['precio']))
            subir = True
        elif d['precio'] < row[0]:
            nota = f"📉 BAJÓ (Era {row[0]})"
            cur.execute("UPDATE propiedades SET precio = %s WHERE id_link = %s", (d['precio'], d['link']))
            subir = True
            
        if subir and sheet:
            fila = [fecha, hora, "Palermo/Bel/Rec", d['precio'], "USD", d['m2'], "", "2", d['dir'], d['link'], nota]
            sheet.append_row(fila)
            print(f"✅ ¡NUEVO!: {d['dir']}")

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    lista = scrape_all()
    if lista:
        procesar(lista)
    print("✅ Proceso terminado.")
