import psycopg2
from psycopg2 import Error
from dotenv import load_dotenv
import os

# Cargar las variables de entorno desde .env (si existe)
load_dotenv()

class CConexion:
    @staticmethod
    def ConexionBaseDeDatos():
        try:
            # Obtener las variables de entorno
            host = os.getenv("DB_HOST", "localhost")
            database = os.getenv("DB_NAME", "musdocemas")
            user = os.getenv("DB_USER", "postgres")
            password = os.getenv("DB_PASSWORD", "Gordiano.1")

            # Conexión a la base de datos
            conexion = psycopg2.connect(
                host=host,
                database=database,
                user=user,
                password=password
            )
            print("Conexión correcta")
            return conexion

        except Error as error:
            print(f"Error al conectarse a la base de datos: {error}")
            return None

               
 # ConexionBaseDeDatos()        