import time
from worker import ejecutar_analisis

print("🤖 Robot inmobiliario iniciado en Railway")

while True:
    try:
        ejecutar_analisis()
        print("⏳ Esperando próximo ciclo...")
        time.sleep(300)  # 5 minutos
    except Exception as e:
        print("❌ Error:", e)
        time.sleep(60)
