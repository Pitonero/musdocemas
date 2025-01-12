#from Conexion import *
import hashlib
from db.Conexion import *
from db.registro import *

class CUsuarios:

    def mostrarUsuarios():    
        try: 
            cone = CConexion.ConexionBaseDeDatos()
            cursor = cone.cursor()
            cursor.execute ("select * from Usuarios;")
            miResultado = cursor.fetchall()
            cone.commit()
            cone.close()
            return miResultado

        except mysql.connector.Error as error:
            print("Error al mostrar datos {}".format(error))

    def insertarUsuario(nombre_usuario,alias,email,password_hash,avatar_url,fecha_registro,verificado,codigo_activacion):
        try:
            cone = CConexion.ConexionBaseDeDatos()
            cursor = cone.cursor()
            sql = "insert into usuarios values( null, %s, %s, %s, %s, %s, %s, %s, %s);"
            # la variable valores tiene que ser una tupla (array que no se puede modificar)
            # como minima expresion es : (valor,). La coma hace que sea una tupla inmutable.
            valores = (nombre_usuario,alias,email,password_hash,avatar_url,fecha_registro,verificado,codigo_activacion)
            cursor.execute(sql,valores)
            cone.commit()
            print("DEBUG: ALTA USUARIO: ", cursor.rowcount, "Registro insertado")
            cone.close()

        except mysql.connector.Error as error:
            print("error de introduccion de datos {}".format(error))

    def modificarUsuario(idUsuario, nombre_usuario,alias,email,password_hash,avatar_url,fecha_registro):
        try:
            cone = CConexion.ConexionBaseDeDatos()
            cursor = cone.cursor()
            sql = "update usuarios set nombre_usuario = %s, alias = %s, email = %s, password_hash = %s, avatar_url = %s, fecha_registro = %s where usuario_id = %s;"
            valores = (nombre_usuario,alias,email,password_hash,avatar_url,fecha_registro,idUsuario)
            cursor.execute(sql,valores)
            cone.commit()
            print("DEBUG: MODIFICACION USUARIO: ",cursor.rowcount, "Registro actualizado")
            cone.close()

        except mysql.connector.Error as error:
            print("error al actualizar datos {}".format(error))

    def modificarPerfil(nombre_usuario,email,avatar_url,usuario):
        try:
            cone = CConexion.ConexionBaseDeDatos()
            cursor = cone.cursor()
            sql = "update usuarios set nombre_usuario = %s, email = %s, avatar_url = %s where alias = %s;"
            valores = (nombre_usuario,email,avatar_url,usuario)
            cursor.execute(sql,valores)
            cone.commit()
            print("DEBUG: MODIFICACION PERFIL: ", cursor.rowcount, "Registro actualizado")
            cone.close()

        except mysql.connector.Error as error:
            print("error al actualizar datos {}".format(error))

    def modificarActivacion(usuario):
        try:
            cone = CConexion.ConexionBaseDeDatos()
            cursor = cone.cursor()
            sql = "update usuarios set verificado = True where alias = %s;"
            valores = (usuario,)
            cursor.execute(sql,valores)
            cone.commit()
            print("DEBUG: MODIFICACION ACTIVACIÓN: ", cursor.rowcount, "Verificación realizada")
            cone.close()

        except mysql.connector.Error as error:
            print("error al actualizar datos {}".format(error))

    def borrarUsuario(idUsuario):
        try:
            cone = CConexion.ConexionBaseDeDatos()
            cursor = cone.cursor()
            sql = "delete from usuarios where usuario_id = %s;"
            valores = (idUsuario,)
            cursor.execute(sql,valores)
            cone.commit()
            print("DEBUG: BORRADO USUARIO: ", cursor.rowcount, "Registro borrado")
            cone.close()

        except mysql.connector.Error as error:
            print("error al borrar datos {}".format(error))

    def leerUnUsuario(alias):
        try:
            cone = CConexion.ConexionBaseDeDatos()
            cursor = cone.cursor()
            sql = "select * from usuarios where alias = %s;"
            valores = (alias,)
            cursor.execute(sql,valores)
            miResultado = cursor.fetchall()
            registros = cursor.rowcount
            cone.commit()
            print("DEBUG: LEER UN USUARIO: ",registros, "Registro recuperado")
            cone.close()
            return miResultado, registros

        except mysql.connector.Error as error:
            print("error al leer datos {}".format(error))

    def leerEmail(email):
        try:
            cone = CConexion.ConexionBaseDeDatos()
            cursor = cone.cursor()
            sql = "select * from usuarios where email = %s;"
            valores = (email,)
            cursor.execute(sql,valores)
            miResultado =  cursor.fetchall()
            leidos = cursor.rowcount
            cone.commit()
            print("DEBUG: LEER EMAIL: ",leidos, "Registro recuperado")
            cone.close()
            return miResultado, leidos

        except mysql.connector.Error as error:
            print("error al leer datos {}".format(error))
