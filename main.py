import time
from scraper_ml import scrape_all

print("Robot inmobiliario iniciado")

while True:
    try:
        rows = scrape_all()
        print(f"Scraped {len(rows)} items")
        time.sleep(300)  # 5 minutos
    except Exception as e:
        print("Error:", e)
        time.sleep(60)
