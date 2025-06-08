import pandas as pd
import requests
from bs4 import BeautifulSoup

class DataWeb:
    def __init__(self):
        self.url = "https://listado.mercadolibre.com.co/smart-watch#D[A:smart%20watch]"
        self.df = pd.DataFrame()  # Inicializa el DataFrame vacío
        self.empty = True

    def obtener_datos(self):
        datos_productos = []  # Lista para almacenar los datos

        try:
            headers = {
                "User-Agent": "Mozilla/5.0"
            }
            respuesta = requests.get(self.url, headers=headers)
            if respuesta.status_code == 200:
                print("Acceso exitoso a la página")
                print("Csv generado correctamente")
                soup = BeautifulSoup(respuesta.text, "html.parser")

                items = soup.select('li.ui-search-layout__item')

                for item in items:
                    # Título del Producto
                    titulo_tag = item.select_one('h3.poly-component__title-wrapper a')
                    titulo = titulo_tag.text.strip() if titulo_tag else "No disponible"

                    # Precio
                    precio_tag = item.select_one('div.poly-price__current span.andes-money-amount__fraction')
                    precio = precio_tag.text.strip() if precio_tag else "No disponible"

                    # Calificación
                    calificacion_tag = item.select_one('span.poly-reviews__rating')
                    calificacion = calificacion_tag.text.strip() if calificacion_tag else "No disponible"

                    datos_productos.append({
                        "Productos": titulo,
                        "Precios": f"${precio}",
                        "Calificaciones": calificacion
                    })

                self.df = pd.DataFrame(datos_productos)
                self.empty = self.df.empty
                return self.df

            else:
                print("Acceso denegado a la página")
                self.df = pd.DataFrame()
                self.empty = True

        except Exception as e:
            print("Error al obtener los datos:", e)
            self.df = pd.DataFrame()
            self.empty = True