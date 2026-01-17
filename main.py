import scraper_ml
import sheets
import time

def run():
    print("--- 🤖 Robot Inmobiliario v2.0 (Argenprop) ---")
    
    # 1. Scrapear
    propiedades = scraper_ml.scrape_all()
    
    # 2. Exportar si hay éxito
    if propiedades:
        sheets.export_to_sheets(propiedades)
    else:
        print("❌ El proceso terminó sin encontrar datos nuevos.")
    
    print("--- 🏁 Fin del proceso ---")

if __name__ == "__main__":
    run()
