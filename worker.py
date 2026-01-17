import csv
import os

INPUT_FILE = "propiedades.csv"
OUTPUT_FILE = "resultado.csv"

ZONAS_BUENAS = ["Belgrano", "Palermo", "Recoleta", "Nuñez"]
PRECIO_M2_MAX = 2500


def calcular_score(propiedad):
    score = 0
    motivos = []

    precio = float(propiedad["precio_usd"])
    metros = float(propiedad["metros"])
    ambientes = int(propiedad["ambientes"])
    zona = propiedad["zona"]

    precio_m2 = precio / metros

    if precio_m2 <= PRECIO_M2_MAX:
        score += 40
        motivos.append("Precio/m2 competitivo")

    if zona in ZONAS_BUENAS:
        score += 30
        motivos.append("Zona demandada")

    if ambientes >= 2:
        score += 20
        motivos.append("Buena tipología")

    return score, "; ".join(motivos)


def clasificar(score):
    if score >= 70:
        return "OPORTUNIDAD"
    elif score >= 40:
        return "REVISAR"
    else:
        return "DESCARTAR"


def ejecutar_analisis():
    if not os.path.exists(INPUT_FILE):
        print("📂 No hay propiedades.csv todavía")
        return

    resultados = []

    with open(INPUT_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            score, motivo = calcular_score(row)
            decision = clasificar(score)

            row["precio_m2"] = round(float(row["precio_usd"]) / float(row["metros"]), 2)
            row["score"] = score
            row
