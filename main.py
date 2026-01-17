from scraper_ml import scrape_all
from sheets import append_rows
import sys

def main():
    print("--- 🤖 Iniciando Robot Inmobiliario ---")
    
    propiedades = scrape_all()
    
    if propiedades and len(propiedades) > 0:
        print(f"✅ Éxito: Se encontraron {len(propiedades)} propiedades.")
        append_rows(propiedades)
    else:
        print("❌ El scraper no encontró nada. ML bloqueó la petición o la URL cambió.")
        # Opcional: imprimir el HTML para debug (solo si estás probando)
    
    print("--- 🏁 Fin del proceso ---")

if __name__ == "__main__":
    main()
