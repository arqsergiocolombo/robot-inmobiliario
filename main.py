from playwright.sync_api import sync_playwright
import time

URL_ARGENPROP = "https://www.argenprop.com/departamentos-venta-palermo"

def buscar_argenprop():
    print("🏠 Iniciando búsqueda en Argenprop...")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )

        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800
