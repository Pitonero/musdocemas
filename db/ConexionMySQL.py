# desde la consola primero: pip install mysql-connector-python
import mysql.connector

class CConexion:
    def ConexionBaseDeDatos():
        try:
            conexion = mysql.connector.connect(user='admin', 
                                               password='Gordiano.1', 
                                               host='127.0.0.1',
                                               database='mus_game', 
                                               port='3306')
            print("Conexion correcta")
           
            return conexion 
        
        except mysql.connector.Error as error:
            print("Error al conectarse a la base de datos {}".format(error))
           
            return conexion 
        
   # ConexionBaseDeDatos()