import requests
from bs4 import BeautifulSoup
import re
import os
from twilio.rest import Client

def scrape_all():
    # URL filtrada: 2 ambientes, Palermo/Belgrano/Recoleta, hasta 100k
    base_url = "https://www.argenprop.com/departamento-venta-barrio-palermo-barrio-belgrano-barrio-recoleta-2-ambientes-hasta-100000-dolares"
    api_key = "eab02f8eb7f617cb6bfd3c2173ed197d" 
    results = []

    # RECORREMOS LAS HOJAS (de la 1 a la 14 para un barrido total)
    for page in range(1, 15):
        target_url = f"{base_url}-pagina-{page}"
        proxy_url = f"http://api.scraperapi.com?api_key={api_key}&url={target_url}&render=true&country_code=ar"

        try:
            print(f"🔎 Buscando en Página {page}...")
            res = requests.get(proxy_url, timeout=120)
            soup = BeautifulSoup(res.text, 'html.parser')
            items = soup.select('div.listing__item')
            
            if not items: 
                print("✅ No hay más páginas.")
                break

            for item in items:
                try:
                    # PRECIO
                    p_tag = item.select_one('.card__price')
                    if not p_tag: continue
                    full_text = p_tag.get_text(strip=True)
                    solo_precio = re.search(r'USD\s*([\d\.]+)', full_text)
                    if not solo_precio: continue
                    precio_final = int(solo_precio.group(1).replace('.', ''))

                    # FILTRO DE PRECIO EXTRA
                    if precio_final > 100000: continue

                    # TEXTO COMPLETO PARA BUSCAR M2 Y AMBIENTES
                    texto_tarjeta = item.get_text(" ").lower()
                    
                    # --- MEJORA: DETECCIÓN DE M2 CON DECIMALES ---
                    m2_search = re.search(r'(\d+([.,]\d+)?)\s*m²', texto_tarjeta)
                    if m2_search:
                        valor_limpio = m2_search.group(1).replace(',', '.')
                        superficie = float(valor_limpio)
                    else:
                        superficie = 0.0
                    
                    # FILTRO SUPERFICIE (Mínimo 40m2 reales)
                    if superficie < 40.0: continue 

                    # AMBIENTES
                    amb_search = re.search(r'(\d+)\s*(amb|dorm|cuarto)', texto_tarjeta)
                    cant_ambientes = amb_search.group(1) if amb_search else "2"

                    # DIRECCIÓN Y LINK
                    dir_tag = item.select_one('.card__address')
                    direccion = dir_tag.get_text(strip=True) if dir_tag else "CABA"
                    a_tag = item.find('a', href=True)
                    link = "https://www.argenprop.com" + a_tag['href'] if a_tag else ""

                    results.append({
                        "precio": precio_final,
                        "link": link,
                        "direccion": direccion,
                        "superficie": int(superficie),
                        "ambientes": cant_ambientes
                    })
                except: continue
        except Exception as e:
            print(f"❌ Error en página {page}: {e}")
            break

    print(f"🎯 Total de oportunidades reales encontradas (+40m2): {len(results)}")
    return results

def enviar_whatsapp(total):
    # Traemos las credenciales desde los Secrets de GitHub cargados en auto_run.yml
    sid = os.getenv('TWILIO_SID')
    token = os.getenv('TWILIO_TOKEN')
    destino = os.getenv('MY_PHONE')
    
    if not sid or not token or not destino:
        print("❌ Error: Faltan las credenciales de Twilio en los Secrets.")
        return

    client = Client(sid, token)

    texto = (
        f"🏠 *INFORME INMOBILIARIO CRÍTICO*\n\n"
        f"Hola Sergio, el robot acaba de reiniciar el sistema.\n\n"
        f"🎯 Se detectaron *{total} departamentos* que cumplen con >40m2 y <USD 100k.\n\n"
        f"📊 Al estar el Excel limpio, estos son todos los resultados actuales."
    )

    try:
        message = client.messages.create(
            from_='whatsapp:+14155238886', # Sandbox de Twilio
            body=texto,
            to=f'whatsapp:{destino}'
        )
        print(f"✅ WhatsApp enviado con éxito: {message.sid}")
    except Exception as e:
        print(f"❌ Error al enviar WhatsApp: {e}")

# --- PUNTO DE EJECUCIÓN PRINCIPAL ---
if __name__ == "__main__":
    # 1. Ejecutamos el scraping
    lista_deptos = scrape_all()
    
    # 2. Si encontró resultados, enviamos el mensaje
    if len(lista_deptos) > 0:
        enviar_whatsapp(len(lista_deptos))
    else:
        print("⚠️ No se encontraron propiedades que superen los 40m2 en este barrido.")
