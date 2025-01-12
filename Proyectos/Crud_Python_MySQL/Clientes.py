from Conexion import *

class CClientes:

    def mostrarClientes():    
        try: 
            cone = CConexion.ConexionBaseDeDatos()
            cursor = cone.cursor()
            cursor.execute ("select * from usuarios;")
            miResultado = cursor.fetchall()
            cone.commit()
            cone.close()
            return miResultado

        except mysql.connector.Error as error:
            print("Error al mostrar datos {}".format(error))

    def insertarClientes(nombres,apellidos,sexo):
        try:
            cone = CConexion.ConexionBaseDeDatos()
            cursor = cone.cursor()
            sql = "insert into usuarios values( null, %s, %s, %s);"
            # la variable valores tiene que ser una tupla (array que no se puede modificar)
            # como minima expresion es : (valor,). La coma hace que sea una tupla inmutable.
            valores = (nombres,apellidos,sexo)
            cursor.execute(sql,valores)
            cone.commit()
            print(cursor.rowcount, "Registro insertado")
            cone.close()

        except mysql.connector.Error as error:
            print("error de introduccion de datos {}".format(error))

    def modificarClientes(idUsuario, nombres,apellidos,sexo):
        try:
            cone = CConexion.ConexionBaseDeDatos()
            cursor = cone.cursor()
            sql = "update usuarios set nombres = %s, apellidos = %s, sexo = %s where Id = %s;"
            valores = (nombres,apellidos,sexo,idUsuario)
            cursor.execute(sql,valores)
            cone.commit()
            print(cursor.rowcount, "Registro actualizado")
            cone.close()

        except mysql.connector.Error as error:
            print("error al actualizar datos {}".format(error))

    def borrarClientes(idUsuario):
        try:
            cone = CConexion.ConexionBaseDeDatos()
            cursor = cone.cursor()
            sql = "delete from usuarios where id = %s;"
            valores = (idUsuario,)
            cursor.execute(sql,valores)
            cone.commit()
            print(cursor.rowcount, "Registro borrado")
            cone.close()

        except mysql.connector.Error as error:
            print("error al borrar datos {}".format(error))