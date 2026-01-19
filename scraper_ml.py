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
        # Abre el archivo llamado "Inmuebles"
        return client.open("Inmuebles").sheet1 
    except Exception as e:
        print(f"❌ Error al conectar con Sheets: {e}")
        return None

def scrape_all():
    # URL con filtros: Palermo, Belgrano, Recoleta, 2 ambientes, hasta 100k USD
    base_url = "https://www.argenprop.com/departamento-venta-barrio-palermo-barrio-belgrano-barrio-recoleta-2-ambientes-hasta-100000-dolares"
    api_key = "eab02f8eb7f617cb6bfd3c2173ed197d" 
    results = []
    
    print("🔎 Iniciando búsqueda veloz en Argenprop (5 páginas)...")

    for page in range(1, 6): # Optimizado a 5 páginas para evitar el error de tiempo
        target_url = f"{base_url}-pagina-{page}"
        # QUITAMOS el render=true para que el proceso no dure 7 minutos y falle
        proxy_url = f"http://api.scraperapi.com?api_key={api_key}&url={target_url}&country_code=ar"
        
        try:
            res = requests.get(proxy_url, timeout=60)
            soup = BeautifulSoup(res.text, 'html.parser')
            items = soup.select('div.listing__item')
            if not items: break

            for item in items:
                try:
                    # Extracción de Precio
                    p_tag = item.select_one('.card__price')
                    if not p_tag: continue
                    full_text = p_tag.get_text(strip=True)
                    solo_precio = re.search(r'USD\s*([\d\.]+)', full_text)
                    if not solo_precio: continue
                    precio_final = int(solo_precio.group(1).replace('.', ''))
                    
                    # Filtro estricto de 2 AMBIENTES (evita monoambientes)
                    texto_tarjeta = item.get_text(" ").lower()
                    if "1 amb" in texto_tarjeta or "monoambiente" in texto_tarjeta: continue
                    if not re.search(r'(2\s*amb|1\s*dorm|1\s*cuarto)', texto_tarjeta): continue

                    # Filtro de Superficie (+40m2)
                    m2_search = re.search(r'(\d+([.,]\d+)?)\s*m²', texto_tarjeta)
                    superficie = float(m2_search.group(1).replace(',', '.')) if m2_search else 0.0
                    if superficie < 40.0: continue 

                    # Dirección y Barrio
