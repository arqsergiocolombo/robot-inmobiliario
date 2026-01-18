import os
import json
import requests
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

def enviar_whatsapp_oportunidad(barrio, precio, link, p_m2):
    """
    Envía una alerta a WhatsApp usando CallMeBot.
    """
    # --- CONFIGURACIÓN PERSONAL ---
    # Reemplaza con tu número y la clave que te llegue al WhatsApp
    telefono = "+5491169095680" 
    api_key = "TU_API_KEY_AQUI" 
    
    mensaje = (
        f"🔥 *¡GANGA DETECTADA!* 🔥\n\n"
        f"📍 *Zona:* {barrio}\n"
        f"💰 *Precio:* USD {precio}\n"
        f"📏 *USD/m2:* {p_m2}\n\n"
        f"🔗 *Ver en Argenprop:* {link}"
    )
    
    try:
        url = f"https://api.callmebot.com/whatsapp.php?phone={telefono}&text={mensaje}&apikey={api_key}"
        requests.get(url, timeout=10)
        print(f"📱 Alerta enviada por propiedad en {barrio}")
    except Exception as e:
        print(f"❌ Error enviando WhatsApp: {e}")

def export_to_sheets(data):
    if not data:
        return

    SPREADSHEET_ID = '1fCjrsBqdjDvkwi7ROKiKcKdAFfDvmetyrP-xsqcFjRg'

    try:
        env_json = os.environ.get('GOOGLE_JSON')
        info = json.loads(env_json)
        creds = service_account.Credentials.from_service_account_info(info)
        service = build('sheets', 'v4', credentials=creds)

        # Chequeamos columna J para no repetir
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID, range='Sheet1!J:J'
        ).execute()
        links_viejos = [item[0] for item in result.get('values', []) if item]

        fecha_hoy = datetime.now().strftime("%d/%m/%Y")
        hora_ahora = datetime.now().strftime("%H:%M")
        nuevas_filas = []

        for d in data:
            if d['link'] in links_viejos:
                continue

            sup = int(d['superficie'])
            p_m2 = round(d['precio'] / sup, 2) if sup > 0 else 0
            
            txt = (d['direccion'] + d['link']).lower()
            barrio = "Palermo" if "palermo" in txt else "Belgrano" if "belgrano" in txt else "Recoleta" if "recoleta" in txt else "CABA"

            # --- FILTRO DE OPORTUNIDAD: MENOS DE 1500 USD/m2 ---
            if 0 < p_m2 < 1500:
                enviar_whatsapp_oportunidad(barrio, d['precio'], d['link'], p_m2)

            # Armamos la fila con las 10 columnas
            fila = [
                fecha_hoy, hora_ahora, barrio, d['precio'], "USD", 
                sup, p_m2, d['ambientes'], d['direccion'], d['link']
            ]
            nuevas_filas.append(fila)

        if nuevas_filas:
            nuevas_filas.append([""] * 10)
            service.spreadsheets().values().append(
                spreadsheetId=SPREADSHEET_ID, range='Sheet1!A2',
                valueInputOption='USER_ENTERED', body={'values': nuevas_filas}
            ).execute()
            print(f"📊 Excel actualizado.")

    except Exception as e:
        print(f"❌ Error: {e}")
