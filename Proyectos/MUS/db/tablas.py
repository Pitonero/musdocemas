from Conexion import *

# Función para obtener información de la mesa
def obtener_informacion_mesa(conn, mesa_id):
    try:
        sql = '''SELECT nombre_mesa, creador_id, es_privada, estado
                 FROM Mesas
                 WHERE mesa_id = %s'''
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, (mesa_id,))
        mesa_info = cur.fetchone()
        return mesa_info if mesa_info else None
    except Error as e:
        print("Error al obtener información de la mesa:", e)
        return None

# Función para listar jugadores en la sala de espera
def listar_jugadores(conn, partida_id):
    try:
        sql = '''SELECT u.usuario_id, u.nombre_usuario, u.alias, u.avatar_url, jp.equipo
                 FROM JugadoresPartida jp
                 JOIN Usuarios u ON jp.usuario_id = u.usuario_id
                 WHERE jp.partida_id = %s'''
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, (partida_id,))
        jugadores = cur.fetchall()
        return jugadores if jugadores else []
    except Error as e:
        print("Error al listar jugadores:", e)
        return []

# Función para enviar mensaje al chat
def enviar_mensaje_chat(conn, partida_id, usuario_id, contenido):
    try:
        sql = '''INSERT INTO MensajesChat (partida_id, usuario_id, contenido, fecha_envio)
                 VALUES (%s, %s, %s, %s)'''
        fecha_envio = datetime.datetime.now()
        cur = conn.cursor()
        cur.execute(sql, (partida_id, usuario_id, contenido, fecha_envio))
        conn.commit()
        print("Mensaje enviado al chat.")
    except Error as e:
        print("Error al enviar mensaje al chat:", e)

# Función para obtener mensajes recientes del chat
def obtener_mensajes_chat(conn, partida_id, limite=20):
    try:
        sql = '''SELECT mc.contenido, u.alias, mc.fecha_envio
                 FROM MensajesChat mc
                 JOIN Usuarios u ON mc.usuario_id = u.usuario_id
                 WHERE mc.partida_id = %s
                 ORDER BY mc.fecha_envio DESC
                 LIMIT %s'''
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, (partida_id, limite))
        mensajes = cur.fetchall()
        return mensajes if mensajes else []
    except Error as e:
        print("Error al obtener mensajes del chat:", e)
        return []

# Función para actualizar el estado de la partida
def actualizar_estado_partida(conn, partida_id, nuevo_estado):
    try:
        sql = '''UPDATE Partidas
                 SET estado = %s, fecha_inicio = %s
                 WHERE partida_id = %s'''
        fecha_inicio = datetime.datetime.now() if nuevo_estado == 'activa' else None
        cur = conn.cursor()
        cur.execute(sql, (nuevo_estado, fecha_inicio, partida_id))
        conn.commit()
        print(f"Estado de la partida actualizado a '{nuevo_estado}'.")
    except Error as e:
        print("Error al actualizar el estado de la partida:", e)
