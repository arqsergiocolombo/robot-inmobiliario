import requests
from bs4 import BeautifulSoup
import re
import os
import psycopg2
from twilio.rest import Client

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
                    # PRECIO
                    p_tag = item.select_one('.card__price')
                    if not p_tag: continue
                    full_text = p_tag.get_text(strip=True)
                    solo_precio = re.search(r'USD\s*([\d\.]+)', full_text)
                    if not solo_precio: continue
                    precio_final = int(solo_precio.group(1).replace('.', ''))
                    if precio_final > 100000: continue

                    # TEXTO PARA FILTROS
                    texto_tarjeta = item.get_text(" ").lower()
                    
                    # --- MEJORA: FILTRO ESTRICTO DE 2 AMBIENTES ---
                    # Si dice "1 amb" o "monoambiente", lo salteamos
                    if "1 amb" in texto_tarjeta or "monoambiente" in texto_tarjeta:
                        continue
                    
                    # Buscamos que explícitamente diga 2 ambientes o 1 dormitorio
                    es_2_amb = re.search(r'(2\s*amb|1\s*dorm|1\s*cuarto|2\s*viviendas)', texto_tarjeta)
                    if not es_2_amb:
                        continue

                    # SUPERFICIE
                    m2_search = re.search(r'(\d+([.,]\d+)?)\s*m²', texto_tarjeta)
                    if m2_search:
                        valor_limpio = m2_search.group(1).replace(',', '.')
                        superficie = float(valor_limpio)
                    else:
                        superficie = 0.0
                    
                    if superficie < 40.0: continue 

                    # DIRECCIÓN Y LINK
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

def procesar_y_detectar_rebajas(deptos):
    db_url = os.getenv('DATABASE_URL')
    if not db_url: return 0, []

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
    
    nuevos_hallazgos = 0
    lista_rebajas = []

    for d in deptos:
        cur.execute("SELECT precio FROM propiedades WHERE id_link = %s", (d['link'],))
        resultado = cur.fetchone()
        
        if resultado:
            precio_anterior = resultado[0]
            if d['precio'] < precio_anterior:
                lista_rebajas.append(f"📉 *{d['direccion']}*\nBajó de USD {precio_anterior} a *USD {d['precio']}*")
                cur.execute("UPDATE propiedades SET precio = %s, fecha_update = CURRENT_TIMESTAMP WHERE id_link = %s", 
                            (d['precio'], d['link']))
        else:
            cur.execute("INSERT INTO propiedades (id_link, direccion, precio, superficie) VALUES (%s, %s, %s, %s)",
                        (d['link'], d['direccion'], d['precio'], d['superficie']))
            nuevos_hallazgos += 1
            
    conn.commit()
    cur.close()
    conn.close()
    return nuevos_hallazgos, lista_rebajas

def enviar_whatsapp(nuevos, rebajas):
    sid = os.getenv('TWILIO_SID')
    token = os.getenv('TWILIO_TOKEN')
    destino = os.getenv('MY_PHONE')
    client = Client(sid, token)

    # CORRECCIÓN DE SINTAXIS AQUÍ (Se cerró la llave correctamente)
    msj = f"🏠 *INFORME INTELIGENTE*\n\n✅ Se encontraron *{nuevos}* propiedades nuevas (+40m2 y 2 amb)."
    
    if rebajas:
        msj += "\n\n🚨 *DETECCIÓN DE REBAJAS:*\n" + "\n".join(rebajas)
    
    msj += "\n\n📊 Historial actualizado en Railway."

    try:
        client.messages.create(from_='whatsapp:+14155238886', body=msj, to=f"whatsapp:{destino}")
        print("✅ WhatsApp enviado.")
    except Exception as e:
        print(f"❌ Error WhatsApp: {e}")

if __name__ == "__main__":
    lista = scrape_all()
    if lista:
        n, r = procesar_y_detectar_rebajas(lista)
        enviar_whatsapp(n, r)
    else:
        print("⚠️ No hay novedades que cumplan los filtros hoy.")
