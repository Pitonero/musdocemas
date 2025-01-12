import mysql.connector
from mysql.connector import Error
import datetime

# Función para crear la conexión a la base de datos MySQL
def create_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="tu_usuario_mysql",
            password="tu_contraseña_mysql",
            database="mus_database"
        )
        if conn.is_connected():
            print("Conexión exitosa a la base de datos.")
        return conn
    except Error as e:
        print(f"Error de conexión: {e}")
        return None