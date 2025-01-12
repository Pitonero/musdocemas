import mysql.connector
import hashlib
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

# Función para hash de contraseña
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Función para registrar un nuevo usuario
def registrar_usuario(conn, nombre_usuario, alias, email, password):
    try:
        # Hash de la contraseña
        password_hash = hash_password(password)
        
        # Fecha de registro
        fecha_registro = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Inserción en la tabla de Usuarios
        sql = '''INSERT INTO Usuarios (nombre_usuario, alias, email, password_hash, fecha_registro)
                 VALUES (%s, %s, %s, %s, %s)'''
        cur = conn.cursor()
        cur.execute(sql, (nombre_usuario, alias, email, password_hash, fecha_registro))
        conn.commit()
        print("Usuario registrado exitosamente.")
    
    except Error as e:
        if "Duplicate entry" in str(e):
            print("Error: el alias o el email ya están registrados.")
        else:
            print("Error al registrar el usuario:", e)

# Configuración de la base de datos y ejecución de registro
conn = create_connection()

# Ejemplo de datos de usuario para registro
nombre_usuario = "Juan Perez"
alias = "juan_p"
email = "juan.perez@example.com"
password = "mi_contraseña_segura"

# Llamada a la función para registrar usuario
if conn:
    registrar_usuario(conn, nombre_usuario, alias, email, password)
    conn.close()