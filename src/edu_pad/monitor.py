import pandas as pd
import sqlite3
import os
import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


class DatabaseMonitor:
    def __init__(self):
        os.makedirs("src/edu_pad/static/db", exist_ok=True)
        os.makedirs("src/edu_pad/static/logs", exist_ok=True)
        self.rutadb = "src/edu_pad/static/db/productos_analisis.db"
        self.tabla = "productos_analisis"
        self.ruta_log = "src/edu_pad/static/logs/monitor_log.json"
        
    def verificar_base_datos(self):
        """Verifica si la base de datos existe y es accesible"""
        if not os.path.exists(self.rutadb):
            print(f"ERROR: Base de datos no encontrada en {self.rutadb}")
            return False
            
        try:
            conn = sqlite3.connect(self.rutadb)
            conn.close()
            print("Base de datos verificada correctamente")
            return True
        except Exception as e:
            print(f"ERROR: No se pudo conectar a la base de datos: {str(e)}")
            return False
    
    def contar_registros(self):
        """Cuenta el número de registros en la tabla y verifica su integridad, guardando métricas útiles"""
        try:
            conn = sqlite3.connect(self.rutadb)
            cursor = conn.cursor()
            
            # Total de registros
            cursor.execute(f"SELECT COUNT(*) FROM {self.tabla}")
            total_registros = cursor.fetchone()[0]
            
            # Registros nulos en columnas importantes
            cursor.execute(f"SELECT COUNT(*) FROM {self.tabla} WHERE Calificaciones IS NULL")
            nulos_calificaciones = cursor.fetchone()[0]
            cursor.execute(f"SELECT COUNT(*) FROM {self.tabla} WHERE Precios IS NULL")
            nulos_precios = cursor.fetchone()[0]
            cursor.execute(f"SELECT COUNT(*) FROM {self.tabla} WHERE Productos IS NULL")
            nulos_productos = cursor.fetchone()[0]
    
            # Última actualización
            cursor.execute(f"SELECT MAX(Update_Date) FROM {self.tabla}")
            ultima_actualizacion = cursor.fetchone()[0]
    
            # Precios para métricas adicionales
            cursor.execute(f"SELECT Productos, Precios FROM {self.tabla} WHERE Precios IS NOT NULL")
            registros = cursor.fetchall()
            precios = []
            nombres = []
            for nombre, precio in registros:
                try:
                    precio_limpio = str(precio).replace('$', '').replace(',', '').strip()
                    precio_float = float(precio_limpio)
                    precios.append(precio_float)
                    nombres.append(nombre)
                except Exception:
                    continue
    
            precio_promedio = round(sum(precios) / len(precios), 3) if precios else 0
            precio_min = min(precios) if precios else 0
            precio_max = max(precios) if precios else 0
            precio_promedio = float(f"{precio_promedio:.3f}")
            precio_min = float(f"{precio_min:.3f}")
            precio_max = float(f"{precio_max:.3f}")
    
            conn.close()
          
            return {
                "total_registros": total_registros,
                "nulos_calificaciones": nulos_calificaciones,
                "ultima_actualizacion": ultima_actualizacion,
                "precio_promedio": precio_promedio,
                "precio_min": precio_min,
                "precio_max": precio_max,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            print(f"ERROR: No se pudo contar registros: {str(e)}")
            return None
    
    def analizar_producto(self, nombre_producto):
        """Analiza un producto específico y muestra su precio y los 3 más cercanos"""
        try:
            conn = sqlite3.connect(self.rutadb)
            cursor = conn.cursor()
            # Obtener todos los productos y precios
            cursor.execute(f"SELECT Productos, Precios FROM {self.tabla}")
            registros = cursor.fetchall()
            conn.close()
    
            # Limpiar y convertir precios
            productos = []
            for nombre, precio in registros:
                try:
                    precio_limpio = str(precio).replace('$', '').replace(',', '').strip()
                    precio_float = float(precio_limpio)
                    productos.append({"nombre": nombre, "precio": precio_float})
                except Exception:
                    continue
    
            if not productos:
                print("No se encontraron productos con precios válidos.")
                return
    
            # Calcular precio promedio
            precios = [p["precio"] for p in productos]
            precio_promedio = sum(precios) / len(precios)
            print(f"Precio promedio de todos los relojes: ${precio_promedio:.2f}")
    
            # Buscar producto específico
            producto_objetivo = None
            for p in productos:
                if nombre_producto.lower() in p["nombre"].lower():
                    producto_objetivo = p
                    break
    
            if not producto_objetivo:
                print(f"No se encontró el producto '{nombre_producto}'.")
                return
    
            print(f"\nProducto encontrado: {producto_objetivo['nombre']}")
            print(f"Precio exacto: ${producto_objetivo['precio']:.2f}")
    
            # Buscar los 3 productos más cercanos en precio (excluyendo el objetivo)
            productos_otros = [p for p in productos if p != producto_objetivo]
            productos_otros.sort(key=lambda x: abs(x["precio"] - producto_objetivo["precio"]))
            print("\nOtros 3 productos con precio más cercano:")
            for cercano in productos_otros[:3]:
                print(f"- {cercano['nombre']} | Precio: ${cercano['precio']:.2f}")
    
        except Exception as e:
            print(f"ERROR: {e}")
    
    def guardar_log(self, metricas):
        """Guarda las métricas en un archivo log JSON"""
        try:
            # Crear el directorio de logs si no existe
            os.makedirs(os.path.dirname(self.ruta_log), exist_ok=True)
            
            # Leer logs existentes si existe el archivo
            if os.path.exists(self.ruta_log):
                with open(self.ruta_log, 'r') as f:
                    try:
                        logs = json.load(f)
                    except:
                        logs = {"registros": []}
            else:
                logs = {"registros": []}
            
            # Añadir el nuevo registro
            logs["registros"].append(metricas)
            
            # Limitar a los últimos 30 registros
            if len(logs["registros"]) > 30:
                logs["registros"] = logs["registros"][-30:]
            
            # Guardar el archivo actualizado
            with open(self.ruta_log, 'w') as f:
                json.dump(logs, f, indent=2)
                
            print(f"Log guardado correctamente en {self.ruta_log}")
            return True
        except Exception as e:
            print(f"ERROR: No se pudo guardar el log: {str(e)}")
            return False
    
    def enviar_alerta(self, asunto, mensaje):
        """Envía una alerta por correo electrónico (configurado mediante variables de entorno)"""
        try:
            # Obtener configuración de correo de variables de entorno
            email_emisor = os.environ.get('EMAIL_SENDER')
            email_receptor = os.environ.get('EMAIL_RECEIVER')
            email_password = os.environ.get('EMAIL_PASSWORD')
            smtp_server = os.environ.get('SMTP_SERVER')
            smtp_port = os.environ.get('SMTP_PORT')
            print(f"SMTP_PORT obtenido: {smtp_port}")
            print(f"SMTP_SERVER obtenido: {smtp_server}")
            print(f"EMAIL_SENDER obtenido: {email_emisor}")
            print(f"EMAIL_RECEIVER obtenido: {email_receptor}")
            print(f"EMAIL_PASSWORD obtenido: {email_password}")

            if not all([email_emisor, email_receptor, email_password]):
                print("ADVERTENCIA: No se enviará alerta por correo. Faltan credenciales.")
                return False
            
            # Crear mensaje
            msg = MIMEMultipart()
            msg['From'] = email_emisor
            msg['To'] = email_receptor
            msg['Subject'] = asunto
            
            # Añadir cuerpo del mensaje
            msg.attach(MIMEText(mensaje, 'plain'))
            
            # Enviar correo
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(email_emisor, email_password)
            server.send_message(msg)
            server.quit()
            
            print(f"Alerta enviada correctamente a {email_receptor}")
            return True
        except Exception as e:
            print(f"ERROR: No se pudo enviar la alerta: {str(e)}")
            return False
    
    def ejecutar_monitoreo(self):
        """Método  principal que ejecuta todas las verificaciones"""
        print("*******************************************************************")
        print(f"Inicio de monitoreo: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("*******************************************************************")
        
        # Verificar base de datos
        if not self.verificar_base_datos():
            self.enviar_alerta(
                "ALERTA: Base de datos no accesible", 
                f"La base de datos dolar_analisis.db no se encuentra o no es accesible. Fecha: {datetime.now()}"
            )
            return False
        
        # Contar registros
        metricas = self.contar_registros()
        if not metricas:
            self.enviar_alerta(
                "ALERTA: Error en monitoreo de DB", 
                f"No se pudo obtener métricas de la tabla {self.tabla}. Fecha: {datetime.now()}"
            )
            return False
    
        # Obtener los 4 productos más baratos
        try:
            conn = sqlite3.connect(self.rutadb)
            cursor = conn.cursor()
            cursor.execute(f"SELECT Productos, Precios FROM {self.tabla}")
            registros = cursor.fetchall()
            conn.close()
    
            productos = []
            for nombre, precio in registros:
                try:
                    precio_limpio = str(precio).replace('$', '').replace(',', '').strip()
                    precio_float = float(precio_limpio)
                    productos.append({"nombre": nombre, "precio": precio_float})
                except Exception:
                    continue
    
            productos.sort(key=lambda x: x["precio"])
            top4 = productos[:4]
        except Exception as e:
            print(f"ERROR al obtener productos más baratos: {e}")
            top4 = []
    
        # Guardar log
        self.guardar_log(metricas)
    
        # Enviar alerta con los 4 productos más baratos
        if top4:
            mensaje = " TOP 4 Smartwatches con mejor precio:\n"
            for i, prod in enumerate(top4):
                mensaje += f"{i+1}. {prod['nombre']} - ${prod['precio']:.3f} COP\n"                
            self.enviar_alerta(
                "INFO: Productos con mejor precio",
                mensaje
            )
            print(mensaje)
        else:
            print("No se encontraron productos válidos para la alerta de mejores precios.")
    
        print("*******************************************************************")
        print(f"Fin de monitoreo: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("*******************************************************************")
        return True

if __name__ == "__main__":
    monitor = DatabaseMonitor()
    monitor.ejecutar_monitoreo()