import mysql.connector
import hashlib
from mysql.connector import Error

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

# Función para hash de contraseña
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Función para identificar al usuario
def identificar_usuario(conn, email, password):
    try:
        # Hash de la contraseña ingresada
        password_hash = hash_password(password)
        
        # Consulta para verificar email y password_hash
        sql = '''SELECT usuario_id, nombre_usuario, alias, avatar_url
                 FROM Usuarios
                 WHERE email = %s AND password_hash = %s'''
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, (email, password_hash))
        usuario = cur.fetchone()
        
        if usuario:
            print(f"Bienvenido {usuario['nombre_usuario']} (alias: {usuario['alias']}).")
            return usuario  # Retornar el usuario si es necesario
        else:
            print("Credenciales incorrectas. Verifica tu email y contraseña.")
            return None
    
    except Error as e:
        print("Error al intentar identificar al usuario:", e)
        return None

# Configuración de la base de datos y ejemplo de identificación de usuario
conn = create_connection()

# Ejemplo de datos de inicio de sesión
email = "juan.perez@example.com"
password = "mi_contraseña_segura"

# Llamada a la función para identificar al usuario
if conn:
    identificar_usuario(conn, email, password)
    conn.close()
