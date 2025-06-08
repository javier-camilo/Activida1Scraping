# Activida1Scraping

## Descripción general

Este proyecto realiza scraping de productos de Mercado Libre (ejemplo: "Smartwatch"), almacena los datos en CSV y una base de datos SQLite, y automatiza el monitoreo y envío de alertas por email. El flujo completo está orquestado con Docker y GitHub Actions, siguiendo buenas prácticas de seguridad y despliegue.

---

## Actividad 1: Extracción y almacenamiento de datos

- **Scraping**: Se extraen datos de productos (nombre, precio, calificación) usando Python, `requests`, `BeautifulSoup` y `pandas`.
- **Almacenamiento**: Los datos se guardan en un archivo CSV y posteriormente en una base de datos SQLite para facilitar su análisis.

---

## Actividad 2: Ingesta y monitoreo

- **Ingesta**: Un módulo carga los datos del CSV a la base de datos, asegurando integridad y consistencia.
- **Monitor**: Se implementa un sistema que calcula métricas (total de registros, precios promedio/mínimo/máximo, nulos, etc.) y guarda un historial en un archivo JSON.

---

## Actividad 3: Automatización avanzada, alertas y despliegue seguro

### 1. Alertas automáticas por email

- El sistema envía alertas automáticas por correo electrónico con el TOP 4 de productos más baratos.
- El envío de emails se realiza de forma segura usando variables de entorno y secretos de GitHub Actions, nunca exponiendo credenciales en el código.
- El código relevante está en [`src/edu_pad/monitor.py`](src/edu_pad/monitor.py).

### 2. Integración con Docker

- Se creó un [`dockerfile`](dockerfile) para construir una imagen que ejecuta el scraping, la ingesta y el monitoreo.
- Esto permite portabilidad y reproducibilidad en cualquier entorno compatible con Docker.

### 3. Automatización con GitHub Actions

- El workflow [`docker.yml`](.github/workflows/docker.yml) automatiza:
  - Construcción de la imagen Docker.
  - Ejecución de los scripts principales en contenedores.
  - Montaje de volúmenes para persistencia de datos.
  - Inyección de variables de entorno sensibles mediante **Secrets** de GitHub.
- Ejemplo de paso para ejecutar el monitoreo y enviar alertas:
  ```yaml
  - name: Paso 6 - Ejecutar Monitor
    run: |
      docker run --rm \
        -v "${{ github.workspace }}/static/csv":/Activida1Scraping/static/csv \
        -v "${{ github.workspace }}/static/db":/Activida1Scraping/static/db \
        -e EMAIL_SENDER=${{ secrets.EMAIL_SENDER }} \
        -e EMAIL_RECEIVER=${{ secrets.EMAIL_RECEIVER }} \
        -e EMAIL_PASSWORD=${{ secrets.EMAIL_PASSWORD }} \
        -e SMTP_SERVER=${{ secrets.SMTP_SERVER }} \
        -e SMTP_PORT=${{ secrets.SMTP_PORT }} \
        contenedor edu_pad.monitor
  ```

### 4. Buenas prácticas de seguridad

- **Gestión de credenciales**: Todas las credenciales (emails, contraseñas, tokens) se almacenan como secretos en GitHub y se pasan como variables de entorno a los contenedores.
- **No se exponen datos sensibles** en el repositorio ni en los logs.

---

## Estructura del proyecto

```
Activida1Scraping/
│
├── src/
│   └── edu_pad/
│       ├── dataweb.py
│       ├── database.py
│       ├── main_extractora.py
│       ├── main_ingesta.py
│       ├── monitor.py
│       └── static/
│           ├── csv/
│           ├── db/
│           └── logs/
├── dockerfile
├── .github/workflows/docker.yml
├── README.md
```

---

## Ejecución manual

1. **Scraping y CSV**:
   ```sh
   python -m edu_pad.main_extractora
   ```
2. **Ingesta a base de datos**:
   ```sh
   python -m edu_pad.main_ingesta
   ```
3. **Monitor y alertas**:
   ```sh
   python -m edu_pad.monitor
   ```

---

## Autores

- **Nombre 1** - [correo1@ejemplo.com]
- **Nombre 2** - [correo2@ejemplo.com]

> Actualiza los nombres y correos según los autores reales del proyecto.

---

**Este proyecto integra scraping, almacenamiento, monitoreo, alertas automáticas, despliegue con Docker y CI/CD con GitHub Actions, siguiendo buenas prácticas de seguridad y automatización profesional.**