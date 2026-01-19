import scraper_ml
if __name__ == "__main__":
    lista = scraper_ml.scrape_all()
    if lista:
        scraper_ml.procesar(lista)
