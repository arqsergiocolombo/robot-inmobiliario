# Robot Inmobiliario Autónomo 🤖
Este robot busca departamentos en Palermo, Belgrano y Recoleta que cumplan con:
- Al menos 2 ambientes (o 1 dormitorio).
- Más de 40 m2 de superficie.
- Precio menor a USD 100.000.

### Funcionamiento
1. Scrapea Argenprop diariamente.
2. Guarda los resultados en una base de datos PostgreSQL en **Railway**.
3. Detecta automáticamente si una propiedad bajó de precio comparándola con registros anteriores.
