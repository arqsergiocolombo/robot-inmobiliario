import time
from scraper_ml import scrape_all
from sheets import append_rows

print("Robot inmobiliario iniciado")

while True:
    try:
        rows = scrape_all()
        append_rows(rows)
        print(f"Subidas {len(rows)} filas a Sheets")
        time.sleep(300)
    except Exception as e:
        print("Error:", e)
        time.sleep(60)
