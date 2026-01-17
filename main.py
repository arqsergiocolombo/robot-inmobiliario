from scraper_ml import scrape_all
from sheets import append_rows

def main():
    print("--- Iniciando búsqueda ---")
    propiedades = scrape_all()
    
    if propiedades:
        print(f"Se encontraron {len(propiedades)} propiedades.")
        append_rows(propiedades)
    else:
        print("No se encontraron datos nuevos.")
    print("--- Fin del proceso ---")

if __name__ == "__main__":
    main()
