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
            viewport={"width": 1280, "height": 800}
        )

        page = context.new_page()
        page.goto(URL_ARGENPROP, timeout=60000)

        print("⏳ Esperando que carguen las publicaciones...")
        page.wait_for_timeout(6000)

        cards = page.locator(".listing__item").all()

        resultados = []

        for card in cards:
            try:
                titulo = card.locator(".card__title").inner_text()
                precio = card.locator(".card__price").inner_text()
                resultados.append((titulo, precio))
            except:
                continue

        browser.close()

        print(f"✅ Encontradas {len(resultados)} publicaciones")
        return resultados


if __name__ == "__main__":
    data = buscar_argenprop()

    print("\n📊 RESULTADOS:")
    for titulo, precio in data:
        print(f"- {titulo} | {precio}")
