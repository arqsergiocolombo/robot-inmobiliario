import os
import json
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

def enviar_telegram_oportunidad(barrio, precio, link, p_m2):
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    if not token or not chat_id:
        print("⚠️ Faltan Secrets de Telegram.")
        return

    mensaje = (
        f"🔥 *¡OPORTUNIDAD DETECTADA!* 🔥\n\n"
        f"📍 *Zona:* {barrio}\n"
        f"💰 *Precio:* USD {precio}\n"
        f"📏 *USD/m2:* {p_m2}\n\n"
        f"🔗 [Ver en Argenprop]({link})"
    )
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": mensaje, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=payload, timeout=10)
        print("🚀 Alerta de Telegram enviada!")
    except Exception as e:
        print(f"❌ Error Telegram: {e}")

def export_to_sheets(data):
    if not data: 
        print("⚠️ No hay datos nuevos para subir.")
        return
    
    SPREADSHEET_ID = '1fCjrsBqdjDvkwi7ROKiKcKdAFfDvmetyrP-xsqcFjRg'
    try:
        env_json = os.environ.get('GOOGLE_JSON')
        info = json.loads(env_json)
        creds = service_account.Credentials.from_service_account_info(info)
        service = build('sheets', 'v4', credentials=creds)

        # Obtenemos links existentes para no duplicar
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID, range='Sheet1!J:J').execute()
        links_viejos = [item[0] for item in result.get('values', []) if item]

        fecha_hoy = datetime.now().strftime("%d/%m/%Y")
        hora_ahora = datetime.now().strftime("%H:%M")
        nuevas_filas = []

        for d in data:
            if d['link'] in links_viejos: continue
            
            sup = int(d['superficie'])
            p_m2 = round(d['precio'] / sup, 2) if sup > 0 else 0
            
            # Detectar Barrio
            txt = (d['direccion'] + d['link']).lower()
            barrio = "Palermo" if "palermo" in txt else "Belgrano" if "belgrano" in txt else "Recoleta" if "recoleta" in txt else "CABA"

            # Alerta Telegram si es oportunidad
            if 0 < p_m2 < 1500:
                enviar_telegram_oportunidad(barrio, d['precio'], d['link'], p_m2)

            nuevas_filas.append([fecha_hoy, hora_ahora, barrio, d['precio'], "USD", sup, p_m2, d['ambientes'], d['direccion'], d['link']])

        if nuevas_filas:
            service.spreadsheets().values().append(
                spreadsheetId=SPREADSHEET_ID, range='Sheet1!A2',
                valueInputOption='USER_ENTERED', body={'values': nuevas_filas}).execute()
            print(f"✅ {len(nuevas_filas)} filas subidas a Google Sheets.")
            
    except Exception as e:
        print(f"❌ Error en Sheets: {e}")

def scrape_argenprop():
    # Buscamos en 1 sola página para que sea dinámico y rápido
    api_key = "eab02f8eb7f617cb6bfd3c2173ed197d"
    base_url = "https://www.argenprop.com/departamento-venta-barrio-palermo-barrio-belgrano-barrio-recoleta-2-ambientes-hasta-100000-dolares-pagina-1"
    proxy_url = f"http://api.scraperapi.com?api_key={api_key}&url={base_url}&render=true&country_code=ar"
    
    print("🔎 Iniciando Scrapeo rápido (Página 1)...")
    results = []
    
    try:
        res = requests.get(proxy_url, timeout=120)
        soup = BeautifulSoup(res.text, 'html.parser')
        items = soup.select('div.listing__item')

        for item in items:
            try:
                # Precio
                p_tag = item.select_one('.card__price')
                if not p_tag: continue
                precio_raw = re.search(r'USD\s*([\d\.]+)', p_tag.text)
                if not precio_raw: continue
                precio = int(precio_raw.group(1).replace('.', ''))

                # Superficie y Ambientes
                texto_tarjeta = item.get_text(" ").lower()
                m2_match = re.search(r'(\d+)\s*m²', texto_tarjeta)
                superficie = int(m2_match.group(1)) if m2_match else 0
                
                # Filtro: 2 ambientes y +40m2
                if superficie < 40 or "1 amb" in texto_tarjeta or "monoambiente" in texto_tarjeta:
                    continue

                link = "https://www.argenprop.com" + item.find('a', href=True)['href']
                dir_tag = item.select_one('.card__address')
                direccion = dir_tag.text.strip() if dir_tag else "CABA"

                results.append({
                    'precio': precio,
                    'superficie': superficie,
                    'direccion': direccion,
                    'link': link,
                    'ambientes': "2"
                })
            except: continue
    except Exception as e:
        print(f"❌ Error Request: {e}")
        
    return results

if __name__ == "__main__":
    datos = scrape_argenprop()
    export_to_sheets(datos)
