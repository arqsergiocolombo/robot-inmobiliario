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
        creds_dict = json.loads(os.getenv('GOOGLE_JSON'))
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        # Asegurate que el nombre del archivo sea "Inmuebles"
        return client.open("Inmuebles").sheet1 
    except Exception as e:
        print(f"❌ Error al conectar con Sheets: {e}")
        return None

def scrape_all():
    base_url = "https://www.argenprop.com/departamento-venta-barrio-palermo-barrio-belgrano-barrio-recoleta-2-ambientes-hasta-100000-dolares"
    api_key = "eab02f8eb7f617cb6bfd3c2173ed197d" 
    results = []
    print("🔎 Iniciando búsqueda veloz (5 páginas)...")

    for page in range(1, 6):
        target_url = f"{base_url}-pagina-{page}"
        proxy_url = f"http://api.scraperapi.com?api_key={api_key}&url={target_url}&country_code=ar"
        try:
            res = requests.get(proxy_url, timeout=60)
            soup = BeautifulSoup(res.text, 'html.parser')
            items = soup.select('div.listing__item')
            if not items: break

            for item in items:
                try:
                    p_tag = item.select_one('.card__price')
                    if not p_tag: continue
                    solo_precio = re.search(r'USD\s*([\d\.]+)', p_tag.get_text())
                    if not solo_precio: continue
                    precio_final = int(solo_precio.group(1).replace('.', ''))
                    
                    texto_tarjeta = item.get_text(" ").lower()
                    if "1 amb" in texto_tarjeta or "monoambiente" in texto_tarjeta: continue
                    if not re.search(r'(2\s*amb|1\s*dorm|1\s*cuarto)', texto_tarjeta): continue

                    m2_search = re.search(r'(\d+([.,]\d+)?)\s*m²', texto_tarjeta)
                    superficie = float(m2_search.group(1).replace(',', '.')) if m2_search else 0.0
                    if superficie < 40.0: continue 

                    dir_tag = item.select_one('.card__address')
                    direccion = dir_tag.get_text(strip=True) if dir_tag else "CABA"
                    barrio = "Palermo" if "palermo" in direccion.lower() else "Belgrano" if "belgrano" in direccion.lower() else "Recoleta"
                    link = "https://www.argenprop.com" + item.find('a', href=True)['href']

                    results.append({
                        "precio": precio_final, "link": link, "direccion": direccion, 
                        "superficie": int(superficie), "barrio": barrio
                    })
                except Exception:
                    continue
        except Exception as e:
            print(f"Error en página {page}: {e}")
            break
    return results

def procesar_y_subir(deptos):
    sheet = conectar_sheets()
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ No se encontró DATABASE_URL")
        return
        
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS propiedades (id_link TEXT PRIMARY KEY, precio INT)")
    
    fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    hora_hoy = datetime.now().strftime("%H:%M")

    for d in deptos:
        cur.execute("SELECT precio FROM propiedades WHERE id_link = %s", (d['link'],))
        res = cur.fetchone()
        nota = ""
        debe_subir = False

        if res:
            if d['precio'] < res[0]:
                nota = f"📉 BAJÓ (Era {res[0]})"
                cur.execute("UPDATE propiedades SET precio = %s WHERE id_link = %s", (d['precio'], d['link']))
                debe_subir = True
        else:
            cur.execute("INSERT INTO propiedades (id_link, precio) VALUES (%s, %s)", (d['link'], d['precio']))
            debe_subir = True 

        if debe_subir and sheet:
            precio_m2 = round(d['precio'] / d['superficie'], 2) if d['superficie'] > 0 else 0
            # Columnas: Fecha, Hora, Barrio, Precio, Moneda, Sup, Precio_m2, Amb, Direccion, Link, Nota
            fila = [fecha_hoy, hora_hoy, d['barrio'], d['precio'], "USD", d['superficie'], precio_m2, "2", d['direccion'], d['link'], nota]
            try:
                sheet.append_row(fila)
                print(f"✅ Subido a Sheets: {d['direccion']}")
            except Exception as e:
                print(f"❌ Error al subir fila: {e}")

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    datos = scrape_all()
    if datos:
        procesar_y_subir(datos)
    else:
        print("⚠️ No hay novedades para los filtros aplicados.")
