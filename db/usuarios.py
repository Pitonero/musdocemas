import psycopg2
from psycopg2 import Error
from db.Conexion import CConexion

class CUsuarios:

    @staticmethod
    def mostrarUsuarios():
        try:
            cone = CConexion.ConexionBaseDeDatos()
            cursor = cone.cursor()
            cursor.execute("SELECT * FROM Usuarios;")
            miResultado = cursor.fetchall()
            cone.close()
            return miResultado

        except Error as error:
            print(f"Error al mostrar datos: {error}")

    @staticmethod
    def insertarUsuario(nombre_usuario, alias, email, password_hash, avatar_url, activo, clave_activacion, fecha_registro, codigo_activacion, verificado):
        try:
            cone = CConexion.ConexionBaseDeDatos()
            cursor = cone.cursor()
            sql = """
                INSERT INTO Usuarios (nombre_usuario, alias, email, password_hash, avatar_url, activo, clave_activacion, fecha_registro, codigo_activacion, verificado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
            valores = (nombre_usuario, alias, email, password_hash, avatar_url, activo, clave_activacion, fecha_registro, codigo_activacion, verificado)
            cursor.execute(sql, valores)
            cone.commit()
            print(f"DEBUG: ALTA USUARIO: {cursor.rowcount} registro insertado")
            cone.close()

        except Error as error:
            print(f"Error al insertar usuario: {error}")

    @staticmethod
    def modificarUsuario(idUsuario, nombre_usuario, alias, email, password_hash, avatar_url, fecha_registro):
        try:
            cone = CConexion.ConexionBaseDeDatos()
            cursor = cone.cursor()
            sql = """
                UPDATE Usuarios
                SET nombre_usuario = %s, alias = %s, email = %s, password_hash = %s, avatar_url = %s, fecha_registro = %s
                WHERE usuario_id = %s;
            """
            valores = (nombre_usuario, alias, email, password_hash, avatar_url, fecha_registro, idUsuario)
            cursor.execute(sql, valores)
            cone.commit()
            print(f"DEBUG: MODIFICACION USUARIO: {cursor.rowcount} registro actualizado")
            cone.close()

        except Error as error:
            print(f"Error al modificar usuario: {error}")

    @staticmethod
    def modificarPerfil(nombre_usuario, email, avatar_url, usuario):
        try:
            cone = CConexion.ConexionBaseDeDatos()
            cursor = cone.cursor()
            sql = """
                UPDATE Usuarios
                SET nombre_usuario = %s, email = %s, avatar_url = %s
                WHERE alias = %s;
            """
            valores = (nombre_usuario, email, avatar_url, usuario)
            cursor.execute(sql, valores)
            cone.commit()
            print(f"DEBUG: MODIFICACION PERFIL: {cursor.rowcount} registro actualizado")
            cone.close()

        except Error as error:
            print(f"Error al modificar perfil: {error}")

    @staticmethod
    def modificarActivacion(usuario):
        try:
            cone = CConexion.ConexionBaseDeDatos()
            cursor = cone.cursor()
            sql = "UPDATE Usuarios SET verificado = TRUE WHERE alias = %s;"
            valores = (usuario,)
            cursor.execute(sql, valores)
            cone.commit()
            print(f"DEBUG: MODIFICACION ACTIVACIÓN: {cursor.rowcount} verificación realizada")
            cone.close()

        except Error as error:
            print(f"Error al modificar activación: {error}")

    @staticmethod
    def borrarUsuario(idUsuario):
        try:
            cone = CConexion.ConexionBaseDeDatos()
            cursor = cone.cursor()
            sql = "DELETE FROM Usuarios WHERE usuario_id = %s;"
            valores = (idUsuario,)
            cursor.execute(sql, valores)
            cone.commit()
            print(f"DEBUG: BORRADO USUARIO: {cursor.rowcount} registro borrado")
            cone.close()

        except Error as error:
            print(f"Error al borrar usuario: {error}")

    @staticmethod
    def leerUnUsuario(alias):
        try:
            cone = CConexion.ConexionBaseDeDatos()
            cursor = cone.cursor()
            sql = "SELECT * FROM Usuarios WHERE alias = %s;"
            valores = (alias,)
            cursor.execute(sql, valores)
            miResultado = cursor.fetchall()
            leidos = len(miResultado)
            cone.close()
            print(f"DEBUG: LEER UN USUARIO: {leidos} registro recuperado")
            return miResultado, leidos

        except Error as error:
            print(f"Error al leer usuario: {error}")

    @staticmethod
    def leerEmail(email):
        try:
            cone = CConexion.ConexionBaseDeDatos()
            cursor = cone.cursor()
            sql = "SELECT * FROM usuarios WHERE email = %s;"
            valores = (email,)
            cursor.execute(sql, valores)
            miResultado = cursor.fetchall()
            leidos = len(miResultado)  # Cambié esto por cursor.rowcount
            print(f"DEBUG: LEER EMAIL: {leidos} registro(s) recuperado(s)")
            return miResultado, leidos
        except Exception as error:
            print(f"Error al leer email: {error}")
        finally:
            if cone:
                cone.close()  # Asegúrate de cerrar la conexión aquí


