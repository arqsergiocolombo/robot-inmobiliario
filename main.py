import scraper_ml

if __name__ == "__main__":
    print("🚀 Iniciando Robot Inmobiliario...")
    datos = scraper_ml.scrape_run()
    scraper_ml.export_to_sheets(datos)
    print("🏁 Proceso finalizado.")
