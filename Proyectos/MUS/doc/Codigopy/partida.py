from partida_tiempo_real import *

# Conectar a la base de datos
conn = create_connection()

# Obtener las cartas del jugador
usuario_id = 2
partida_id = 1
cartas = obtener_cartas_jugador(conn, partida_id, usuario_id)
print("Cartas del jugador:", cartas)

# Registrar una apuesta
registrar_apuesta(conn, partida_id, usuario_id, 'grande', 10)

# Obtener apuestas actuales
apuestas = obtener_apuestas(conn, partida_id)
print("Apuestas actuales:", apuestas)

# Obtener y actualizar turno
turno_actual = obtener_turno_actual(conn, partida_id)
print("Turno actual:", turno_actual)
actualizar_turno(conn, partida_id, 3)  # Actualizar turno a otro usuario_id

# Obtener marcador de puntuación
marcador = obtener_marcador_puntuacion(conn, partida_id)
print("Marcador de puntuación:", marcador)

# Enviar y obtener señas
enviar_seña(conn, partida_id, usuario_id, 'guiñar')
señas = obtener_señas(conn, partida_id)
print("Señas recientes:", señas)

# Cerrar la conexión
close_connection(conn)

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

# Función para obtener las cartas de un jugador
def obtener_cartas_jugador(conn, partida_id, usuario_id):
    try:
        sql = '''SELECT carta FROM CartasJugador 
                 WHERE partida_id = %s AND usuario_id = %s'''
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, (partida_id, usuario_id))
        cartas = cur.fetchall()
        return [carta['carta'] for carta in cartas] if cartas else []
    except Error as e:
        print("Error al obtener cartas del jugador:", e)
        return []

# Función para registrar una apuesta
def registrar_apuesta(conn, partida_id, usuario_id, tipo_apuesta, cantidad):
    try:
        sql = '''INSERT INTO Apuestas (partida_id, usuario_id, tipo_apuesta, cantidad, fecha_apuesta)
                 VALUES (%s, %s, %s, %s, %s)'''
        fecha_apuesta = datetime.datetime.now()
        cur = conn.cursor()
        cur.execute(sql, (partida_id, usuario_id, tipo_apuesta, cantidad, fecha_apuesta))
        conn.commit()
        print(f"Apuesta de tipo '{tipo_apuesta}' registrada con éxito.")
    except Error as e:
        print("Error al registrar la apuesta:", e)

# Función para obtener las apuestas actuales
def obtener_apuestas(conn, partida_id):
    try:
        sql = '''SELECT tipo_apuesta, usuario_id, cantidad 
                 FROM Apuestas 
                 WHERE partida_id = %s 
                 ORDER BY fecha_apuesta DESC'''
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, (partida_id,))
        apuestas = cur.fetchall()
        return apuestas if apuestas else []
    except Error as e:
        print("Error al obtener apuestas:", e)
        return []

# Función para indicar el turno actual
def obtener_turno_actual(conn, partida_id):
    try:
        sql = '''SELECT turno_actual 
                 FROM Partidas 
                 WHERE partida_id = %s'''
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, (partida_id,))
        turno = cur.fetchone()
        return turno['turno_actual'] if turno else None
    except Error as e:
        print("Error al obtener el turno actual:", e)
        return None

# Función para actualizar el turno
def actualizar_turno(conn, partida_id, nuevo_turno_usuario_id):
    try:
        sql = '''UPDATE Partidas
                 SET turno_actual = %s 
                 WHERE partida_id = %s'''
        cur = conn.cursor()
        cur.execute(sql, (nuevo_turno_usuario_id, partida_id))
        conn.commit()
        print("Turno actualizado.")
    except Error as e:
        print("Error al actualizar el turno:", e)

# Función para obtener el marcador de puntuación
def obtener_marcador_puntuacion(conn, partida_id):
    try:
        sql = '''SELECT equipo, SUM(puntos) AS puntos_equipo 
                 FROM JugadoresPartida 
                 WHERE partida_id = %s 
                 GROUP BY equipo'''
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, (partida_id,))
        puntuacion = cur.fetchall()
        return {equipo['equipo']: equipo['puntos_equipo'] for equipo in puntuacion} if puntuacion else {}
    except Error as e:
        print("Error al obtener el marcador de puntuación:", e)
        return {}

# Función para enviar una seña
def enviar_seña(conn, partida_id, usuario_id, tipo_seña):
    try:
        sql = '''INSERT INTO Señas (partida_id, usuario_id, tipo_seña, fecha_seña)
                 VALUES (%s, %s, %s, %s)'''
        fecha_seña = datetime.datetime.now()
        cur = conn.cursor()
        cur.execute(sql, (partida_id, usuario_id, tipo_seña, fecha_seña))
        conn.commit()
        print(f"Seña '{tipo_seña}' enviada con éxito.")
    except Error as e:
        print("Error al enviar seña:", e)

# Función para obtener señas recientes
def obtener_señas(conn, partida_id, limite=10):
    try:
        sql = '''SELECT s.tipo_seña, u.alias, s.fecha_seña
                 FROM Señas s
                 JOIN Usuarios u ON s.usuario_id = u.usuario_id
                 WHERE s.partida_id = %s
                 ORDER BY s.fecha_seña DESC
                 LIMIT %s'''
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, (partida_id, limite))
        señas = cur.fetchall()
        return señas if señas else []
    except Error as e:
        print("Error al obtener señas:", e)
        return []

# Función para cerrar la conexión a la base de datos
def close_connection(conn):
    if conn.is_connected():
        conn.close()
        print("Conexión cerrada.")

