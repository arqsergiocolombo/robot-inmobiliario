import requests
from bs4 import BeautifulSoup
import re
import os
import psycopg2
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

def conectar_sheets():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        # Usamos el secreto que ya tenés cargado en GitHub
        import json
        creds_dict = json.loads(os.getenv('GOOGLE_JSON'))
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        return client.open("Inmuebles").get_workspace(0) # Asegurate que el nombre sea exacto
    except Exception as e:
        print(f"❌ Error Sheets: {e}")
        return None

def scrape_all():
    base_url = "https://www.argenprop.com/departamento-venta-barrio-palermo-barrio-belgrano-barrio-recoleta-2-ambientes-hasta-100000-dolares"
    api_key = "eab02f8eb7f617cb6bfd3c2173ed197d" 
    results = []
    print("🔎 Iniciando búsqueda en Argenprop...")

    for page in range(1, 10): # Ajustado a 10 para asegurar estabilidad
        target_url = f"{base_url}-pagina-{page}"
        proxy_url = f"http://api.scraperapi.com?api_key={api_key}&url={target_url}&render=true&country_code=ar"
        try:
            res = requests.get(proxy_url, timeout=120)
            soup = BeautifulSoup(res.text, 'html.parser')
            items = soup.select('div.listing__item')
            if not items: break

            for item in items:
                # ... (Lógica de filtrado de 2 amb y +40m2 que ya funcionaba) ...
                # Suponiendo que extraemos: precio, direccion, superficie, link
                results.append({"precio": precio, "dir": direccion, "m2": superficie, "link": link})
        except: continue
    return results

def procesar_todo(deptos):
    sheet = conectar_sheets()
    db_url = os.getenv('DATABASE_URL')
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    hora_hoy = datetime.now().strftime("%H:%M")

    for d in deptos:
        # 1. Verificamos en DB si es nuevo o rebaja
        cur.execute("SELECT precio FROM propiedades WHERE id_link = %s", (d['link'],))
        res = cur.fetchone()
        
        es_nuevo = False
        nota = ""
        
        if res:
            if d['precio'] < res[0]:
                nota = f"📉 BAJÓ de {res[0]}"
                cur.execute("UPDATE propiedades SET precio = %s WHERE id_link = %s", (d['precio'], d['link']))
        else:
            cur.execute("INSERT INTO propiedades (id_link, direccion, precio, superficie) VALUES (%s,%s,%s,%s)",
                        (d['link'], d['dir'], d['precio'], d['m2']))
            es_nuevo = True

        # 2. Si es nuevo o rebaja, lo subimos al Sheets
        if es_nuevo or nota != "":
            # Formato de tu Excel: Fecha, Hora, Barrio, Precio, etc.
            nueva_fila = [fecha_hoy, hora_hoy, "Barrio", d['precio'], "USD", d['m2'], "", d['dir'], d['link'], nota]
            if sheet:
                sheet.append_row(nueva_fila)
                print(f"✅ Subido a Sheets: {d['dir']}")

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    data = scrape_all()
    if data:
        procesar_todo(data)
