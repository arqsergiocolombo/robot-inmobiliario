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
    if not token or not chat_id: return

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
    except: pass

def export_to_sheets(data):
    if not data: return
    SPREADSHEET_ID = '1fCjrsBqdjDvkwi7ROKiKcKdAFfDvmetyrP-xsqcFjRg'
    try:
        info = json.loads(os.environ.get('GOOGLE_JSON'))
        creds = service_account.Credentials.from_service_account_info(info)
        service = build('sheets', 'v4', credentials=creds)

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
            txt = (d['direccion'] + d['link']).lower()
            barrio = "Palermo" if "palermo" in txt else "Belgrano" if "belgrano" in txt else "Recoleta" if "recoleta" in txt else "CABA"

            if 0 < p_m2 < 1500:
                enviar_telegram_oportunidad(barrio, d['precio'], d['link'], p_m2)

            nuevas_filas.append([fecha_hoy, hora_ahora, barrio, d['precio'], "USD", sup, p_m2, d['ambientes'], d['direccion'], d['link']])

        if nuevas_filas:
            service.spreadsheets().values().append(
                spreadsheetId=SPREADSHEET_ID, range='Sheet1!A2',
                valueInputOption='USER_ENTERED', body={'values': nuevas_filas}).execute()
            print(f"✅ {len(nuevas_filas)} propiedades nuevas subidas.")
    except Exception as e:
        print(f"❌ Error Sheets: {e}")

def scrape_run():
    api_key = "eab02f8eb7f617cb6bfd3c2173ed197d"
    # Cambiado a Página 1 para prueba rápida
    url = "https://www.argenprop.com/departamento-venta-barrio-palermo-barrio-belgrano-barrio-recoleta-2-ambientes-hasta-100000-dolares-pagina-1"
    proxy = f"http://api.scraperapi.com?api_key={api_key}&url={url}&render=true&country_code=ar"
    
    results = []
    try:
        res = requests.get(proxy, timeout=120)
        soup = BeautifulSoup(res.text, 'html.parser')
        for item in soup.select('div.listing__item'):
            try:
                p_tag = item.select_one('.card__price')
                precio = int(re.search(r'USD\s*([\d\.]+)', p_tag.text).group(1).replace('.', ''))
                texto = item.get_text(" ").lower()
                m2 = int(re.search(r'(\d+)\s*m²', texto).group(1))
                if m2 < 40 or "1 amb" in texto: continue
                link = "https://www.argenprop.com" + item.find('a', href=True)['href']
                direccion = item.select_one('.card__address').text.strip()
                results.append({'precio': precio, 'superficie': m2, 'direccion': direccion, 'link': link, 'ambientes': "2"})
            except: continue
    except: pass
    return results
