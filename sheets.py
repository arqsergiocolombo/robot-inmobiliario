import os
import json
import requests
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

def enviar_telegram_oportunidad(barrio, precio, link, p_m2):
    # Ahora el código es SEGURO y no genera alertas de GitGuardian
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    if not token or not chat_id:
        print("⚠️ Faltan las llaves de Telegram en los Secrets de GitHub.")
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
        print("🚀 Alerta enviada de forma segura!")
    except Exception as e:
        print(f"❌ Error Telegram: {e}")

def export_to_sheets(data):
    if not data: return
    SPREADSHEET_ID = '1fCjrsBqdjDvkwi7ROKiKcKdAFfDvmetyrP-xsqcFjRg'
    try:
        env_json = os.environ.get('GOOGLE_JSON')
        info = json.loads(env_json)
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

            # SI ES MENOR A 1500 USD/m2, DISPARA TELEGRAM
            if 0 < p_m2 < 1500:
                enviar_telegram_oportunidad(barrio, d['precio'], d['link'], p_m2)

            nuevas_filas.append([fecha_hoy, hora_ahora, barrio, d['precio'], "USD", sup, p_m2, d['ambientes'], d['direccion'], d['link']])

        if nuevas_filas:
            nuevas_filas.append([""] * 10)
            service.spreadsheets().values().append(
                spreadsheetId=SPREADSHEET_ID, range='Sheet1!A2',
                valueInputOption='USER_ENTERED', body={'values': nuevas_filas}).execute()
    except Exception as e:
        print(f"❌ Error: {e}")
