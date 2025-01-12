import os
import mysql.connector

class CConexion:
    @staticmethod
    def ConexionBaseDeDatos():
        try:
            conexion = mysql.connector.connect(
                user=os.getenv("DB_USER", "admin"),              # Variable de entorno
                password=os.getenv("DB_PASSWORD", "Gordiano.1"), # Variable de entorno
                host=os.getenv("DB_HOST", "localhost"),          # Variable de entorno          
                database=os.getenv("DB_NAME", "mus_game"),       # Variable de entorno
                port=os.getenv("DB_PORT", "3306")                # Variable de entorno
            )
            print("Conexión correcta")
            return conexion
        
        except mysql.connector.Error as error:
            print(f"Error al conectarse a la base de datos: {error}")
            return None  # Cambié esto para que no devuelva una conexión inválida

     #           host=os.getenv("DB_HOST", "127.0.0.1"),          # Variable de entorno       
    #ConexionBaseDeDatos()