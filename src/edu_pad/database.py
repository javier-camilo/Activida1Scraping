import pandas as pd
import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.rutadb = os.path.join(current_dir, "static", "db", "productos_analisis.db")

    
    def guardar_df(self,df=pd.DataFrame()):
        df=df.copy()
        try:
            conn=sqlite3.connect(self.rutadb)
            df["Create_Date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            df["Update_Date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            df.to_sql("productos_analisis", conn, if_exists="replace", index=False)
            print("*******************************************************")
            print("Datos Almacenados en la base de datos")
            print("*******************************************************")
            print("Datos guardados en la base de datos: {}".format(df.shape))
            return df
        except Exception as errores:
            print("Error al guardar en la base de datos: {}".format(df.shape))
            return None
        
    def obtener_datos(self,nombre_tabla="productos_analisis"):
        try:
            conn=sqlite3.connect(self.rutadb)
            query="SELECT * FROM {}".format(nombre_tabla)
            df=pd.read_sql_query(query, conn)
            print("*******************************************************")
            print("Se obtuvieron los s datos correctamente")
            print("*******************************************************")
            print("Cantidad de registros en base de datos: {}".format(df.shape))
            return df
        except Exception as errores:
            print(f"Error al obtener los datos de la tabla: {str(nombre_tabla)} en la base de datos: {str(errores)}")
            return None