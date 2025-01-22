from gevent import monkey
monkey.patch_all()

from flask import Flask, render_template, request, session, redirect, url_for, jsonify, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
from flask_session import Session
from flask_login import LoginManager,login_user, logout_user,login_required
from datetime import datetime, timedelta
from db.usuarios import *
from db.Conexion import *
from envio_email.enviar_email import Ccorreo
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import os
import traceback
from flask_sqlalchemy import SQLAlchemy
import hashlib

app = Flask(__name__)

app.secret_key = 'your_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_NAME'] = 'session_usuario'

# Configuración de conexión a PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Gordiano.1@localhost/musdocemas'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializa la base de datos
db = SQLAlchemy(app)

Session(app)

socketio = SocketIO(app, async_mode='eventlet')  # Usa eventlet

# Lista para jugadores logados y mesas disponibles
logged_players = []
session_store = {}
partidas = {}
tables = {}
salas = {}  # Diccionario para rastrear usuarios en cada sala
table_counter = 1  # Contador global para las mesas

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/reglas')
def reglas():
    return render_template('reglas.html')

@app.route('/noticias')
def noticias():
    print("DEBUG. Entra para lanzar noticias.html")
    return render_template('noticias.html')

@app.route('/politicaprivacidad')
def politicaprivacidad():
    print("DEBUG. Entra para lanzar politicaprivacidad.html")
    return render_template('politicaprivacidad.html')

@app.route('/politicacookies')
def politicacookies():
    return render_template('/politica-cookies.html')

@app.route('/terminosservicio')
def terminosservicio():
    print("DEBUG. Entra para lanzar terminosservicio.html")
    return render_template('terminosservicio.html')

@app.route('/tutorial')
def tutorial():
    return render_template('tutorial.html')

@app.route('/ranking')
def ranking():
    return render_template('estadisticas.html')

@app.route('/iniciosesion')
def iniciosesion():
    return render_template('identificacion.html')
    
@app.route('/registrarse')
def registrarse():
    return render_template(
        'registro.html',
        nombrep="",
        usuario="",
        password="",
        correo="",
        mostrar_verificacion = False 
    )

@app.route('/logout2')
def logout2():

    # Revisar disconnect
    username = session.get('usuario')
    mesa_id = session.get('mesa_id')
    #mesa_id = session['mesa_id']  # Recuperar el identificador de la mesa
    #mesa = tables.get(mesa_id) 
    print("DEBUG LOGOUT2 JUGADOR ", username, ". Id de la mesa: ", mesa_id)
    return render_template('index.html')

@app.route('/logout')
def logout():

    # Revisar disconnect
    username = session.get('usuario')
    mesa_id = session.get('mesa_id')
    #mesa_id = session['mesa_id']  # Recuperar el identificador de la mesa
    #mesa = tables.get(mesa_id) 
    print("DEBUG LOGOUT JUGADOR ", username, ". Id de la mesa: ", mesa_id)
    if mesa_id in tables:
        print("DEBUG LOGOUT JUGADOR. ", username)
        #jugadores = mesa["jugadores"]
        # Habría que eliminarlo de jugadores o sustituirlo por bot
        #socketio.emit('mensaje_mesa', {'msg': f"El jugador {username}, se ha desconectado de la mesa de juego.", 'username': 'Docemas' }, to=mesa_id)
    
    if username in logged_players:
        logged_players.remove(username)
        for table, jugadores in tables.items():
            for i, jugador in enumerate(jugadores):
                if jugador == username:
                    tables[table][i] = None
                    print(f"Jugador eliminado de jugadores: {username}")
     #   socketio.emit('update_players', logged_players, broadcast=True)

    # Elimina todos los datos de la sesión
    print(f"Va alimpiar la sesión")
    session.clear()

    # Redirige al usuario a la página inico o de login
    return render_template('index.html')
    #return render_template('identificacion.html') 

@app.route('/contactar')
def contactar():
    return render_template('contactar.html', nombre="", correo="")

@app.route('/contactar2')
def contactar2():
    nombre = session['nombre']
    correo = session['correo']
    return render_template('contactar.html', nombre=nombre, correo=correo)

@app.route('/enviar_correo', methods=['POST'])
def enviar_correo():
    # Recuperar datos del formulario
    nombre = request.form.get('nombre')
    email = request.form.get('email')
    asunto = request.form.get('asunto')
    mensaje = request.form.get('mensaje')

    # Configuración del correo
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_usuario = "musdocemas@gmail.com"  # Cambia esto por tu cuenta de Gmail
    smtp_password = "dmyz ajrs lnim qcht" # Cambia esto por tu contraseña o token de aplicación

    # Crear el mensaje
    cuerpo_mensaje = f"De: {nombre}\nEmail: {email}\n\n{mensaje}"
    msg = MIMEText(cuerpo_mensaje)
    msg['Subject'] = asunto
    msg['From'] = email
    msg['To'] = "musdocemas@gmail.com"  # Buzón de destino

    try:
        # Enviar el correo
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_usuario, smtp_password)
        server.sendmail(email, "musdocemas@gmail.com", msg.as_string())
        server.quit()

        print("Correo enviado correctamente", "success")

    except Exception as e:
        print(f"Error al enviar correo: {e}")

    if session['usuario']:
        username = session['usuario']
        nombre = session['nombre']
        #avatar = 'img/avatar.png'
        if session['usuario']:
            return render_template('entrarajugar.html',usuario=username,nombre=nombre,avatar='img/avatar.png')
            #return render_template('entrarajugar.html',usuario=username,nombre=nombre,avatar=avatar)
    else:
        return redirect('/')

   
@app.route('/perfilusuario')
def perfilusuario():
    usuario = session.get('usuario')
    datosusuario, leidos=CUsuarios.leerUnUsuario(usuario)

    print("DEBUG. Datos usuario leer:", datosusuario, " leidos: ", leidos)

    if leidos != 1:
         print('No se encontró el perfil')
    else:
        nombre = datosusuario [0] [1]
        usuariobd = datosusuario [0] [2]
        email = datosusuario [0] [3]
        #passwordbd = datosusuario [0] [4]
        avatar= datosusuario [0] [5]
        codigo= datosusuario [0] [7]
        print("DEBUG LEE USUARIO. usuario: ", usuario, " Avatar seleccionado2:", avatar , " codigo: ", codigo)
        return render_template('perfilusuario.html',usuario=usuariobd,nombre=nombre,correo=email, avatar=avatar)

@app.route('/seleccionar_avatar/<avatar>')
def seleccionar_avatar(avatar):
    usuario = session.get('usuario')
    if usuario:
        session['avatar'] = f'img/avatares/{avatar}'
    return redirect(url_for('perfilusuario'))

#Función para guardar el registro:
@app.route('/update_perfil',methods=['POST'])
def update_perfil():
    nombre =  request.form['name']   
    #alias =  request.form['alias']   
    correo =  request.form['email']  
    alias = session['usuario']   
    nombreAvatar = session['avatar']  
    print("Avatar seleccionado:" + nombreAvatar + " usuario: " + alias + " nombre: " + nombre+ " correo: " + correo)
    if nombre=='' or correo == '' or alias=='' or nombreAvatar=='':
        print('Recuerda rellenar todos los campos')
        return redirect(url_for('perfilusuario'))

    CUsuarios.modificarPerfil(nombre,correo,nombreAvatar,alias)
    return render_template('perfilusuario.html',usuario=alias,nombre=nombre,correo=correo, avatar=nombreAvatar)


@app.route('/listar_avatares')
def listar_avatares():
    avatar_dir = os.path.join(app.static_folder, 'img', 'avatares')
    avatares = [f for f in os.listdir(avatar_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
    return render_template('lista_avatares.html', avatares=avatares)

# Ruta para listar los avatares
@app.route('/avatares/')
def listar_avatares2():
    print("Entra en listar avatares")
    avatares_path = os.path.join(app.static_folder, 'img', 'avatares')
    avatares = os.listdir(avatares_path)  # Lista los archivos en la carpeta
    avatares = [f'img/avatares/{avatar}' for avatar in avatares if avatar.endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    return render_template('lista_avatares.html', avatares=avatares)

# Ruta para servir archivos estáticos, incluidos los avatares
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/avatars')
def list_avatars():
    print("Entra en list avatars")
    # Ruta del directorio donde están los avatares
    avatar_dir = os.path.join(app.static_folder, 'img/avatares')
    
    # Verifica si el directorio existe
    if not os.path.exists(avatar_dir):
        return jsonify({'error': 'No se encontró el directorio de avatares'}), 404
    
    # Lista solo imágenes en el directorio
    avatars = [f for f in os.listdir(avatar_dir) if f.endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    return jsonify(avatars)

@app.route('/lobby')
def lobby():
    #usuario = request.args.get('usuario')
    usuario = session.get('usuario')
    avatar = session['avatar']  
    print('Abrir sala de espera con Usuario: ', usuario, " Avatar: ", avatar)

    if usuario in logged_players:
        for table, jugadores in tables.items():
            for i, jugador in enumerate(jugadores):
                if jugador == usuario:
                    print(f"Jugador {usuario} estaba jugando en la mesa: {tables[table]['nombre']}")
                    return render_template('reingresar_mesa.html', usuario=usuario, mesa=tables[table]['nombre'])

    return render_template('sala_espera.html',usuario=usuario,avatar=avatar)
    #return render_template('sala_espera.html',usuario=usuario,avatar=nombreAvatar)

@app.route('/entrarajugar')
#@login_required
def entrarajugar():
    username = session['usuario']
    nombre = session['nombre'] 
    if session['avatar']:
        avatar = session['avatar']
    else:
        avatar = 'img/avatar.png'  
    print('DEBUG ENTRAR A JUGAR.: Usuario', username, ' Nombre: ', nombre, ' Avatar: ', avatar)
    if session['usuario']:
        return render_template('entrarajugar.html',usuario=username,nombre=nombre,avatar=avatar)
    else:
        print("Debe identificarse primero para entrar a jugar.")


@app.route('/mesa_juego/<mesa_id>')
def mesa_juego(mesa_id):
    username = session.get('usuario')  # Usuario actual del cliente
    if mesa_id in tables:
        session['mesa_id'] = mesa_id
        mesa = tables[mesa_id]      
    #    jugadores = mesa["jugadores"] 
    #    mano = mesa["mano"]         
    #    print("Contenido de username:", username)
    #    print("Contenido de jugadores mesa juego:", jugadores)  # Debug: Verifica la estructura
    #    print("Contenido de avatares mesa juego:", avatares)
    #    print("Contenido de mesa juego:", mesa)
    #    print("Contenido de avatares:", avatares) 
       # Reorganizar jugadores para que el usuario actual esté en la posición inferior
        # Renderiza la página de la mesa de juego
        print("Jugador para abrir mesa de juego: ", username) 
        return render_template('mesa_juego.html', mesa=mesa, usuario=username, mesa_id=mesa_id)
    else:
        return f"No se encontró la mesa con ID {mesa_id}", 404


#Función para guardar el registro:
@app.route('/store',methods=['POST'])
def storage():
    nombrep =  request.form['nombre_usuario']   
    alias =  request.form['alias']   
    password =  request.form['password']   
    correo =  request.form['email']  
    avatar_url =  'img/avatar.png'   
    verificado = False
    
    if nombrep=='' or correo == '' or alias=='' or password=='':
        print("DEBUG. Faltan por rellenar campos ")         
        return render_template('registro.html', nombrep=nombrep,usuario=alias,password=password,correo=correo,mensaje='Recuerda rellenar todos los campos.')
     
    if nombrep=='Bot1' or nombrep=='Bot2' or nombrep=='Bot3':
        print("DEBUG. Nombres reservados para los Bots.")         
        return render_template('registro.html', nombrep=nombrep,usuario=alias,password=password,correo=correo,mensaje='Ya existe este nombre de usuario.')

    # Verificamos que el email sea único
    datosusuario, leidos=CUsuarios.leerEmail(correo)
    if leidos > 0 and (datosusuario [0] [7] == True):
        print("DEBUG. EL EMAIL ", correo, " ya lo tiene otro usuario asignado: ", datosusuario [0] [2])         
        return render_template('registro.html', nombrep=nombrep,usuario=alias,password=password,correo=correo,mensaje='El email ya lo tiene otro usuario asignado.')
 
    # Generar el hash de la contraseña
    password_hash = hashlib.sha256(password.encode()).hexdigest()

    now = datetime.now()
    #tiempo=now.strftime("%Y%H%M%S")

    datosusuario, leidos=CUsuarios.leerUnUsuario(alias)
    print("DEBUG. LEEMOS USUARIO: Datosusuario: ", datosusuario) 
        
    if leidos > 0 and (datosusuario [0] [7] == True):
        print("DEBUG. EL USUARIO ", alias, " existe y ya está verificado: ", datosusuario [0] [6])         
        return render_template('registro.html', nombrep=nombrep,usuario=alias,password=password,correo=correo,mensaje='El nombre del usuario ya lo tiene otro usuario asignado.')
    
    if leidos == 0:
        # Generar un número aleatorio de 6 dígitos
        codigo_activacion = str(random.randint(100000, 999999))   
        print("DEBUG. ALTA USUARIO: codigo activacion", codigo_activacion)    
        CUsuarios.insertarUsuario(nombrep,alias,correo,password_hash,avatar_url,now,verificado,codigo_activacion)
        print("DEBUG. ALTA USUARIO: codigo activacion", codigo_activacion, " VERIFICADO: ", verificado)    
        Ccorreo.enviar_email(correo, codigo_activacion)
        return render_template('registro.html', nombrep=nombrep,usuario=alias,password=password,correo=correo,mostrar_verificacion = True,mensaje='Se ha enviado un correo con el código de activación.')

    if leidos > 0 and (datosusuario [0] [7] == False):
        print("DEBUG. ALTA USUARIO: codigo verificacion BD: ", datosusuario [0] [8]) 
        verificacion = request.form['verificacion'] 
        if datosusuario [0] [8] != verificacion:            
            return render_template('registro.html', nombrep=nombrep,usuario=alias,password=password,correo=correo,mensaje='Código de activación erróneo.')
        else:
            CUsuarios.modificarActivacion(alias)
            session['usuario'] = alias
            session['nombre'] = nombrep 
            session['avatar'] = avatar_url
            return render_template('entrarajugar.html',usuario=alias,nombre=nombrep,avatar=avatar_url)
    '''
    else:  
        CUsuarios.modificarActivacion(alias)
        session['usuario'] = alias
        session['nombre'] = nombrep 
        session['avatar'] = avatar_url
        return render_template('entrarajugar.html',usuario=alias,nombre=nombrep,avatar=avatar_url)
    '''

@app.route('/acceso', methods=['POST'])
def acceso():
    mensaje_error = None  # Inicializamos el mensaje de error en None
    usuario = request.form['username']
    password = request.form['password']
    
    # Simulación de lógica de autenticación
    if not usuario:
        mensaje_error = "Debe teclear el usuario."
        return render_template('identificacion.html', usuario=usuario,password=password,mensaje_error=mensaje_error)
    elif not password:  
        mensaje_error = "Debe teclear la password."
        return render_template('identificacion.html', usuario=usuario,password=password,mensaje_error=mensaje_error)

    datosusuario, registros = CUsuarios.leerUnUsuario(usuario)
    print("DEBUG. Datos usuario leer:", datosusuario, " leidos: ", registros)

    if registros != 1:
        mensaje_error = "Usuario no encontrado."
        return render_template('identificacion.html', usuario=usuario,password=password,mensaje_error=mensaje_error)
    else:
        nombre = datosusuario [0] [1]
        usuariobd = datosusuario [0] [2]
        correo = datosusuario [0] [3]
        passwordbd = datosusuario [0] [4]
        avatar = datosusuario [0] [5]
        acceso = datosusuario [0] [7]
        
        print("Los datos recuperados del usuario son:", datosusuario)
        
        if acceso == 0:
            print("Entra por acceso = 0:", acceso)
            mensaje_error = "Usuario no validado con código de activación."
            return render_template('identificacion.html', usuario=usuario,password=password,mensaje_error=mensaje_error)

        #print ("La clave:", usuariobd)
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        if usuario != usuariobd:
            mensaje_error = "Usuario no existe."
            return render_template('identificacion.html', usuario=usuario,password=password,mensaje_error=mensaje_error)
        elif password_hash != passwordbd:
            mensaje_error = "Contraseña incorrecta."
            return render_template('identificacion.html', usuario=usuario,password=password,mensaje_error=mensaje_error)
        else:
            mensaje_error = "Datos correctos."
            session['usuario'] = usuariobd
            session['nombre'] = nombre
            session['avatar'] = avatar
            session['correo'] = correo        

            if usuario and usuario not in logged_players:
                logged_players.append(usuario)

            # En el caso en el que el jugador ya estuviera en una mesa y busca reconectarse aqui
            for id_mesa, mesa in tables.items():
                if usuariobd in mesa['jugadores']:
                    print(f"DEBUG ACCESO. Jugador {usuariobd} estaba jugando en la mesa: {id_mesa}")
                   #sid = request.sid
                   # join_room(str(id_mesa))
                    return render_template('mesa_juego.html', mesa=tables[id_mesa], usuario=usuariobd, mesa_id=id_mesa)

    return render_template('entrarajugar.html',usuario=usuario,nombre=nombre,avatar=avatar)


@socketio.on('join')
def handle_join(data):
    #mesa_id = data['mesa_id']
    username = data.get('username')
    usersesion = session['usuario']
    print('Entra en Join de usuarios. Usuario connet: ', username, ' usuario de la sesion: ', usersesion)
    if username and username not in logged_players:
        logged_players.append(username)
    emit('update_players', logged_players, broadcast=True)  # Envía la lista de usuarios a todos los clientes
    emit('update_tables', tables, broadcast=False) # envía la lista de mesas solo al cliente recien conectado

@socketio.on('connect')
def handle_connect():
    username = session.get('username')
    #sid = request.sid
    #session_store[username] = sid
    #logged_players[sid] = {"nombre": None}  # Agrega cada cliente con un identificador único
    #print(f"Se ha conectado un jugador desde socketIO: ", username)
    # if username and username not in logged_players:
    #    logged_players.append(username)
    # Emitir la lista actualizada de jugadores a todos los clientes
    #emit('update_players', logged_players, broadcast=True)
    # Emitir el estado actual de las mesas solo al cliente recién conectado

@socketio.on('disconnect')
def handle_disconnect(): 
    username = session.get('usuario')
    mesa_id = session.get('mesa_id')
    #mesa_id = session['table_id']  # Recuperar el identificador de la mesa
    #mesa = tables.get(mesa_id) 
    print("DEBUG DESCONECTAR JUGADOR ", username, ". Id de la mesa: ", mesa_id)
    if mesa_id in tables:
        # Habría que eliminarlo de jugadores o sustituirlo por bot
       #jugadores = mesa["jugadores"]
        print("DEBUG DESCONECTAR JUGADOR. ", username)
        socketio.emit('mensaje_mesa', {'msg': f"{username}, tiene problemas con su conexión.", 'username': 'Docemas' }, to=mesa_id)

    print(f"Jugador desconectado: {username}")
    if username in logged_players:
        logged_players.remove(username)
        for table, jugadores in tables.items():
            for i, jugador in enumerate(jugadores):
                if jugador == username:
                    tables[table][i] = None
       # socketio.emit('update_players', logged_players, broadcast=True)

    # Elimina todos los datos de la sesión
    session.clear()
    # Redirige al usuario a la página inico o de login
    return render_template('index.html')
    #return render_template('identificacion.html') 

@socketio.on('chat_message')
def handle_chat_message(data):
    username = data.get('username')
    message = data.get('message')
   # print("DEBUG Chat_message:  usuario: ", username, " mensaje: ", message)
    emit('chat_message', {'username': username, 'message': message}, broadcast=True)

   
@socketio.on('message')
def handle_message(data):
    print("Mensaje genérico recibido:", data)
    emit('message', data, broadcast=True)

@socketio.on('mensaje_chat')
def mensaje_chat(data):
    mesa_id = data['mesa_id']
    print(f"Mensaje en mesa {mesa_id}: {data}")
    # Emitir el mensaje a todos los jugadores de la mesa
    emit('mensaje_mesa', {'msg': data['message'], 'username': data['username']}, broadcast=True)


@socketio.on('mensaje_chat_mesa')
def mensaje_chat_mesa(data):
    mesa_id = data['mesa_id']
    username = data.get('username')
    message = data.get('message')
   # print("El usuario está conectado a las mesas: ", rooms())
    print(f"Mensaje en chat de mesa {mesa_id}: {data}")
    # Emitir el mensaje a todos los jugadores de la mesa
    #emit('mensaje_mesa', {'message': f"{username} se ha unido a la mesa {mesa_id}.", 'username': 'Docemas'}, to=mesa_id)
    emit('mensaje_mesa', {'msg': data['message'], 'username': data['username']}, to=mesa_id)

@socketio.on('join_mesa')
def join_mesa(data):
    mesa_id = data['mesa_id']
    username = data['username']
    # Verificar si el usuario está en la sala
    sid = request.sid  # ID de sesión del cliente actual 
    if mesa_id in rooms(sid):  
        print(f"{username} ya está en la room {mesa_id}")
    else:
        join_room(str(mesa_id))  # Une al cliente a la sala de la mesa  
        print(f"{username} se unió a la room {mesa_id}")
   

@socketio.on('entrar_asiento')
def handle_entrar_asiento(data):
    username = data['username']
    mesa_id = data['mesa_id']
    asiento = data['asiento']
    avatar = data['avatar']
    numeroMesa = int(mesa_id.split('_')[1]) 
    print("Asiento en entrar: ", asiento, " Table: ", mesa_id, " usuario: ", username, " avatar: ", avatar)

    # En el caso en el que el jugador ya estuviera en una mesa y quiere entrar a otra
    for id_mesa, mesa in tables.items():
        if username in mesa['jugadores']:
            if mesa_id != id_mesa:
                print(f"DEBUG ACCESO. Jugador {username} estaba jugando en la mesa: {id_mesa}")
                emit('chat_message', {'message': f"{username} ya estás en la {id_mesa}.", 'username': 'Docemas'}, broadcast=False)
                emit('errorAsiento', {'message': f"{username} ya estás ocupando la {id_mesa}.", 'jugador': username, 'indice': asiento, 'mesa':  mesa_id},  broadcast=False)
                return render_template('sala_espera.html',usuario=username,avatar=avatar)

    join_room(mesa_id)  # Une al cliente a la sala de la mesa  
    #if table_id in tables and tables[table_id][asiento] is None:
    mesa = tables[mesa_id]
    if mesa["jugadores"][asiento] is None:
        mesa["jugadores"][asiento] = username
        mesa["avatares"][asiento] = avatar
        tables[mesa_id] = mesa  # Guardar cambios
    print(f"{username} entró en el asiento {asiento} de {mesa_id} con el avatar {avatar}")
    # Agregar el username a la sala
    if mesa_id not in salas:
        salas[mesa_id] = []
    salas[mesa_id].append(username)
    #print("Todas las tablas: ", tables)
    # Emitir un mensaje solo a los de la room notificando el nuevo jugador
    emit('chat_message', {'message': f"{username} se ha unido a la mesa {numeroMesa}.", 'username': 'Docemas'}, to=mesa_id)
    emit('update_tables', tables, broadcast=True) # Emitir un mensaje a todos en la sala notificando el nuevo jugador


@socketio.on('salir_asiento')
def handle_salir_asiento(data):
    username = data['username']
    mesa_id = data['mesa_id']
    asiento = data['asiento']
    mesa = tables[mesa_id]
    if mesa["jugadores"][asiento] == username:
        mesa["jugadores"][asiento] = None
        tables[mesa_id] = mesa  # Guardar cambios
    print("Asiento en salir: ", asiento, "usuario: ", username)
    # Eliminar al cliente de la mesa
    leave_room(mesa_id)    
    numeroMesa = int(mesa_id.split('_')[1]) 
    # (Opcional) Notificar a otros jugadores en la sala
    emit('chat_message', {'message': f"{username} se ha desconectado de la mesa {numeroMesa}.", 'username': 'Docemas'}, to=mesa_id)
    emit('update_tables', tables, broadcast=True) # Emitir un mensaje a todos en la sala notificando el nuevo jugador

@socketio.on('finalizar_partida')
def finalizar_partida(data):
    mesa_id = data['mesa_id']

    # Notificar a todos los jugadores
    emit('redireccionar_sala_espera', {'url': '/lobby'}, room=mesa_id)

    # Borramos la mesa de Tables:
    if mesa_id in tables:
        del tables[mesa_id]

    leave_room(mesa_id)    
    numeroMesa = int(mesa_id.split('_')[1]) 
    # (Opcional) Notificar a otros jugadores en la sala

    emit('chat_message', {'message': f"Finalizada la partida de la mesa {numeroMesa}.", 'username': 'Docemas'}, broadcast=True)
    emit('update_tables', tables, broadcast=True) # Emitir un mensaje a todos en la sala notificando el nuevo jugador


@socketio.on('send_message')
def handle_message(data):
    mesa_id = data['mesa_id']
    username = data['username']
   # message = data['mensaje']
    emit('chat_message', {'message': f"{username} se ha unido a la mesa {mesa_id} .", 'username': 'Docemas'}, to=mesa_id)


@socketio.on('create_table')
def handle_create_table(data):

    username = data['usuario']
    juegos_vaca = data['num_juegos']
    puntos_juego = data['puntos_por_juego']
    tiempo_espera = data['tiempo_espera']
    admitir_bots = data['admitir_bots']

    for table in tables.values():
        if table['owner'] == username:
            emit('chat_message', {'message': f"{username} ya tiene una mesa abierta.", 'username': 'Docemas'}, broadcast=True)
            return

    global table_counter
    table_id = f"Mesa_{table_counter}"
    print("DEBUG CREATE TABLE. La mesa a crear es:", table_id, " el owner es: ", username)
    tables[table_id] = {
        "nombre": f"Mesa_{table_counter}",
        "owner": username,
        "juegos_vaca": juegos_vaca,
        "puntos_juego": puntos_juego, 
        "espera": tiempo_espera,
        "bots": admitir_bots,
        "estado": "En espera",
        "jugadores": [None, None, None, None],  # Asientos vacíos
        "avatares": [None, None, None, None],  # Avatares vacíos
        "lances": ["Grande", "Chica", "Pares", "Juego", "Punto"],
        "estado_partida": "Repartir",
        "descartes": [],
        "manos": [],
        "mano": 0,
        "turno_actual": 0,  # Índice del jugador que tiene el turno
        "turno_anterior": 0,  # Índice del jugador que tiene el turno
        "jugadorAnterior": None,
        "jugadorApuesta": None,        
        "musContador": 0,  # verificar que se completa una ronda
        "puntos": [0,0],
        "juegos": [0, 0],
        "grande": [0, 0],
        "chica": [0, 0],
        "pares": [0, 0],
        "juego": [0, 0],
        "punto": [0, 0],
        "lance_actual": None,  # Lance activo: grande, chica, pares o juego
        "accion": None, # Paso, Veo, Envido, Órdago
        "acciones": [None, None, None, None, None], # última acción en cada lance
        "apuesta": [0, 0, 0, 0, 0],
        "apuesta_actual": 0,
        "apuesta_anterior": 0,
        "pareja_contraria": [],
        "estado_jugadores": {
                "Jugador1": {"ha_hablado": False},
                "Jugador2": {"ha_hablado": False},
                "Jugador3": {"ha_hablado": False},
                "Jugador4": {"ha_hablado": False}
                },
        "estado_juego": {
                "Jugador1": {"tiene_juego": False, "puntos": 0},
                "Jugador2": {"tiene_juego": False, "puntos": 0},
                "Jugador3": {"tiene_juego": False, "puntos": 0},
                "Jugador4": {"tiene_juego": False, "puntos": 0}
                },
        "pares_confirmados": {}
    }


    print('CREAR MESA PY. Va a hacer el emit desde create_table: ',  table_id, 'nro_table', table_counter )  
    emit('crear_mesaPY', { 'table_name': table_id, 'nro_table': table_counter }, broadcast=True)
    session['mesa_id'] = table_id  # Almacenamos el nombre de la mesa en la sesión del jugador
    table_counter += 1
    if table_counter > 999: 
        table_counter = 1

# Código para entrar a la mesa de juego:
@socketio.on('iniciar_partida')
def iniciar_partida(data):
    #print("Evento iniciar_partida recibido con datos:", data)
    table_id = data.get('table_id')
    mesa = tables.get(table_id)
    jugadores = mesa.get('jugadores', [])
    # Filtrar jugadores válidos (excluyendo None o vacíos)
    jugadoresEnMesa = [j for j in jugadores if j is not None and j != ""]
    #print("INICIAR PARTIDA. JUGADORES EN LA MESA", jugadores)
    if len(jugadoresEnMesa) < 4:
        jugadores_faltantes = 4 - len(jugadoresEnMesa)
        #print("INICIAR PARTIDA. FALTAN JUGADORES EN LA MESA", jugadores_faltantes)
        emit('error', {'message': f"La mesa no está completa. Faltan {jugadores_faltantes} jugadores."},  broadcast=False)
        usuario = session.get('usuario')
        avatar = session['avatar']  
        return render_template('sala_espera.html',usuario=usuario,avatar=avatar)

    inicializar_partida(table_id)
   # print(f"INICIAR PARTIDA Se va a iniciar la partida en {table_id}. Primero se actualiza sala de espera.)")
    try:
        emit('update_tables', tables, broadcast=True)
       # print(f"INICIAR PARTIDA Se LLMAMA A PARTIDA INICIADA. Primero se actualiza sala de espera.)")
        emit('partida_iniciada', { 'mesa_id': table_id, 'mesa': mesa}, to=table_id)

    except Exception as e:
        print(f"Error al iniciar la partida: {e}")

@socketio.on('reiniciar_partida')
def reiniciar_partida(data):
    table_id = data.get('table_id')
    mesa = tables.get(table_id)

    jugadores = mesa.get('jugadores', [])
    # Filtrar jugadores válidos (excluyendo None o vacíos)
    jugadoresEnMesa = [j for j in jugadores if j is not None and j != ""]
    #print("INICIAR PARTIDA. JUGADORES EN LA MESA", jugadores)
    if len(jugadoresEnMesa) < 4:
        jugadores_faltantes = 4 - len(jugadoresEnMesa)
       # print("INICIAR PARTIDA. FALTAN JUGADORES EN LA MESA", jugadores_faltantes)
        emit('error', {'message': f"La mesa no está completa. Faltan {jugadores_faltantes} jugadores."},  broadcast=False)
        usuario = session.get('usuario')
        avatar = session['avatar']  
        return render_template('sala_espera.html',usuario=usuario,avatar=avatar)

    inicializar_mesa(mesa, table_id)
    inicializar_partida(table_id)
    #print("Mesa:", mesa)
   # print("Va a llamar a reiniciar_nueva_partida. table_id: ", table_id)
    emit('reiniciar_nueva_partida', { 'mesa_id': table_id}, to=table_id)

# Función que inicializa la mesa para nueva partida
def inicializar_partida(table_id):
    mesa = tables.get(table_id)
   # Seleccionar aleatoriamente el mano (índice entre 0 y 3)
    if mesa["juegos"][0] == 0 and mesa["puntos"][0] == 0 and mesa["juegos"][1] == 0 and mesa["puntos"][1] == 0:
        mano = random.randint(0, 3)
        estado = 'En juego'
        tables[table_id]["estado"] = estado
        tables[table_id]["mano"] = mano
        tables[table_id]['turno_actual'] = mano
        tables[table_id]['musContador'] = 0

    ###### Simulación de cuatro jugadores en mesa. Es para pruebas con un un usuario logado:
    #tables[table_id]["jugadores"] = ['Gordiano1', 'Gordiano10', 'Gordiano11', 'Gordiano12']
    #tables[table_id]["avatares"] = ['../static/img/avatares/avatar19.png', '../static/img/avatares/avatar99.png', '../static/img/avatares/avatar9.png', '../static/img/avatares/avatar111.png']
        mesa = tables.get(table_id)

@socketio.on('actualizar_mesa')
def handle_actualizar_mesa(data):
    mesa_id = data['mesa_id']
    if mesa_id in tables:
        emit('mesa_actualizada', tables[mesa_id], to=mesa_id)

@socketio.on('actualizar_jugadores')
def handle_actualizar_jugadores(data):
    mesa_id = data['mesa_id']
    emit('jugadores_actualizados', tables[mesa_id], to=mesa_id)

#################################################################################
# sockets para el reparto de cartas. Desde mesa de juego el botón repartir llama:
#################################################################################
@socketio.on('repartir_cartas')
def handle_repartir_cartas(data):
    """
    Reparte cartas a los jugadores en la mesa especificada, integrando descartes si es necesario.
    """
    mesa_id = data.get('mesa_id')
    try:
        # Recuperar la mesa
        mesa = tables.get(mesa_id)
        
        if not mesa:
           raise KeyError(f"No se encontró la mesa con ID {mesa_id}")
        
        jugadores = mesa['jugadores']
        mano = mesa['mano']
        mesa['turno_anterior'] = (mano - 1) % 4
        jugador_anterior = mesa['jugadores'][mesa['turno_anterior']]
        jugador_turno = mesa['jugadores'][mesa['mano']]

      #  if None in jugadores:
      #      raise ValueError("No se puede repartir cartas. La mesa no está completa.")

        # Repartir cartas a los jugadores (4 inicialmente, ajustable en el futuro)
        num_cartas_por_jugador = [4] * len(jugadores)  # Aquí todos los jugadores piden 4 cartas
        manos, baraja, descartes = repartir_cartas(
            jugadores, 
            mesa.get('baraja', crear_baraja()),  # Usar la baraja actual o crear una nueva
            num_cartas_por_jugador, 
            mesa.get('descartes', [])  # Usar descartes existentes si los hay
        )

        # Actualizar la estructura de la mesa
        mesa['baraja'] = baraja
        mesa['descartes'] = descartes
        mesa['manos'] = manos
        mesa['estado_partida'] = "Mus"
        tables[mesa_id] = mesa  # Guardar cambios en la mesa
        print("cartas repartidas manos:", manos)
        
        emit('mensaje_mesa', {'msg': f"Reparte {jugador_anterior}. {jugador_turno} habla.", 'username': 'Nueva ronda' }, to=mesa_id)
 
         # Emitir las cartas repartidas a los jugadores
        emit('cartas_repartidas', {'mesa_id': mesa_id, 'manos': manos, 'mano': mano},  to=mesa_id)

    except KeyError as e:
        emit('error', {'message': str(e)}, room=request.sid)

import random

# Generar la baraja de cartas (sin 8 y 9)
def crear_baraja():
    palos = ['o', 'c', 'e', 'b']  # oros, copas, espadas, bastos
    valores = [1, 2, 3, 4, 5, 6, 7, 10, 11, 12]  # As, 2-7, Sota, Caballo, Rey
    baraja = [f"{valor}{palo}" for palo in palos for valor in valores]
    return baraja

# Repartir cartas con manejo de descartes
import random

# Repartir cartas a todos los jugadores con manejo de descartes
def repartir_cartas(jugadores,baraja, num_cartas_por_jugador, descartes):
    """
    Reparte cartas de la baraja según el número de cartas solicitado por cada jugador.

    Args:
    - baraja (list): Lista de cartas disponibles.
    - num_cartas_por_jugador (list): Lista de enteros indicando cuántas cartas pide cada jugador.
    - descartes (list): Lista de cartas descartadas disponibles.

    Returns:
    - manos (dict): Diccionario con las cartas repartidas por jugador.
    - baraja (list): Baraja restante tras repartir las cartas.
    - descartes (list): Cartas que quedan como descartadas.
    """
    total_cartas_solicitadas = sum(num_cartas_por_jugador)
    jugadores=jugadores

    # Si no hay suficientes cartas en la baraja, usar los descartes
    if len(baraja) < total_cartas_solicitadas:
        print("No hay suficientes cartas en la baraja. Usando descartes.")
        baraja.extend(descartes)
        random.shuffle(baraja)
        descartes.clear()

    if len(baraja) < total_cartas_solicitadas:
        raise ValueError("No hay suficientes cartas incluso con descartes.")

    # Mezclar la baraja
    random.shuffle(baraja)
    
    # Crear las manos de los jugadores utilizando los nombres de la lista
    manos = {jugador: [] for jugador in jugadores}

    # Distribuir las cartas a cada jugador
    for i, num_cartas in enumerate(num_cartas_por_jugador):
        for _ in range(num_cartas):
            carta = baraja.pop()  # Extraer una carta de la baraja
            manos[jugadores[i]].append(carta)  # Asignar la carta al jugador correspondiente


        # Criterio de ordenación para el Mus
    def criterio_mus(carta):
        """
        Define el criterio de ordenación para el Mus:
        - Extrae el valor numérico de la carta y da prioridad a los treses y reyes.
        """
        valor = int(carta[:-1])  # Extrae el número de la carta (elimina el último carácter, que es el palo)
        if valor == 3 or valor == 12:  # Los treses y reyes equivalen a 12
            return 12
        return valor

    # Ordenar las manos de los jugadores según el criterio
    for jugador in manos:
        manos[jugador].sort(key=criterio_mus, reverse=True)        

    '''
    # Crear las manos de los jugadores
    manos = {f"Jugador {i+1}": [] for i in range(len(num_cartas_por_jugador))}

    for i, num_cartas in enumerate(num_cartas_por_jugador):
        for _ in range(num_cartas):
            carta = baraja.pop()  # Extraer una carta de la baraja
            manos[f"Jugador {i+1}"].append(carta) 
    '''

    return manos, baraja, descartes

# Repartir cartas solo a un jugador con manejo de descartes 
def repartir_cartas_jugador(jugador, baraja, num_cartas, descartes, mesa_id):
    """
    Reparte cartas de la baraja a un jugador específico.

    Args:
    - jugador (str): Nombre del jugador que recibirá las cartas.
    - baraja (list): Lista de cartas disponibles.
    - num_cartas (int): Número de cartas que solicita el jugador.
    - descartes (list): Lista de cartas descartadas disponibles.

    Returns:
    - mano (list): Lista de cartas repartidas al jugador.
    - baraja (list): Baraja restante tras repartir las cartas.
    - descartes (list): Cartas que quedan como descartadas.
    """
    # Si no hay suficientes cartas en la baraja, usar los descartes
    if len(baraja) < num_cartas:
        print("No hay suficientes cartas en la baraja. Usando descartes.")
        emit('mensaje_mesa', {'msg': f"{jugador}, no hay suficientes cartas en la baraja. Usando descartes.", 'username': 'Docemas'}, to=mesa_id)
        baraja.extend(descartes)
        random.shuffle(baraja)
        descartes.clear()

    if len(baraja) < num_cartas:
        raise ValueError("No hay suficientes cartas incluso con descartes.")

    # Mezclar la baraja
    random.shuffle(baraja)

    # Repartir las cartas al jugador
    mano = []
    for _ in range(num_cartas):
        carta = baraja.pop()  # Extraer una carta de la baraja
        mano.append(carta)   # Asignar la carta al jugador

    print(f"Cartas repartidas a {jugador}: {mano}")

        # Criterio de ordenación para el Mus
    def criterio_mus(carta):
        """
        Define el criterio de ordenación para el Mus:
        - Extrae el valor numérico de la carta y da prioridad a los treses y reyes.
        """
        valor = int(carta[:-1])  # Extrae el número de la carta (elimina el último carácter, que es el palo)
        if valor == 3 or valor == 12:  # Los treses y reyes equivalen a 12
            return 12
        return valor

    # Ordenar las manos de los jugadores según el criterio
    mano.sort(key=criterio_mus, reverse=True)   

    return mano, baraja, descartes


###  diseño ajustado para manejar descartes por jugador

### Actualizamos la función de `handle_descartar_cartas` para integrar los descartes enviados por los jugadores.
@socketio.on('descartar_cartas')
def handle_descartar_cartas(data):
    mesa_id = data['mesa_id']
    username = data['username']
    descartes = data['cartas_descartadas']
    
    try:
        mesa = tables.get(mesa_id)
        if not mesa:
            raise KeyError(f"No se encontró la mesa con ID {mesa_id}")

        # Validar que las manos están inicializadas correctamente
        if 'manos' not in mesa or not isinstance(mesa['manos'], dict):
            raise ValueError(f"'manos' no está definido o no es un diccionario en la mesa {mesa_id}")

        # Buscar el índice del jugador basado en el username
        jugadores = mesa.get('jugadores', [])
        if username not in jugadores:
            raise ValueError(f"El jugador {username} no está en la mesa {mesa_id}")
        
        jugador_index = jugadores.index(username)
        jugador_key = f"Jugador {jugador_index + 1}"  # Clave en el diccionario de manos
        print(f"Jugador_index: ", jugador_index, " jugador_key: ", jugador_key)

        # Actualizar la mano del jugador eliminando las cartas descartadas
        mesa['manos'][jugador_key] = [
            carta for carta in mesa['manos'][jugador_key] if carta not in descartes
        ]
        print(f"DESCARTE: Actualiza la mano del jugador index: ", mesa['manos'][jugador_key])
        # Añadir los descartes al pool de descartes de la mesa
        if 'descartes' not in mesa or not isinstance(mesa['descartes'], list):
            mesa['descartes'] = []

        mesa['descartes'].extend(descartes)
        print(f"Actualiza tables con mesa ")
        # Guardar los cambios en la estructura de la mesa
        tables[mesa_id] = mesa
        print(f"Va a hacer el emit a clientes Descartes: ", mesa['descartes'])
        # Emitir los descartes actualizados a los clientes
        emit('descartes_actualizados', {'mesa_id': mesa_id, 'descartes': mesa['descartes']},  to=mesa_id)
        # Emitir las nuevas cartas al jugador
        #print("cartas_repartidas ",
        #    "mesa_id:", mesa_id, "username: ", username, " mesa(manos)jugindex: ", mesa['manos'][jugador_index])

        #emit('cartas_repartidas', {'mesa_id': mesa_id,'username': username,'cartas': mesa['manos'][jugador_index]}, room=mesa_id)
    except (KeyError, ValueError) as e:
        emit('error', {'message': str(e)}, to=mesa_id)

@socketio.on('pedir_cartas')
def handle_pedir_cartas(data):
    """
    Recibe la solicitud de cartas de un jugador y distribuye cartas de la baraja o de los descartes.
    """
    mesa_id = data['mesa_id']
    jugador = data['jugador']
    num_cartas = data['num_cartas']
    cartasEnMano = data['cartasRestantes']

    print(f"Cartas en mano de {jugador}: ", cartasEnMano, " cartas solicitadas: ", num_cartas)

    try:
        mesa = tables.get(mesa_id)
        if not mesa:
            raise KeyError(f"No se encontró la mesa con ID {mesa_id}")
        baraja = mesa.get('baraja', crear_baraja())
        descartes = mesa.get('descartes', [])
        manos = mesa['manos']
        jugadores = mesa['jugadores']
        mesa['musContador'] += 1

        # Verificar si la mano del jugador existe
        if jugador not in manos:
            raise KeyError(f"El jugador {jugador} no está en la mesa.")

        # Repartir cartas al jugador
        nuevas_cartas, baraja, descartes = repartir_cartas_jugador(
            jugador,
            baraja,
            num_cartas,
            descartes,
            mesa_id
        )
        print(f"Cartas nuevas de {jugador}: ", nuevas_cartas)
        # Actualizar la mano del jugador
        manos[jugador] = []  # Vaciar la mano del jugador
        manos[jugador].extend(cartasEnMano)  # Añadir las cartas que el jugador conservó
        manos[jugador].extend(nuevas_cartas)  # Añadir las nuevas cartas recibidas
      # print("La mano del jugador después de nuevas cartas:", manos[jugador])
        mesa['baraja'] = baraja
        mesa['descartes'] = descartes
        mesa['manos'] = manos
        mesa['turno_anterior'] = mesa['turno_actual']
        mesa['turno_actual'] = (mesa['turno_actual'] + 1) % len(mesa['jugadores'])  
       # mesa['turno_actual'] = mesa['mano']
        #jugador_turno = jugadores[mesa["mano"]] 
        jugador_turno = jugadores[mesa["turno_actual"]] 
        print("Mesa después de pedir cartas:", mesa)
        print(f'Va a hacer el emit a cartas pedidas con: ', {'jugador': jugador, 'turno_actual': jugador_turno, 'nuevas_cartas': manos[jugador]})
        # Emitir las nuevas cartas al jugador
        emit('cartas_pedidas', {'jugador': jugador, 'turno_actual': jugador_turno, 'contDescartados': mesa['musContador'], 'nuevas_cartas': manos[jugador]},  to=mesa_id)
        
        if num_cartas == 1:
            cartulaje = " carta"
        else:
            cartulaje = " cartas"
        tables[mesa_id] = mesa 
        emit('mensaje_mesa', {'msg': f"{jugador} pide {num_cartas} {cartulaje}. Habla {jugador_turno}", 'username': 'Docemas'}, to=mesa_id)
        emit('mostrarMensaje', {'msg': f"{jugador} pide {num_cartas} {cartulaje}",'jugador': jugador, 'num_cartas': num_cartas, 'cartulaje': cartulaje}, to=mesa_id)

        if (mesa['musContador'] == 4):
            mesa["musContador"] = 0
        tables[mesa_id] = mesa  # Guardar cambios

    except KeyError as e:
        emit('error', {'mensaje_mesa': str(e)},  to=mesa_id)
    except ValueError as e:
        emit('error', {'mensaje_mesa': "No hay suficientes cartas para completar el reparto."},  to=mesa_id)

#####  CÓDIGO PARA CONTROLAR lOS EVENTOS DE CADA TURNO ####################################################

@socketio.on('tratar_mus')
def tratar_mus(data):
    ## Comunicamos a todos quien se ha dado MUS y pasamos turno al siguiente
    mesa_id = data['mesa_id']
    mesa = tables.get(mesa_id)
    jugadores = mesa['jugadores']
    jugadorAntes = jugadores[mesa["turno_actual"]]
    #print("Antes de actualizar: indice mano: ", mesa['mano'], " indica turno_actual: ",  mesa['turno_actual'])
    mesa['musContador'] += 1
    print("TRATAR_MUS 1: mesa['mano']: ", mesa['mano'])
    mesa['estado_partida'] = "Mus"
    # Si es la primera ronda el nuevo mano corre un turno, sino el mano corre con la nueva ronda
    if mesa["juegos"][0] == 0 and mesa["puntos"][0] == 0 and mesa["juegos"][1] == 0 and mesa["puntos"][1] == 0:
        mesa['mano'] = (mesa['mano'] + 1) % len(mesa['jugadores'])
        print("[DEBUG] TRATAR MUS. mesa['mano']: ", mesa['mano'])

    mesa['turno_anterior'] = mesa['turno_actual']
    mesa['turno_actual'] = (mesa['turno_actual'] + 1) % len(mesa['jugadores'])   
    musContador = mesa['musContador']
    jugador_turno = jugadores[mesa["turno_actual"]]

    print("TRATAR MUS: El mano es : ", jugadores[mesa['mano']], " indice mano: ", mesa['mano'])
    print("TRATAR MUS: El turno es: ", jugadores[mesa['turno_actual']], " indice actual: ", mesa['turno_actual'], " jugador antes: ", jugadorAntes)

    #print("En tratar_mus Contador: ", musContador, " jugador antes  ", jugadorAntes, ", siguiente: ", jugador_turno, ", turno actual: ", mesa['turno_actual'])
    #print("Despues de actualizar: indice mano: ", mesa['mano'], " indica turno_actual: ",  mesa['turno_actual'])
    #emit('mensaje_mesa', {'msg': f"{jugadorAntes} se da MUS. Habla {jugador_turno}", 'username': 'Docemas'}, to=mesa_id)
  
    # Si es la primera ronda y todos pasan, el nuevo mano corre un turno, sino el que toque
    #if mesa["juegos"] == [0,0] and mesa["puntos"] == [0,0]:
    if mesa["juegos"][0] == 0 and mesa["puntos"][0] == 0 and mesa["juegos"][1] == 0 and mesa["puntos"][1] == 0:
        if (musContador == 4):
            #mesa['mano'] = (mesa['mano'] + 1) % len(mesa['jugadores'])
            mesa['turno_anterior'] = mesa['turno_actual']
            mesa['turno_actual'] = (mesa['turno_actual'] + 1) % len(mesa['jugadores'])   
            jugador_turno = jugadores[mesa["turno_actual"]]  
            print("[DEBUG] TRATAR MUS. CONTADOR ES 4 mesa['mano']: ", mesa['mano'])

    if (musContador == 4):
        mesa['estado_partida'] = "Descartar"
    
    emit('actualizar_mus', {
        'musContador': mesa['musContador'],
        'indiceActual': mesa['turno_actual'],        
        'jugadorActual': jugador_turno
    }, to=mesa_id)

    if (musContador == 4):
        mesa["musContador"] = 0
        emit('mensaje_mesa', {'msg': f"{jugadorAntes} se da MUS. {jugador_turno} es ahora el mano y le toca descartarse.", 'username': 'Docemas'}, to=mesa_id)
    else:
        emit('mensaje_mesa', {'msg': f"{jugadorAntes} se da MUS. Habla {jugador_turno}", 'username': 'Docemas'}, to=mesa_id)

    tables[mesa_id] = mesa  # Guardar cambios


@socketio.on('tratar_corto')
def tratar_corto(data):
    mesa_id = data['mesa_id']
    mesa = tables.get(mesa_id)
    jugadores = mesa['jugadores']
    mesa['estado_partida'] = "Cortar"
    # Si es la primera ronda el mano es el que corta, sino el que toque
    if mesa["juegos"][0] == 0 and mesa["puntos"][0] == 0 and mesa["juegos"][1] == 0 and mesa["puntos"][1] == 0:
        jugador_turno = jugadores[mesa["turno_actual"]]
        indice_mano = mesa["turno_actual"]
        mesa['mano'] = indice_mano
        print("TRATAR_CORTO 1: jugador_turno: ", jugador_turno, " mesa['mano']: ", mesa['mano'])
    else:
      # mesa['mano'] = (mesa['mano'] + 1) % len(mesa['jugadores'])
        jugador_turno = jugadores[mesa['mano']]
        indice_mano = mesa['mano']
        print("TRATAR_CORTO 2: jugador_turno: ", jugador_turno, " mesa['mano']: ", mesa['mano'])

    emit('mensaje_mesa', {'msg': f"Comienza nueva ronda, {jugador_turno} es el mano.", 'username': 'Docemas'}, to=mesa_id)
    #print("TRATAR_CORTO: En tratar_corto Mesa_ID: ", mesa_id, " jugador_turno: ", jugador_turno)

    # jugadores = mesa['jugadores']
    # manos = mesa['manos']
    ## Aquí definimos los datos para la ronda dentro de la mesa:

    mesa["turno_actual"] = mesa['mano']
    mesa["pares_confirmados"] = {jugador: None for jugador in mesa["jugadores"]}
    mesa["lance_actual"] = "Grande"  # Lance activo: grande, chica, pares o juego
    mesa["accion"] = ""
    mesa["acciones"] = [None, None, None, None, None]
    mesa["apuesta"] = [0, 0, 0, 0, 0]
    mesa["apuesta_actual"] = 0
    mesa["apuesta_anterior"] = 0    
    tables[mesa_id] = mesa  # Guardar cambios
    reiniciar_hablado(mesa)
    print("lance actual: ", mesa['lance_actual'])
    print(f"TRATAR_CORTO: Va a hacer el emit comenzar ronda con: ", {'jugador turno': jugador_turno})    
    emit('comenzar_ronda', {'mesa_id': mesa_id,
                            'turno_actual': indice_mano, 
                            'jugador_turno': jugador_turno,
                            'lance_actual': mesa['lance_actual']}, 
                             to=mesa_id)

##########################################################################################################
#####  CÓDIGO PARA CONTROLAR LOS LANCES DE CADA TURNO ####################################################
##########################################################################################################

@socketio.on('accion_jugador')
def manejar_accion(data):
    """
    Maneja las acciones de los jugadores.
    """
    print("[DEBUG] Entra en manejar accion.")

    mesa_id = data['mesa_id']
    jugador = data['jugador']
    accion = data['accion']
    acciona = accion

    envido = data.get('envido', 0)  # Valor del envido si aplica

    # Recuperar la mesa
    mesa = tables.get(mesa_id)
    puntos_juego = mesa['puntos_juego']

    if accion == "Órdago": 
        envido = puntos_juego  # Órdago tiene un valor alto fijo de la variable global puntos_juego  
        acciona = "lanza un ¡¡¡ÓRDAGO!!!"

    print(f"[DEBUG] Manejar Acción. Mesa_id: {mesa_id}, Jugador: {jugador}, Acción: {accion}, Apuesta: {envido}")

    #debug_manos(mesa)
    mesa['estado_partida'] = "Jugar"
    # Validar que 'lance_actual' no sea None
    #if mesa["lance_actual"] is None:
    #    raise ValueError("[ERROR] Manejar accion: 'lance_actual' no está definido en la mesa.")

    # Validar que 'lance_actual' esté en la lista de 'lances'
    if mesa["lance_actual"] not in mesa["lances"]:
        raise ValueError(f"[ERROR] 'Manejar accion: Lance_actual' ({mesa['lance_actual']}) no está en la lista de 'lances': {mesa['lances']}.")
  
    indice_apuesta = mesa['lances'].index(mesa["lance_actual"])
    mesa["accion"] = accion
    mesa["acciones"][indice_apuesta] = accion
    mesa["jugadorAnterior"] = jugador

    # Guardamos la apusta última y si ha habido rebote la inmediata anterior
    if envido > 0:
        mesa["apuesta_anterior"] = mesa["apuesta_actual"]
        mesa["apuesta_actual"] = envido
        if envido < 40:
            acciona = "envida " + str(envido)

    print(f"[DEBUG] Manejar Acción. Jugador: {jugador}, Lance: {mesa['lance_actual']}, Acción: {accion}, Apuesta: {mesa['apuesta']}")

    # 
    # TRATAMOS LOS LANCES DE GRANDE, CHICA Y PARES:
    #     
    if mesa["lance_actual"] in ["Grande", "Chica", "Punto"]:
        
        if accion in ["Envido", "Órdago"]:
            mesa["jugadorApuesta"] = jugador
            mesa["apuesta"][indice_apuesta] += envido
            mesa["estado_jugadores"][jugador]["ha_hablado"] = True
            reiniciar_hablado(mesa) 
            avanzar_turno(mesa)  # Turno para que el rival responda
            emit('mensaje_mesa', {'msg': f"{jugador} {acciona}.", 'username': mesa['lance_actual']}, to=mesa_id)
            print("[DEBUG] Manejar Acción: Estado actualizado 1 desde ", mesa['lance_actual'], " - ", accion)
            emit('estado_actualizado', mesa, to=mesa_id)
            return 
            
        if accion == "Veo":
            if mesa["apuesta"][indice_apuesta] >= mesa['puntos_juego']: # Se ve el Órdago, vamos directamente a ver el ganador
                if mesa["lance_actual"] == "Grande":
                    determinar_ganador_grande(mesa)
                elif mesa["lance_actual"] == "Chica":
                    determinar_ganador_chica(mesa)
                elif mesa["lance_actual"] == "Punto":
                    determinar_ganador_punto(mesa)
                return            
            else:    
                mesa["acciones"][indice_apuesta] = accion
                emit('mensaje_mesa', {'msg': f"{jugador} ve el envite.", 'username': mesa["lance_actual"]}, to=mesa_id)
                ganador = None  # Se determina el ganador al final de la ronda salvo que sea Órdago
                registrar_lance(mesa, ganador, mesa["lance_actual"], mesa["apuesta"][indice_apuesta], 0)
                reiniciar_hablado(mesa)
                pasar_a_siguiente_lance(mesa) # Hace el emit
                return
        
        if accion == "Paso":
            mesa["estado_jugadores"][jugador]["ha_hablado"] = True
            print("[DEBUG] Manejar Acción: Estado de jugadores antes de verificar todos_han_pasado:")
            for jugador, estado in mesa["estado_jugadores"].items():
                print(f"Debuf: manejar_accion: PASO en lance {mesa['lance_actual']}. estado_jugadores: {jugador}: {estado}")

            if todos_han_pasado(mesa):
                emit('mensaje_mesa', {'msg': f"{mesa['jugadorAnterior']} dice: {accion}.", 'username': mesa['lance_actual']}, to=mesa_id)
                print(f"[DEBUG] Manejar Acción: Todos los jugadores han pasado en {mesa['lance_actual']}. Finalizando el lance.")
                ganador = None  # Se determina el ganador al final de la ronda 
                registrar_lance(mesa, ganador, mesa["lance_actual"], mesa["apuesta"][indice_apuesta], 1)
                reiniciar_hablado(mesa)
                pasar_a_siguiente_lance(mesa) # Hace el emit
                return
            else:
                print("[DEBUG] No todos han pasado todavía. Avanzando turno.")
                print("[DEBUG] Manejar Acción: Estado actualizado 2 desde ", mesa['lance_actual'], " - ", accion)
                emit('mensaje_mesa', {'msg': f"{mesa['jugadorAnterior']} dice: {accion}.", 'username': mesa['lance_actual']}, to=mesa_id)
                avanzar_turno(mesa)
                emit('estado_actualizado', mesa, to=mesa_id)
                return
    # 
    # TRATAMOS EL LANCE DE PARES:
    #     
    if mesa["lance_actual"] == "Pares":
        jugadores_con_pares = [
            jugador for jugador, tiene_pares in mesa["pares_confirmados"].items() if tiene_pares
        ]
        if accion in ["Envido", "Órdago"]:
            # El jugador envida (apuesta)
            mesa["jugadorApuesta"] = jugador
            mesa["apuesta"][indice_apuesta] += envido  # Incrementa la apuesta
            mesa["estado_jugadores"][jugador]["ha_hablado"] = True
            print(f"[DEBUG] Manejar Acción:  {jugador} envida. Apuesta actual: {mesa['apuesta'][indice_apuesta]}")
            reiniciar_hablado(mesa) 
            avanzar_turno(mesa)  # Turno para el siguiente jugador con pares
            print("[DEBUG] Manejar Acción: Estado actualizado 3 desde ", mesa['lance_actual'], " - ", accion)
            emit('mensaje_mesa', {'msg': f"{jugador} {acciona}.", 'username': mesa['lance_actual']}, to=mesa_id)
            emit('estado_actualizado', mesa, to=mesa_id)
            return

        elif accion == "Veo":
            if mesa["apuesta"][indice_apuesta] >= mesa['puntos_juego']: # Se ve el Órdago, vamos directamente a ver el ganador
                determinar_ganador_pares(mesa)
                return
            else: 
                # El jugador acepta la apuesta; se cierra el lance
                mesa["acciones"][2] = accion
                emit('mensaje_mesa', {'msg': f"{jugador} ve el envite.", 'username': mesa['lance_actual']}, to=mesa_id)
                print(f"[DEBUG] Manejar Acción: {jugador} ve la apuesta de {mesa['apuesta'][indice_apuesta]}. Cerrando el lance.")
                ganador = None  # Se determina el ganador al final de la ronda salvo que sea Órdago
                registrar_lance(mesa, ganador, "Pares", mesa["apuesta"][indice_apuesta], 0)
                reiniciar_hablado(mesa)
                pasar_a_siguiente_lance(mesa)
                return

        elif accion == "Paso":
            mesa["estado_jugadores"][jugador]["ha_hablado"] = True
            # Si todos los jugadores con pares han pasado, termina el lance
            if todos_han_pasado(mesa):
                emit('mensaje_mesa', {'msg': f"{mesa['jugadorAnterior']} dice: {accion}.", 'username': mesa['lance_actual']}, to=mesa_id)
                print(f"[DEBUG] Manejar Acción: PASO, Todos los jugadores han pasado en {mesa['lance_actual']}. Finalizando el lance.")
                ganador = None  # Se determina el ganador al final de la ronda 
                registrar_lance(mesa, ganador, mesa["lance_actual"], mesa["apuesta"][indice_apuesta], 1)
                reiniciar_hablado(mesa)
                pasar_a_siguiente_lance(mesa) # Hace el emit
                return
            else:
                print("[DEBUG] No todos han pasado todavía. Avanzando turno.")
                # Si no, simplemente avanza el turno per tiene que ser al siguiente con pares
                avanzar_turno(mesa)
                print("[DEBUG] Manejar Acción: Estado actualizado 4 desde ", mesa['lance_actual'], " - ", accion)
                emit('mensaje_mesa', {'msg': f"{jugador} dice: {accion}.", 'username': mesa['lance_actual']}, to=mesa_id)
                emit('estado_actualizado', mesa, to=mesa_id)
                return
    # 
    # TRATAMOS EL LANCE DE JUEGO:
    # 
    if mesa["lance_actual"] == "Juego":
        jugadores_con_juego = [
            jugador["jugador"] for jugador in mesa["estado_juego"] if jugador["tiene_juego"]
        ]

        if accion in ["Envido", "Órdago"]:
            # El jugador envida (apuesta)
            mesa["jugadorApuesta"] = jugador
            mesa["apuesta"][indice_apuesta] += envido  # Incrementa la apuesta
            mesa["estado_jugadores"][jugador]["ha_hablado"] = True
            print(f"[DEBUG] Manejar Acción: {jugador} envida. Apuesta actual: {mesa['apuesta']}")
            reiniciar_hablado(mesa) 
            avanzar_turno(mesa)  # Turno para el siguiente jugador con juego
            print("[DEBUG] Manejar Acción: Estado actualizado 5 desde ", mesa['lance_actual'], " - ", accion)
            emit('mensaje_mesa', {'msg': f"{jugador} {acciona}.", 'username': mesa['lance_actual']}, to=mesa_id)
            emit('estado_actualizado', mesa, to=mesa_id)
            return
        
        if accion == "Veo":
            if mesa["apuesta"][indice_apuesta] >= mesa['puntos_juego']: # Se ve el Órdago, vamos directamente a ver el ganador
                determinar_ganador_juego(mesa)
                return
            else: 
                # El jugador acepta la apuesta; se cierra el lance
                mesa["acciones"][3] = accion
                emit('mensaje_mesa', {'msg': f"{jugador} ve el envite.", 'username': mesa['lance_actual']}, to=mesa_id)
                print(f"[DEBUG] Manejar Acción: {jugador} ve la apuesta de {mesa['apuesta'][indice_apuesta]}. Cerrando el lance.")
                ganador = None  # Se determina el ganador al final de la ronda salvo que sea Órdago
                registrar_lance(mesa, ganador, "Juego", mesa['apuesta'][indice_apuesta], 0)
                reiniciar_hablado(mesa)
                pasar_a_siguiente_lance(mesa)
                return

        if accion == "Paso":
            mesa["estado_jugadores"][jugador]["ha_hablado"] = True
            # Si todos los jugadores con juego han pasado, termina el lance
            if todos_han_pasado(mesa):
                emit('mensaje_mesa', {'msg': f"{mesa['jugadorAnterior']} dice: {accion}.", 'username': mesa['lance_actual']}, to=mesa_id)
                print(f"[DEBUG] Manejar Acción: PASO. Todos los jugadores con juego han pasado en {mesa['lance_actual']}. Finalizando el lance.")
                ganador = None  # Se determina el ganador al final de la ronda 
                registrar_lance(mesa, ganador, mesa["lance_actual"], mesa["apuesta"][indice_apuesta], 1)
                reiniciar_hablado(mesa)
                pasar_a_siguiente_lance(mesa) # Hace el emit
                return
            else:
                print("[DEBUG] No todos han pasado todavía. Avanzando turno.")
                # Si no, simplemente avanza el turno per tiene que ser al siguiente con juego
                avanzar_turno(mesa)
                print("[DEBUG] Manejar Acción: Estado actualizado 6 desde ", mesa['lance_actual'], " - ", accion)
                emit('mensaje_mesa', {'msg': f"{jugador} dice: {accion}.", 'username': mesa['lance_actual']}, to=mesa_id)
                emit('estado_actualizado', mesa, to=mesa_id)
                return

    # Verificar si todos los jugadores han hablado
    if todos_jugadores_han_hablado(mesa):
        # Registrar el lance actual si nadie apostó
        print("[DEBUG] Manejar Acción: Todos los jugadores han hablado.")
        ganador = determinar_ganador(mesa)
        registrar_lance(mesa, ganador, mesa["lance_actual"], mesa["apuesta"][indice_apuesta], 1)
        reiniciar_hablado(mesa)
        pasar_a_siguiente_lance(mesa) # Ya hace emit 
        return

    # Guardar cambios en la mesa
    tables[mesa_id] = mesa
    print("[DEBUG] Manejar Acción: Va a emitir estado actualizado: siguiente turno:", mesa['turno_actual'], " lance: ", mesa['lance_actual'])
    print("[DEBUG] Manejar Acción: Estado actualizado 7 desde ", mesa['lance_actual'], " - ", accion)
    # Enviar estado actualizado a todos los clientes
    emit('estado_actualizado', mesa, to=mesa_id)

# Funcion preparada para simplificar el código de manejar_accion. De momento no se llama.
def procesar_lance(mesa):
    print("[DEBUG] Procesar lance: Todos los jugadores han hablado.")
    indice_apuesta = mesa['lances'].index(mesa["lance_actual"])
    ganador = determinar_ganador(mesa)
    registrar_lance(mesa, ganador, mesa["lance_actual"], mesa["apuesta"][indice_apuesta], 1)
    reiniciar_hablado(mesa)
    pasar_a_siguiente_lance(mesa) # Ya hace emit 
    # Guardar cambios en la mesa
    tables[mesa['nombre']] = mesa    
    return

def todos_han_pasado(mesa):
    """
    Verifica si todos los jugadores relevantes han pasado en el lance actual.
    """
    #print("[DEBUG] Entra en todos han pasado. mesa[estado_juego]: ", mesa["estado_juego"])

    indice_apuesta = mesa['lances'].index(mesa["lance_actual"])

    if mesa["lance_actual"] == "Pares":
        jugadores_relevantes = [
            jugador for jugador, tiene_pares in mesa["pares_confirmados"].items() if tiene_pares
        ]
    elif mesa["lance_actual"] == "Juego":
        jugadores_relevantes = [
            jugador["jugador"] for jugador in mesa["estado_juego"] if jugador["tiene_juego"]
        ]
    else:
        jugadores_relevantes = mesa["jugadores"]  # Para Grande, Chica y Punto

    if mesa["apuesta"][indice_apuesta] > 0:
    #    if mesa["lance_actual"] in ["Grande", "Chica", "Punto"]:
    #        jugadores_relevantes = mesa["pareja_contraria"]
    #    else:
        jugadores_relevantes = mesa["pareja_contraria"]

    print("[DEBUG] todos_han_pasado. Jugadores relevantes: ", jugadores_relevantes)
    print("[DEBUG] todos_han_pasado. Estado de cada jugador:", {j: mesa['estado_jugadores'][j] for j in jugadores_relevantes})

    # Verifica que todos los jugadores relevantes hayan pasado
    return all(
        mesa["estado_jugadores"][jugador]["ha_hablado"] and mesa["accion"] == "Paso"
        for jugador in jugadores_relevantes
    )

def todos_jugadores_han_hablado(mesa):

    indice_apuesta = mesa['lances'].index(mesa["lance_actual"])

    if mesa["lance_actual"] == "Pares":
        jugadores_relevantes = [
            jugador for jugador, tiene_pares in mesa["pares_confirmados"].items() if tiene_pares
        ]
    elif mesa["lance_actual"] == "Juego":
        jugadores_relevantes = [
            jugador["jugador"] for jugador in mesa["estado_juego"] if jugador["tiene_juego"]
        ]
    else:
        jugadores_relevantes = mesa["jugadores"]  # Para Grande, Chica y Punto

    if mesa["apuesta"][indice_apuesta] > 0:
    #    if mesa["lance_actual"] in ["Grande", "Chica", "Punto"]:
    #        jugadores_relevantes = mesa["pareja_contraria"]
    #    else:
        jugadores_relevantes = mesa["pareja_contraria"]

    print("[DEBUG] todos_han_hablado. Jugadores relevantes: ", jugadores_relevantes)
    print("[DEBUG] todos_han_hablado. Estado de cada jugador:", {j: mesa['estado_jugadores'][j] for j in jugadores_relevantes})

    # Verifica que todos los jugadores relevantes hayan hablado
    return all(
        mesa["estado_jugadores"][jugador]["ha_hablado"] for jugador in jugadores_relevantes
    )
    #return all(estado.get("ha_hablado", False) for estado in mesa["estado_jugadores"].values())


def avanzar_turno(mesa):
    """
    Avanza el turno al siguiente jugador válido según el lance actual y las reglas del juego.
    """
    turno_actual = mesa["turno_actual"]
    jugador_actual = mesa["jugadores"][turno_actual]
    indice_apuesta = mesa['lances'].index(mesa["lance_actual"])
    envite = mesa["apuesta"][indice_apuesta]
    
    print(f"[DEBUG] Avanzar_turno. Jugador: {jugador_actual}, Lance: {mesa['lance_actual']}, acción: {mesa['accion']}")
    # Función para obtener la pareja de un jugador
    def obtener_pareja(jugador):
        idx = mesa["jugadores"].index(jugador)
        return 1 if idx % 2 == 0 else 2

    # Actualizar pareja apostadora y pareja contraria si es necesario
    if mesa["accion"] in ["Envido", "Órdago"]:
        pareja_apostadora = obtener_pareja(jugador_actual)
        mesa["pareja_apostadora"] = pareja_apostadora
        print(f"[DEBUG] Avanzar_turno. Pareja apostadora: {pareja_apostadora}")
        pareja_contraria = 1 if pareja_apostadora == 2 else 2
        jugadores_contrarios = [
            jugador for jugador in mesa["jugadores"]
            if obtener_pareja(jugador) == pareja_contraria
        ]
        mesa["pareja_contraria"] = jugadores_contrarios 
        print(f"[DEBUG] Avanzar_turno. Lance: {mesa['lance_actual']}, acción: {mesa['accion']} Jugadores contrarios: {jugadores_contrarios}")
    elif envite > 0:
        jugadores_contrarios = mesa["pareja_contraria"]
    else:
        jugadores_contrarios = mesa["jugadores"]

    # Determinar jugadores válidos según el lance
    if mesa["lance_actual"] == "Pares":
        jugadores_validos = [
            jugador for jugador in jugadores_contrarios
            if mesa["pares_confirmados"].get(jugador, False)
        ]
        mesa["pareja_contraria"] = jugadores_validos
    elif mesa["lance_actual"] == "Juego":
        jugadores_validos = [
            jugador["jugador"] for jugador in mesa["estado_juego"]
            if jugador["tiene_juego"] and jugador["jugador"] in jugadores_contrarios
        ]
        mesa["pareja_contraria"] = jugadores_validos
    else:
        jugadores_validos = jugadores_contrarios

    print(f"[DEBUG] Avanzar_turno. Lance: {mesa['lance_actual']}, acción: {mesa['accion']} Jugadores válidos: {jugadores_validos}")

    # Si no hay jugadores válidos, pasar al siguiente lance
    if not jugadores_validos:
        reiniciar_hablado(mesa)
        pasar_a_siguiente_lance(mesa)
        return

    # Marcar al jugador actual como que ya ha hablado
    #if jugador_actual in jugadores_validos:
     #   mesa["estado_jugadores"][jugador_actual]["ha_hablado"] = True

    # Buscar el siguiente jugador válido
    for _ in range(len(mesa["jugadores"])):
        mesa['turno_anterior'] = mesa['turno_actual']
        mesa["turno_actual"] = (mesa["turno_actual"] + 1) % len(mesa["jugadores"])
        siguiente_jugador = mesa["jugadores"][mesa["turno_actual"]]
        if siguiente_jugador in jugadores_validos:
            break

    print(f"[DEBUG] Avanzar_turno. Siguiente turno: {mesa['jugadores'][mesa['turno_actual']]}")



def reiniciar_hablado(mesa):
    """
    Inicializa el estado de los jugadores en la mesa usando los nombres reales de mesa["jugadores"].
    """
    if "jugadores" in mesa:
        mesa["estado_jugadores"] = {
            jugador: {"ha_hablado": False} for jugador in mesa["jugadores"]
        }
        print("Estado de jugadores inicializado:", mesa['estado_jugadores'])
    else:
        raise KeyError("La clave 'jugadores' no está presente en la mesa.")


def pasar_a_siguiente_lance(mesa):
    """
    Avanza al siguiente lance en el orden predefinido.
    Si se trata del lance de pares, evalúa las condiciones especiales.
    """
    print("[DEBUG] Entra en pasar a siguiente lance: ", mesa['lance_actual'])
    mesa_id = mesa["nombre"]
    lances = ["Grande", "Chica", "Pares", "Juego", "Punto"]
    indice_actual = lances.index(mesa["lance_actual"])
    mesa["apuesta_actual"] = 0
    mesa["apuesta_anterior"] = 0

    if mesa["lance_actual"] == "Juego":
        finalizar_ronda(mesa) 
        return

    # Bloqueamos los botones de la mesa antes de entrar en Pares o Juego par dar tiempo a que se cante
    #if mesa["lance_actual"] in ["Chica", "Pares"]:
    #    emit('bloquear_mesa_botones', mesa["lance_actual"], to=mesa_id)

    if indice_actual + 1 < len(lances):
        mesa["lance_actual"] = lances[indice_actual + 1]
        mesa["turno_actual"] = mesa["mano"]  # Reiniciar turno para el nuevo lance
        print(f"[DEBUG] Avanzando al siguiente lance: {mesa['lance_actual']} (índice: {indice_actual})")
        reiniciar_hablado(mesa)
        print(f"Se pasa al lance: {mesa['lance_actual']} y se reinicia hablado.")

        if mesa["lance_actual"] == "Grande":
            print("[DEBUG] Pasar_a_siguiente_lance: Estado actualizado 8 desde ", mesa['lance_actual'])
            emit('estado_actualizado', mesa, to=mesa_id)

        if mesa["lance_actual"] == "Chica":
            print("[DEBUG] Pasar_a_siguiente_lance: Estado actualizado 9 desde ", mesa['lance_actual'])
            emit('estado_actualizado', mesa, to=mesa_id)

        if mesa["lance_actual"] == "Pares":
            print("[DEBUG] Pasar_a_siguiente_lance: Estado actualizado 10 desde ", mesa['lance_actual'])
            emit('estado_actualizado', mesa, to=mesa_id)
            emit('bloquear_mesa_botones', mesa['lance_actual'], to=mesa_id)
            print("[DEBUG] Comenzando el lance de pares.")
            inicializar_pares(mesa)
            # Analizar las manos y determinar quién tiene pares
            resultados_pares = analizar_pares(mesa["manos"], mesa_id)
            mesa["pares_confirmados"] = resultados_pares  # Guardar en la mesa para referencia
            total_pares = contar_jugadores_con_pares(resultados_pares)
            mesa["turno_actual"] = encontrar_indice_primer_con_pares( mesa["pares_confirmados"], mesa["mano"])
            # jugadores_con_pares = [jugador for jugador, tiene_pares in mesa["pares_confirmados"].items() if tiene_pares]
            # mesa["turno_actual"] = mesa["jugadores"].index(jugadores_con_pares[0])  # Primer jugador con pares
            # primer_turno_con_pares(mesa)
            turno_actual = mesa["turno_actual"]
            print("[DEBUG] Pares. turno_actual: ", turno_actual, " total jugadores con pares: ", total_pares)
            #turno_actual = encontrar_indice_primer_con_pares(mesa["pares_confirmados"], mesa["mano"])
            contrarias = son_parejas_contrarias(resultados_pares)
            jugadorturno = mesa["jugadores"][turno_actual]
 
             # Emitir a todos los clientes la información de pares y enviar jugador primero con pares para posicionar turno
            print("[DEBUG] Se hace el emit de pares confirmados: ", mesa['pares_confirmados'], " es el turno de :", jugadorturno, " hay ", total_pares, " jugadores con pares.", " contrarias: ", contrarias)
            emit("pares_confirmados", {'resultados_pares': mesa['pares_confirmados'], 'lance': mesa['lance_actual'], 'total_pares': total_pares, 'turno_actual': turno_actual, 'contrarias': contrarias, 'puntos': mesa['puntos']}, to=mesa_id)
            socketio.sleep(1)
            """
            print("[DEBUG] Pongo sleep de 5 segundos para que canten los pares.")   
            # Obtener la hora actual
            hora_actual = datetime.now().time()
            print("La hora actual es:                       ", hora_actual)
            time.sleep(5)
            # Obtener la hora actual
            hora_actual = datetime.now().time()
            print("La hora actual es después de 5 segundos: ", hora_actual)      
            """

            if (total_pares == 0):
                mesa["lance_actual"] = "Juego"
                emit('mensaje_mesa', {'msg': f"Ningún jugador tiene pares.", 'username': mesa['lance_actual']}, to=mesa_id)
            if (total_pares == 1):
                mesa["lance_actual"] = "Juego"
                emit('mensaje_mesa', {'msg': f"Solo hay un jugador con pares.", 'username': mesa['lance_actual']}, to=mesa_id)
            if (total_pares == 2):
                if (contrarias):
                    emit('mensaje_mesa', {'msg': f"Comienza el lance de pares. Es el turno de {jugadorturno}", 'username': mesa['lance_actual']}, to=mesa_id)
                else:
                    mesa["lance_actual"] = "Juego"
                    emit('mensaje_mesa', {'msg': f"Solo una pareja tiene pares.", 'username': 'Docemas'}, to=mesa_id)
            if (total_pares == 3):
                emit('mensaje_mesa', {'msg': f"Comienza el lance de pares. Es el turno de {jugadorturno}", 'username': mesa['lance_actual']}, to=mesa_id)
            if (total_pares == 4):
                emit('mensaje_mesa', {'msg': f"Comienza el lance de pares. Es el turno de {jugadorturno}", 'username': mesa['lance_actual']}, to=mesa_id)


        if mesa["lance_actual"] == "Juego":
            print("[DEBUG] Pasar_a_siguiente_lance: Estado actualizado 11 desde ", mesa['lance_actual'])
            emit('estado_actualizado', mesa, to=mesa_id)     
            emit('bloquear_mesa_botones', mesa['lance_actual'], to=mesa_id)       
            print("[DEBUG] Comenzando el lance de juego.")
            inicializar_juego(mesa)  # Inicializa las variables necesarias para este lance
            #procesar_lance_juego(mesa)
            # Analizar las manos y determinar quién tiene juego
            resultados_juego = analizar_juego(mesa)  
            mesa["estado_juego"] = resultados_juego  # Guardar en la mesa para referencia
            jugadorturno, indiceJuego, cantidadJ = obtener_info_jugador_con_juego(resultados_juego)
            contrariasJ = son_parejas_contrarias_con_juego(resultados_juego)
            primer_turno_con_juego(mesa)
            mesa["turno_actual"] = indiceJuego
            print("[DEBUG] Juego. turno_actual: ", indiceJuego)
            if (cantidadJ == 2):
                if (contrariasJ):
                    emit('mensaje_mesa', {'msg': f"Comienza el lance de juego. Es el turno de {jugadorturno}", 'username': mesa['lance_actual']}, to=mesa_id)
            if (cantidadJ == 3):
                emit('mensaje_mesa', {'msg': f"Comienza el lance de juego. Es el turno de {jugadorturno}", 'username': mesa['lance_actual']}, to=mesa_id)
            if (cantidadJ == 4):
                emit('mensaje_mesa', {'msg': f"Comienza el lance de juego. Es el turno de {jugadorturno}", 'username': mesa['lance_actual']}, to=mesa_id)

            """
            print("[DEBUG] Pongo sleep de 5 segundos para que canten el juego.")
            # Obtener la hora actual
            hora_actual = datetime.now().time()
            print("La hora actual es:                       ", hora_actual)
            time.sleep(5)
            # Obtener la hora actual
            hora_actual = datetime.now().time()
            print("La hora actual es después de 5 segundos: ", hora_actual)   
            """
            # Emitir a todos los clientes la información de juego
            print("[DEBUG] Se hace el emit de juego confirmado: ", mesa['estado_juego'], " jugadorturno: ", jugadorturno, " indicaJuego: ", indiceJuego, " cantidadj: ", cantidadJ, " contrarias: ", contrariasJ)
            emit("juego_confirmado", {'resultado_juego': mesa['estado_juego'], 'total_juego': cantidadJ, 'turno_actual': jugadorturno, 'contrarias': contrariasJ}, to=mesa_id)
            socketio.sleep(3)

        if mesa["lance_actual"] == "Juego":
            if (cantidadJ == 0):
                emit('mensaje_mesa', {'msg': f"Ningún jugador tiene juego. Pasamos al Punto.", 'username': mesa['lance_actual']}, to=mesa_id)
                mesa["lance_actual"] = "Punto"
            elif (cantidadJ == 1):
                emit('mensaje_mesa', {'msg': f"Solo {jugadorturno} tiene juego. Finaliza la ronda.", 'username': mesa['lance_actual']}, to=mesa_id)
                finalizar_ronda(mesa)
            elif (cantidadJ == 2 and not contrariasJ):
                    emit('mensaje_mesa', {'msg': f"Solo una pareja tiene juego. Finaliza la ronda.", 'username': mesa['lance_actual']}, to=mesa_id)
                    finalizar_ronda(mesa)

        if mesa["lance_actual"] == "Punto":           
            jugadorturno, indiceJuego, cantidadJ = obtener_info_jugador_con_juego(mesa["estado_juego"])
            print("[DEBUG] Comenzando el lance de Punto. cantidadJ: ", cantidadJ)
            if (cantidadJ == 0):
                    mesa["turno_actual"] = mesa["mano"]
                    jugadorturno = mesa["jugadores"][mesa["turno_actual"]]
                    emit('mensaje_mesa', {'msg': f"Comienza el lance de Punto. Es el turno de {jugadorturno}", 'username': mesa["lance_actual"]}, to=mesa_id)
                    # Emitir a todos los clientes la información de pares y enviar jugador primero con pares para posicionar turno
                    print("[DEBUG] Se hace el emit de Punto. Es el turno de :", jugadorturno)        
            print("[DEBUG] Pasar_a_siguiente_lance: Estado actualizado 12 desde ", mesa['lance_actual'])
            emit('estado_actualizado', mesa, to=mesa_id)
    else:
        finalizar_ronda(mesa)  # Si se completaron todos los lances, finalizar la ronda



def contar_jugadores_con_pares(pares_confirmados):
    return sum(1 for tiene_pares in pares_confirmados.values() if tiene_pares)

def son_parejas_contrarias(pares_confirmados):
    """
    Determina si los jugadores con pares están en parejas contrarias.
    
    pares_confirmados: dict con el formato {nombre_jugador: True/False}
    """
    # Convertir las claves a una lista para mantener el orden
    posiciones = list(pares_confirmados.keys())
    
    # Verificar que haya exactamente 4 jugadores
    if len(posiciones) != 4:
        raise ValueError("pares_confirmados debe contener exactamente 4 jugadores.")
    
    # Determinar las parejas dinámicamente
    pareja1 = {posiciones[0], posiciones[2]}  # Jugador en posición 0 y 2
    pareja2 = {posiciones[1], posiciones[3]}  # Jugador en posición 1 y 3
    
    # Jugadores que tienen pares
    jugadores_con_pares = [jugador for jugador, tiene_pares in pares_confirmados.items() if tiene_pares]
    
    # Comprobación de cantidad
    if len(jugadores_con_pares) != 2:
        return False  # No aplica si no hay exactamente dos jugadores con pares
    
    # Determinar si están en la misma pareja
    jugador1, jugador2 = jugadores_con_pares
    if (jugador1 in pareja1 and jugador2 in pareja1) or (jugador1 in pareja2 and jugador2 in pareja2):
        return False  # Misma pareja
    
    # Si no están en la misma pareja, son parejas contrarias
    return True

def son_parejas_contrarias_con_juego(jugadores):
    """
    Verifica si exactamente dos jugadores tienen 'tiene_juego' a True y si forman parejas cruzadas (A y D, o B y C).

    Args:
        jugadores: Una lista de diccionarios, donde cada diccionario representa un jugador.

    Returns:
        True si exactamente dos jugadores tienen juego y forman parejas cruzadas, False en caso contrario.
    """
    if len(jugadores) != 4:
        return False

    jugadores_con_juego = [i for i, jugador in enumerate(jugadores) if jugador['tiene_juego']]

    if len(jugadores_con_juego) != 2:
        return False

    indice1, indice2 = jugadores_con_juego

    # Comprobamos las combinaciones de parejas opuestas
    if  (indice1 == 0 and indice2 == 1) or (indice1 == 1 and indice2 == 0) or \
        (indice1 == 0 and indice2 == 3) or (indice1 == 3 and indice2 == 0) or \
        (indice1 == 1 and indice2 == 2) or (indice1 == 2 and indice2 == 1) or \
        (indice1 == 2 and indice2 == 3) or (indice1 == 3 and indice2 == 2):
        return True
    else:
        return False

def encontrar_indice_primer_con_pares(pares_confirmados, mano):
    """
    Encuentra el índice del primer jugador con pares comenzando desde el 'mano'.

    Args:
        pares_confirmados (dict): Diccionario ordenado con jugadores y si tienen pares (True o False).
        mano (int): Índice del jugador que es 'mano' en la lista de jugadores.

    Returns:
        int: Índice del primer jugador con pares, o -1 si no se encuentra ninguno.
    """
    jugadores = list(pares_confirmados.keys())  # Extrae la lista de jugadores
    num_jugadores = len(jugadores)

    # Recorremos circularmente desde el mano
    for i in range(num_jugadores):
        indice_actual = (mano + i) % num_jugadores  # Índice circular
        jugador_actual = jugadores[indice_actual]

        if pares_confirmados[jugador_actual]:  # Verifica si tiene pares (True)
            return indice_actual  # Devuelve el índice del jugador

    return -1  # Si ningún jugador tiene pares

def obtener_info_jugador_con_juego(jugadores):
    """
    Busca el primer jugador con 'tiene_juego' a True y cuenta cuántos jugadores lo tienen.

    Args:
        jugadores: Una lista de diccionarios, donde cada diccionario representa un jugador.

    Returns:
        Una tupla que contiene:
            - El nombre del primer jugador con juego (str) o None si ningún jugador tiene juego.
            - El índice del primer jugador con juego (int) o -1 si ningún jugador tiene juego.
            - El número total de jugadores con juego (int).
    """
    jugador_con_juego = None
    indice_jugador_con_juego = -1  # Inicializamos a -1 para indicar que no se ha encontrado
    num_jugadores_con_juego = 0 

    for i, jugador in enumerate(jugadores):   # Usamos enumerate para obtener índice y valor
        print(f"[DEBUG] Revisando jugador {jugador['jugador']}, tiene_juego: {jugador['tiene_juego']}")
        if jugador['tiene_juego']:
            num_jugadores_con_juego += 1
            if jugador_con_juego is None:
                jugador_con_juego = jugador['jugador']
                indice_jugador_con_juego = i  # Guardamos el índice


    return jugador_con_juego, indice_jugador_con_juego, num_jugadores_con_juego

def inicializar_pares(mesa):
    """
    Inicializa el estado para el lance de pares.
    """
    print("[DEBUG] Entra en inicializar pares.")
    mesa["pares_confirmados"] = {jugador: None for jugador in mesa["jugadores"]}
    print("[DEBUG] Estado de pares inicializado:", mesa['pares_confirmados'])

def inicializar_juego(mesa):
    print("[DEBUG] Entra en inicializar juego.")
    mesa["estado_juego"] = []
    mesa["apuesta"][4] = 0  # Inicializar apuestas para el lance de juego

def tiene_pares(turno_actual, mesa):
    """
    Verifica si el jugador actual tiene pares.
    """
    jugador_actual = mesa["jugadores"][turno_actual]
    print(f"[DEBUG] Verificando pares para el jugador: {jugador_actual}")
    # Comprueba en la estructura 'pares_confirmados' si tiene pares
    return mesa["pares_confirmados"].get(jugador_actual, False)


def tiene_juego(turno_actual, mesa):
    """
    Verifica si el jugador actual tiene juego.
    """
    jugador_actual = mesa["jugadores"][turno_actual]
    print(f"[DEBUG] Verificando juego para el jugador: {jugador_actual}")

    # Busca el estado del jugador en 'estado_juego' y verifica si tiene juego
    for jugador in mesa["estado_juego"]:
        if jugador["jugador"] == jugador_actual:
            return jugador.get("tiene_juego", False)
    
    return False

def primer_turno_con_pares(mesa):
    """
    Devuelve el índice (turno_actual) del primer jugador que tenga pares.
    Debería encontrarlo desde el mano que es desde donde hay que empezar a contar y no lo hace
    """
    for idx, jugador in enumerate(mesa["jugadores"]):
        if mesa["pares_confirmados"].get(jugador, False):
            print(f"[DEBUG] Primer jugador con pares: {jugador} en el turno {idx}")
            return idx
    print("[DEBUG] Ningún jugador tiene pares.")
    return None

def primer_turno_con_juego(mesa):
    """
    Devuelve el índice (turno_actual) del primer jugador que tenga juego.
    Args:
        mesa (dict): Información de la mesa que incluye jugadores y estado del juego.

    Returns:
        int or None: Índice del primer jugador con juego, o None si ninguno tiene juego.
    """
    for idx, estado in enumerate(mesa["estado_juego"]):  # Iterar sobre la lista de estados
        if estado.get("tiene_juego", False):
            print(f"[DEBUG] Primer jugador con juego: {estado['jugador']} en el turno {idx}")
            return idx
    print("[DEBUG] Ningún jugador tiene juego.")
    return None


def calcular_puntos_cartas(mano):
    """
    Calcula los puntos totales de una mano en función de las reglas del lance de Juego o Punto.
    Args:
        mano (list): Lista de cartas del jugador. Cada carta se representa como una cadena (p. ej., '3c', '11o').

    Returns:
        int: Puntos totales de la mano.
    """
    # Definimos los valores de las cartas
    valores_cartas = {
        "1": 1, "2": 1, "3": 10, "4": 4, "5": 5, "6": 6, "7": 7,
        "10": 10, "11": 10, "12": 10  # 10, Sota, Caballo, Rey valen 10
    }

    puntos = 0

    for carta in mano:
        # Extraemos el valor de la carta ignorando el palo (todo menos el último carácter)
        valor = carta[:-1]  # Ignora el último carácter, que es el palo
        puntos += valores_cartas.get(valor, 0)  # Busca el valor en el diccionario; si no lo encuentra, usa 0

    print("[DEBUG] Entra en CALCULAR PUNTOS CARTAS Puntos: ", puntos, " mano: ", mano)

    return puntos


def determinar_ganador(mesa):
    """
    Determina el ganador del lance actual basado en las manos de los jugadores.
    """
    print("[DEBUG] Entra en determinar ganador.")
    lance = mesa["lance_actual"]
    manos = mesa["manos"]  # Diccionario: claves = nombres de jugadores, valores = manos

    if lance == "Juego":
            jugadores_con_juego = [
                jugador["jugador"] for jugador in mesa["estado_juego"] if jugador["tiene_juego"]
            ]
            return max(jugadores_con_juego, key=lambda j: evaluar_juego(manos[j]))


    if lance == "Pares":
        jugadores_con_pares = [
            jugador for jugador, tiene_pares in mesa["pares_confirmados"].items() if tiene_pares
        ]
        if len(jugadores_con_pares) == 1:
            return jugadores_con_pares[0]  # Si solo un jugador tiene pares, es el ganador
        elif len(jugadores_con_pares) > 1:
            return max(jugadores_con_pares, key=lambda j: evaluar_pares(manos[j]))

    # Otros lances (como Grande, Chica, Juego, etc.)
    if lance == "Grande":
        return max(mesa["jugadores"], key=lambda j: evaluar_grande(manos[j]))
    elif lance == "Chica":
        return max(mesa["jugadores"], key=lambda j: evaluar_chica(manos[j]))

    print("Determinar ganador. lance actual: ", mesa['lance_actual'])


def registrar_lance(mesa, ganador, lance, apuesta_actual, estado_apuesta):
    """
    Registra el resultado de un lance para ser contabilizado al final de la ronda.
    Si el lance es "Pares" y solo una pareja tiene pares, asigna los puntos directamente.
    """
    print("[DEBUG] Entra en registrar lance: ", lance)

    mesa_id = mesa['nombre']

    pareja1 = [mesa["jugadores"][0], mesa["jugadores"][2]]  # Primer y tercer jugador
    pareja2 = [mesa["jugadores"][1], mesa["jugadores"][3]]  # Segundo y cuarto jugador

    if "resultados_lances" not in mesa:
        mesa["resultados_lances"] = []

    if apuesta_actual > 0 and mesa["apuesta_anterior"] > 0 and estado_apuesta == 1: # ha habido reenvite y no se ha visto
        amarracos = apuesta_actual - mesa["apuesta_actual"]
    else: 
        amarracos = 1

    if apuesta_actual > 0 and estado_apuesta == 1: # ha habido envite y/o reemvite y no se ha visto
        print("[DEBUG] Entra en registrar lance de {lance}. Jugador Apuesta: ", mesa['jugadorApuesta'], " pareja1: ", pareja1)
        if mesa["jugadorApuesta"] in pareja1:
            # La pareja contraria es pareja1, sumamos punto en el índice 0
            mesa["puntos"][0] += amarracos
            emit('mensaje_mesa', {'msg': f"¡La pareja 1 gana 1 punto a {lance}!", 'username': mesa['lance_actual']}, to=mesa_id)
            if lance == "Grande":
                mesa["grande"][0] += amarracos
            elif lance == "Chica":
                mesa["chica"][0] += amarracos
            elif lance == "Pares":
                mesa["pares"][0] += amarracos
            elif lance == "Juego":
                mesa["juego"][0] += amarracos
            elif lance == "Punto":
                mesa["punto"][0] += amarracos                                
        #elif set(mesa["pareja_contraria"]) == set(pareja2):
        else:
            # La pareja contraria es pareja2, sumamos punto en el índice 0
            mesa["puntos"][1] += amarracos
            emit('mensaje_mesa', {'msg': f"¡La pareja 2 gana 1 punto a {lance}!", 'username': mesa['lance_actual']}, to=mesa_id)
            if lance == "Grande":
                mesa["grande"][1] += amarracos
            elif lance == "Chica":
                mesa["chica"][1] += amarracos
            elif lance == "Pares":
                mesa["pares"][1] += amarracos
            elif lance == "Juego":
                mesa["juego"][1] += amarracos
            elif lance == "Punto":
                mesa["punto"][1] += amarracos  
    
    print("[DEBUG] Entra en registrar lance. Valor de Puntos: ", mesa['puntos'])
    mesa["jugadorApuesta"] = None
    
    mesa["apuesta_anterior"] = 0
    mesa["apuesta_actual"] = 0

    if mesa["puntos"][0] >= mesa['puntos_juego'] or mesa["puntos"][1] >= mesa['puntos_juego']:
        emitir_actualizar_interfaz(mesa)
        verificar_finaliza_juego_partida(mesa)
        return 

    if lance == "Pares" and ganador is None:
        # Determinar qué pareja tiene pares
        jugadores_con_pares = [
            jugador for jugador, tiene_pares in mesa['pares_confirmados'].items() if tiene_pares
        ]
        pares_pareja1 = sum(1 for jugador in jugadores_con_pares if jugador in pareja1)
        pares_pareja2 = sum(1 for jugador in jugadores_con_pares if jugador in pareja2)

        if pares_pareja1 > 0 and pares_pareja2 == 0:
            ganador = pareja1[0]  # Asignar a la pareja 1
        elif pares_pareja2 > 0 and pares_pareja1 == 0:
            ganador = pareja2[0]  # Asignar a la pareja 2

    mesa["resultados_lances"].append({ 
        "lance": lance,
        "ganador": ganador,
        "apuesta": apuesta_actual,  # Amarracos apostados en este lance
        "estado_apuesta": estado_apuesta  # 0 Si la apuesta fue vista 1 si pasaron
    })
    print(f"[DEBUG] Registrar lance: {mesa['resultados_lances']}")

def finalizar_ronda(mesa):
    """
    Procesa los resultados de todos los lances registrados, actualiza el marcador,
    y valida si una pareja ha ganado el juego.
    """
    print("[DEBUG] Entra en finalizar ronda. ")
    
    #emit('bloquear_mesa_botones', mesa["lance_actual"], to=mesa_id)

    if "resultados_lances" not in mesa:
        return

    # El mano correo un turno para la nueva ronda
    #mesa['mano'] = (mesa['mano'] + 1) % len(mesa['jugadores'])
    #print("[DEBUG] Finalizar ronda. mesa['mano']: ", mesa['mano'])

    for resultado in mesa["resultados_lances"]:
        lance = resultado["lance"]
        ganador = resultado["ganador"]
    '''
        # Si el ganador no está definido, determinarlo
        if ganador is None:
    '''

    ganador = determinar_ganador_grande(mesa)
    ganador = determinar_ganador_chica(mesa)
    ganador = determinar_ganador_pares(mesa)
    if ha_habido_juego(mesa):
        ganador = determinar_ganador_juego(mesa)
    else:
        ganador = determinar_ganador_punto(mesa)

    # Actualizar el resultado del lance con el ganador determinado
    #time.sleep(1)
    
    # Emitir actualizar_interfaz_ronda
    emitir_actualizar_interfaz(mesa)

    verificar_finaliza_juego_partida(mesa)


def emitir_actualizar_interfaz(mesa):
    
    mesa_id = mesa['nombre']
    # Recuperamos la apuesta del lance
    indice_apuesta = mesa['lances'].index(mesa["lance_actual"])
    apuesta = mesa["apuesta"][indice_apuesta]
    mesa["mano"] = (mesa["mano"] + 1) % len(mesa["jugadores"])

   # Emitir actualizar_interfaz_rondao
    emit("actualizar_interfaz_ronda", {
        "turno_actual": mesa['mano'],        
        "jugadorAnterior": mesa['jugadorAnterior'],  
        "puntos": mesa['puntos'],
        "juegos": mesa['juegos'],        
        "grande": mesa['grande'],
        "chica": mesa['chica'],        
        "pares": mesa['pares'],
        "juego": mesa['juego'],  
        "punto": mesa['punto'],
        "manos": mesa['manos'],
        "juegos_vaca": mesa['juegos_vaca'],
        "puntos_juego": mesa['puntos_juego'],
        "apuesta": apuesta
    }, to=mesa_id)

def verificar_finaliza_juego_partida(mesa):

    print("[DEBUG] Ronda finalizada. Estado actualizado enviado a los clientes. Mesa:", mesa)

    mesa_id = mesa['nombre']

    # Validar si alguna pareja supera el valor de puntos_juego
    for equipo, puntos in enumerate(mesa["puntos"]):
        if puntos >= mesa['puntos_juego']:
            mesa["juegos"][equipo] += 1  
            mesa["puntos"] = [0,0]  
            emit('mensaje_mesa', {'msg': f"¡La pareja {equipo + 1} ha ganado el juego con {puntos} puntos!", 'username': mesa['lance_actual']}, to=mesa_id)
            print(f"[DEBUG] El juego ha terminado. Ganadores: Pareja {equipo + 1}")

    # Validar si alguna pareja supera el valor de la variable global juegos_vaca
    for equipo, juegos in enumerate(mesa["juegos"]):
        if juegos >= mesa['juegos_vaca']:
            mesa["juegos"] = [0,0]  
            mesa["puntos"] = [0,0]  
            emit('mensaje_mesa', {'msg': f"¡La pareja {equipo + 1} ha ganado la partida. Gana los {juegos} juegos!", 'username': 'Final'}, to=mesa_id)
            print(f"[DEBUG] La partida ha terminado. Ganadores: Pareja {equipo + 1}")

    inicializar_mesa(mesa, mesa_id)


def inicializar_mesa(mesa, mesa_id):
    # Limpiar los resultados de la ronda anterior para preparar la nueva
    print("[DEBUG] verificar_finaliza_juego_partida. mesa['mano']: ", mesa['mano'])
    mesa['estado_partida'] = "Repartir"
    mesa["lance_actual"] == "Grande"
    mesa["turno_actual"] = mesa["mano"]
    mesa["musContador"] = 0
    mesa["resultados_lances"] = []
    mesa["accion"] = ""
    mesa["acciones"] = [None, None, None, None, None]
    mesa["apuesta"] = [0, 0, 0, 0, 0]
    mesa["apuesta_actual"] = 0
    mesa["apuesta_anterior"] = 0    
    mesa['baraja'] = crear_baraja()
    random.shuffle(mesa['baraja'])
    mesa["descartes"] = []
    mesa['manos'] = {jugador: [] for jugador in mesa['jugadores']}
    mesa["grande"] = [0,0]
    mesa["chica"] = [0,0]
    mesa["pares"] = [0,0]    
    mesa["juego"] = [0,0]    
    mesa["punto"] = [0,0]    
    tables[mesa_id] = mesa  # Guardar cambios
    print(f"Mesa {mesa_id} reiniciada para una nueva ronda.")


def ha_habido_juego(mesa):
    # Iteramos sobre la lista estado_juego para verificar si alguien tiene juego
    for jugador in mesa['estado_juego']:
        if jugador['tiene_juego'] or jugador['puntos'] >= 31:
            return True
    return False

def determinar_ganador_grande(mesa):
    """
    Determina el ganador del lance Grande.
    Se compara carta a carta en orden descendente, y el jugador con las cartas más altas gana.
    En caso de empate, gana el jugador que es mano.
    """
    print("[DEBUG] Entra en determinar ganador grande.")
 
    manos = mesa["manos"]
    jugadores = mesa["jugadores"]

    # Mapa de valores de las cartas para el lance Grande
    mapa_valores = {
        "1": 1, "2": 1, "3": 12, "4": 4, "5": 5, "6": 6, "7": 7,
        "10": 10, "11": 11, "12": 12  # Sota, Caballo, Rey
    }

    # Configuración de las parejas
    parejas = {
        jugadores[0]: 0,  # Pareja 1
        jugadores[2]: 0,  # Pareja 1
        jugadores[1]: 1,  # Pareja 2
        jugadores[3]: 1   # Pareja 2
    }

    # Transformar las manos a listas de valores ordenadas de mayor a menor
    manos_ordenadas = {
        jugador: sorted([mapa_valores[carta[:-1]] for carta in mano], reverse=True)
        for jugador, mano in manos.items()
    }

    print(f"[DEBUG] Manos ordenadas para Grande: {manos_ordenadas}")

    # Resolver ganador con prioridad al jugador mano
    mano_index = mesa["mano"]  # Índice del jugador que es mano
    jugadores_ordenados = jugadores[mano_index:] + jugadores[:mano_index]  # Orden desde el mano

    ganador = max(
        jugadores_ordenados,
        key=lambda j: (
            manos_ordenadas[j],  # Prioridad 1: Mano con mayor valor
            -jugadores_ordenados.index(j)  # Prioridad 2: Mano en caso de empate
        )
    )

    print(f"[DEBUG] Ganador del lance Grande: {ganador} con la mano {manos_ordenadas[ganador]}")

    # Determinar el equipo ganador usando las parejas
    equipo = parejas[ganador]

    if mesa["apuesta"][0] >= mesa['puntos_juego']:  # Se valida el ganador si hay Órdago
        mesa["puntos"][equipo] += mesa['puntos_juego']
        mesa["grande"][equipo] += mesa['puntos_juego']
        # Emitir actualizar_interfaz_ronda
        emitir_actualizar_interfaz(mesa)
        verificar_finaliza_juego_partida(mesa)
        return 
   
    # Caso 1: Todos pasan. Se asigna el punto de la grande en paso a la pareja ganadora
    if mesa["acciones"][0] == "Paso" and mesa["apuesta"][0] == 0:
        mesa["puntos"][equipo] += 1
        mesa["grande"][equipo] += 1
        print(f"[DEBUG] Grande: Todos pasaron. Punto sumado al equipo {equipo} ganado en paso.")

    # Caso 2: Nadie vio la apuesta. Se está tratando en tratar_lance en caliente

    # Caso 3: La apuesta fue vista. Se suma la apuesta + el punto de grande a la pareja ganadora 
    elif mesa["acciones"][0] in ["Veo"]:
        # Sumar los puntos apostados al equipo ganador
        puntos_apuesta = mesa["apuesta"][0]  # Recuperar el valor de la apuesta y lo suma al ganador
        mesa["puntos"][equipo] += puntos_apuesta
        mesa["grande"][equipo] += puntos_apuesta        
        print(f"[DEBUG] Grande: Apuesta vista. {puntos_apuesta} puntos sumados al equipo {equipo}.")

    return ganador

def determinar_ganador_chica(mesa):
    """
    Determina el ganador del lance Chica.
    Se compara carta a carta en orden ascendente, y el jugador con las cartas más pequeñas gana.
    En caso de empate, gana el jugador que es mano.
    """

    print("[DEBUG] Entra en determinar ganador chica.")

    manos = mesa["manos"]
    jugadores = mesa["jugadores"]

    # Mapa de valores de las cartas para el lance Chica
    mapa_valores = {
        "1": 1, "2": 1, "3": 12, "4": 4, "5": 5, "6": 6, "7": 7,
        "10": 10, "11": 11, "12": 12  # Sota, Caballo, Rey
    }

    # Configuración de las parejas
    parejas = {
        jugadores[0]: 0,  # Pareja 1
        jugadores[2]: 0,  # Pareja 1
        jugadores[1]: 1,  # Pareja 2
        jugadores[3]: 1   # Pareja 2
    }

    # Transformar las manos a listas de valores ordenadas de menor a mayor
    manos_ordenadas = {
        jugador: sorted([mapa_valores[carta[:-1]] for carta in mano])
        for jugador, mano in manos.items()
    }

    print(f"[DEBUG] Manos ordenadas para Chica: {manos_ordenadas}")

    # Resolver ganador con prioridad al jugador mano
    mano_index = mesa["mano"]  # Índice del jugador que es mano
    jugadores_ordenados = jugadores[mano_index:] + jugadores[:mano_index]  # Orden desde el mano

    ganador = max(
        jugadores_ordenados,
        key=lambda j: (
            [-v for v in manos_ordenadas[j]],  # Prioridad 1: Mano con menor valor (invertir para max)
            -jugadores_ordenados.index(j)  # Prioridad 2: Mano en caso de empate
        )
    )

    print(f"[DEBUG] Ganador del lance Chica: {ganador} con la mano {manos_ordenadas[ganador]}")

    # Determinar el equipo ganador usando las parejas
    equipo = parejas[ganador]

    if mesa["apuesta"][1] >= mesa['puntos_juego']:  # Se valida el ganador si hay Órdago
        mesa["puntos"][equipo] += mesa['puntos_juego']
        mesa["grande"][equipo] += mesa['puntos_juego']
        # Emitir actualizar_interfaz_ronda
        emitir_actualizar_interfaz(mesa)        
        verificar_finaliza_juego_partida(mesa)
        return 

    # Caso 1: Todos pasan. Se asigna el punto de la chica en paso a la pareja ganadora
    if mesa["acciones"][1] == "Paso" and mesa["apuesta"][1] == 0:
        mesa["puntos"][equipo] += 1
        mesa["chica"][equipo] += 1
        print(f"[DEBUG] Chica: Todos pasaron. Punto sumado en paso al equipo {equipo}.")

    # Caso 2: Nadie vio la apuesta. se gestiona en tratar_lance

    # Caso 3: La apuesta fue vista. Se suma la apuesta + el punto de chica a la pareja ganadora 
    elif mesa["acciones"][1] in ["Veo"]:
        # Sumar los puntos apostados al equipo ganador
        puntos_apuesta = mesa["apuesta"][1]  # Recuperar el valor de la apuesta y lo suma al ganador
        mesa["puntos"][equipo] += puntos_apuesta
        mesa["grande"][equipo] += puntos_apuesta        
        print(f"[DEBUG] Chica: Apuesta vista: {puntos_apuesta} puntos sumados al equipo {equipo}.")

    return ganador


def determinar_ganador_pares(mesa):
    """
    Determina el ganador del lance Pares.
    Evalúa los pares (duples, medias y parejas) según las reglas.
    En caso de empate en valores, gana el jugador que es mano.
    """
    print("[DEBUG] Entra en determinar ganador de pares.")

    manos = mesa["manos"]
    jugadores = mesa["jugadores"]

    # Mapa de valores de las cartas para pares
    mapa_valores = {
        "1": 1, "2": 1, "3": 12, "4": 4, "5": 5, "6": 6, "7": 7,
        "10": 10, "11": 11, "12": 12  # Sota, Caballo, Rey
    }

    # Configuración de las parejas
    parejas = {
        jugadores[0]: 0,  # Pareja 1
        jugadores[2]: 0,  # Pareja 1
        jugadores[1]: 1,  # Pareja 2
        jugadores[3]: 1   # Pareja 2
    }

    # Clasificar los pares de cada jugador
    clasificacion_pares = {}
    for jugador, mano in manos.items():
        valores = [mapa_valores[carta[:-1]] for carta in mano]
        conteo = {v: valores.count(v) for v in set(valores)}

        # Determinar las combinaciones
        parejas_encontradas = [v for v, c in conteo.items() if c == 2]  # Valores con exactamente 2 cartas
        trios_encontrados = [v for v, c in conteo.items() if c == 3]    # Valores con exactamente 3 cartas
        cuartetos = [v for v, c in conteo.items() if c == 4]            # Valores con exactamente 4 cartas

        # Determinar el tipo de combinación más alta
        if len(cuartetos) >= 1 or len(parejas_encontradas) >= 2:
            combinacion = "duples"
            puntos = 3
            valor_principal = sorted(cuartetos + parejas_encontradas, reverse=True)[:2]
        elif len(trios_encontrados) >= 1:
            combinacion = "medias"
            puntos = 2
            valor_principal = [max(trios_encontrados)]
        elif len(parejas_encontradas) == 1:
            combinacion = "pareja"
            puntos = 1
            valor_principal = [parejas_encontradas[0]]
        else:
            combinacion = "sin_pares"
            puntos = 0
            valor_principal = []

        # Clasificación ajustada
        clasificacion_pares[jugador] = {
            "puntos": puntos,
            "valores": valor_principal,
            "combinacion": combinacion,
            "duples": 1 if combinacion == "duples" else 0,
            "trios": 1 if combinacion == "medias" else 0,
            "parejas": 1 if combinacion == "pareja" else 0,
        }

    print(f"[DEBUG] Clasificación de pares: {clasificacion_pares}")

    # Resolver ganador
    mano_index = mesa["mano"]
    jugadores_ordenados = jugadores[mano_index:] + jugadores[:mano_index]

    ganador = max(
        jugadores,
        key=lambda j: (
            clasificacion_pares[j]["puntos"],
            clasificacion_pares[j]["valores"],
            -jugadores_ordenados.index(j)
        )
    )

    print(f"[DEBUG] determinar_ganador_pares Parejas: {parejas}")
    print(f"[DEBUG] determinar_ganador_pares Ganador: {ganador}")

    # Determinar el equipo del ganador y su compañero
    equipo = parejas[ganador]
    compañero = [j for j in jugadores if parejas[j] == equipo and j != ganador][0]

    if mesa["apuesta"][2] >= mesa['puntos_juego']:  # Se valida el ganador si hay Órdago
        mesa["puntos"][equipo] += mesa['puntos_juego']
        mesa["grande"][equipo] += mesa['puntos_juego']
        # Emitir actualizar_interfaz_ronda
        emitir_actualizar_interfaz(mesa)
        verificar_finaliza_juego_partida(mesa)
        return

    # Caseo 1: Calcular los puntos de la pareja ganadora
    puntos_ganados = (
        clasificacion_pares[ganador]["duples"] * 3 +
        clasificacion_pares[ganador]["trios"] * 2 +
        clasificacion_pares[ganador]["parejas"] * 1
    ) + (
        clasificacion_pares[compañero]["duples"] * 3 +
        clasificacion_pares[compañero]["trios"] * 2 +
        clasificacion_pares[compañero]["parejas"] * 1
    )

    print(f"[DEBUG] Puntos adicionales del ganador ({ganador}): {clasificacion_pares[ganador]}")
    print(f"[DEBUG] Puntos adicionales del compañero ({compañero}): {clasificacion_pares[compañero]}")

    # Actualizar los puntos en la mesa
    mesa["puntos"][equipo] += puntos_ganados
    mesa["pares"][equipo] += puntos_ganados
    print(f"[DEBUG] Determinar ganador Pares. Puntos por pares: {puntos_ganados} puntos sumados al equipo {equipo}.")

    # Caso 2: Nadie vio la apuesta. se gestiona en tratar_lance

    # Caso 3: La apuesta fue vista. Se suma la apuesta a la pareja ganadora 
    if mesa["acciones"][2] in ["Veo"]:
        # Sumar los puntos apostados al equipo ganador
        puntos_apuesta = mesa["apuesta"][2] 
        mesa["puntos"][equipo] += puntos_apuesta
        mesa["pares"][equipo] += puntos_apuesta        
        print(f"[DEBUG] Determinar ganador Pares. Apuesta vista: {puntos_apuesta} puntos sumados al equipo {equipo}.")

    print(f"[DEBUG] Ganador del lance Pares: {ganador}")
    print(f"[DEBUG] Puntos acumulados en la mesa: {mesa['puntos']}")

    return ganador

def determinar_ganador_juego(mesa):
    """
    Determina el ganador del lance Juego y actualiza los puntos.
    También suma los puntos del compañero si tiene juego válido.
    """
    print("[DEBUG] Entra en determinar ganador de juego.")

    manos = mesa["manos"]
    jugadores = mesa["jugadores"]

    # Mapa de valores de las cartas para el lance Juego
    mapa_valores = {
        "1": 1, "2": 1, "3": 10, "4": 4, "5": 5, "6": 6, "7": 7,
        "10": 10, "11": 10, "12": 10  # Sota, Caballo, Rey
    }

    # Configuración de las parejas
    parejas = {
        jugadores[0]: 0,  # Pareja 1
        jugadores[2]: 0,  # Pareja 1
        jugadores[1]: 1,  # Pareja 2
        jugadores[3]: 1   # Pareja 2
    }

    # Calcular puntos de cada jugador
    puntos_jugadores = {
        jugador: sum(mapa_valores[carta[:-1]] for carta in mano)
        for jugador, mano in manos.items()
    }

    print(f"[DEBUG] Puntos de los jugadores en Juego: {puntos_jugadores}")

    # Filtrar solo jugadores con juego
    jugadores_con_juego = [
        jugador for jugador in jugadores
        if puntos_jugadores[jugador] in {31, 40, 32, 39, 38, 37, 36, 35, 34, 33}
    ]

    if not jugadores_con_juego:
        print("[DEBUG] Ningún jugador tiene juego. No se asignan puntos.")
        return None

    # Orden desde el mano
    mano_index = mesa["mano"]
    jugadores_ordenados = jugadores[mano_index:] + jugadores[:mano_index]

    # Resolver ganador: Priorizar "31", luego puntuaciones mayores, y desempatar por "mano"
    ganador = max(
        jugadores_con_juego,
        key=lambda j: (
            puntos_jugadores[j] == 31,  # Priorizar si tiene 31 (True > False)
            puntos_jugadores[j],        # Luego comparar la puntuación directamente
            -jugadores_ordenados.index(j)  # Priorizar al mano en caso de empate
        )
    )

    puntos_ganador = puntos_jugadores[ganador]
    print(f"[DEBUG] Ganador provisional del Juego: {ganador} con {puntos_ganador} puntos.")

    # Determinar el equipo del ganador
    equipo = parejas[ganador]

    if mesa["apuesta"][3] >= mesa['puntos_juego']:  # Se valida el ganador si hay Órdago
        mesa["puntos"][equipo] += mesa['puntos_juego']
        mesa["grande"][equipo] += mesa['puntos_juego']
        # Emitir actualizar_interfaz_ronda
        emitir_actualizar_interfaz(mesa)
        verificar_finaliza_juego_partida(mesa)
        return 

    # Identificar al compañero del ganador
    compañero = [j for j in jugadores if parejas[j] == equipo and j != ganador][0]

    # Caso 1: Calcular puntos del ganador
    puntos_ganados = 3 if puntos_ganador == 31 else 2

    # Calcular puntos del compañero si tiene juego válido
    if puntos_jugadores[compañero] in {31, 40, 32, 39, 38, 37, 36, 35, 34, 33}:
        if puntos_jugadores[compañero] == 31:
            puntos_ganados += 3
        elif puntos_jugadores[compañero] > 31:
            puntos_ganados += 2

    print(f"[DEBUG] Puntos ganados por el equipo {equipo}: {puntos_ganados} (incluyendo compañero).")

    # Sumar puntos al equipo ganador
    mesa["puntos"][equipo] += puntos_ganados
    mesa["juego"][equipo] += puntos_ganados

    # Caso 2: Nadie vio la apuesta. se gestiona en tratar_lance

    # Caso 3: La apuesta fue vista. Se suma la apuesta a la pareja ganadora 
    if mesa["acciones"][3] in ["Veo"]:
        puntos_apuesta = mesa["apuesta"][3] 
        mesa["puntos"][equipo] += puntos_apuesta
        mesa["juego"][equipo] += puntos_apuesta        
        print(f"[DEBUG] Determinar ganador Juego. Apuesta vista: {puntos_apuesta} puntos sumados al equipo {equipo}.")

    print(f"[DEBUG] Ganador del lance Juego: {ganador} con {puntos_ganador} puntos.")
    print(f"[DEBUG] Puntos acumulados en la mesa: {mesa['puntos']}")

    return ganador

def determinar_ganador_punto(mesa):
    """
    Determina el ganador del lance Punto y actualiza los puntos.
    Evalúa las puntuaciones y calcula los puntos según las reglas:
    - Gana quien más se acerque a 30 sin pasarse.
    - Si nadie ve una apuesta, se aplica "miedo" (un punto adicional al final de la ronda).
    - En caso de empate en puntuaciones, gana el jugador que es mano.
    """

    print("[DEBUG] Entra en determinar ganador de punto.")

    manos = mesa["manos"]  # Diccionario: {jugador: mano}
    jugadores = mesa["jugadores"]  # Lista de jugadores en orden

    # Validar que manos es un diccionario
    if not isinstance(manos, dict):
        raise TypeError(f"mesa['manos'] debe ser un diccionario, pero es {type(manos)}")

    # Mapa de valores de las cartas (igual que en Juego)
    mapa_valores = {
        "1": 1, "2": 1, "3": 10, "4": 4, "5": 5, "6": 6, "7": 7,
        "10": 10, "11": 10, "12": 10  # Sota, Caballo, Rey
    }

    # Calcular los puntos de cada jugador
    puntajes = {
        jugador: min(sum(mapa_valores[carta[:-1]] for carta in mano), 30)  # Limitar puntuación a 30
        for jugador, mano in manos.items()
    }

    print(f"[DEBUG] Puntos de los jugadores en Punto: {puntajes}")

    # Resolver ganador con prioridad al jugador mano
    mano_index = mesa["mano"]  # Índice del jugador que es mano
    jugadores_ordenados = jugadores[mano_index:] + jugadores[:mano_index]  # Orden desde el mano

    ganador = max(
        jugadores_ordenados,
        key=lambda j: (
            puntajes[j],  # Prioridad 1: Más cerca de 30 sin pasarse
            -jugadores_ordenados.index(j)  # Prioridad 2: Mano en caso de empate
        )
    )

    # Determinar la pareja del ganador mediante un diccionario
    parejas = {
        jugadores[0]: 0,  # Pareja 1
        jugadores[2]: 0,  # Pareja 1
        jugadores[1]: 1,  # Pareja 2
        jugadores[3]: 1   # Pareja 2
    }
    equipo = parejas[ganador]

    if mesa["apuesta"][4] >= mesa['puntos_juego']:  # Se valida el ganador si hay Órdago
        mesa["puntos"][equipo] += mesa['puntos_juego']
        mesa["grande"][equipo] += mesa['puntos_juego']
        # Emitir actualizar_interfaz_ronda
        emitir_actualizar_interfaz(mesa)
        verificar_finaliza_juego_partida(mesa)
        return 

    # Caso 1: Todos pasan. Se asigna el punto del Punto en paso a la pareja ganadora
    if mesa["acciones"][4] == "Paso" and mesa["apuesta"][4] == 0:
        mesa["puntos"][equipo] += 1
        mesa["punto"][equipo] += 1
        print(f"[DEBUG] Punto: Todos pasaron. Punto sumado en paso al equipo {equipo}.")
    
    # Caso 2: Nadie vio la apuesta. se gestiona el punto del miedo en tratar_lance

    # Caso 3: La apuesta fue vista. Se suma la apuesta a la pareja ganadora 
    if mesa["acciones"][4] in ["Veo"]:
        puntos_apuesta = mesa["apuesta"][4] 
        mesa["puntos"][equipo] += puntos_apuesta
        mesa["punto"][equipo] += puntos_apuesta        
        print(f"[DEBUG] Determinar ganador Punto. Apuesta vista: {puntos_apuesta} puntos sumados al equipo {equipo}.")

    print(f"[DEBUG] Ganador del lance Punto: {ganador} con {puntajes[ganador]} puntos.")
    print(f"[DEBUG] Punto. Equipo {equipo} ahora tiene {mesa['puntos']} puntos acumulados.")

    return ganador

def evaluar_grande(mano):
    """
    Evalúa el valor para el lance de 'grande'.
    """
    print("[DEBUG] Entra en evaluar grande.")
    # Diccionario para convertir valores de cartas (tres como rey, dos como as)
    mapa_valores = {
        "1": 1, "2": 1, "3": 12, "4": 4, "5": 5, "6": 6, "7": 7, "10": 10, "11": 11, "12": 12
    }
    valores = [mapa_valores[carta[:-1]] for carta in mano]
    print("evaluar_grande. mano: ", mano, " valor máximo: ", max(valores))
    return max(valores)

def evaluar_chica(mano):
    """
    Evalúa el valor para el lance de 'chica'.
    """
    print("[DEBUG] Entra en evaluar chica.")
    # Diccionario para convertir valores de cartas (tres como rey, dos como as)
    mapa_valores = {
        "1": 1, "2": 1, "3": 12, "4": 4, "5": 5, "6": 6, "7": 7, "10": 10, "11": 11, "12": 12
    }
    valores = [mapa_valores[carta[:-1]] for carta in mano]
    print("evaluar_chica. mano: ", mano, " valor mínimo: ", min(valores))
    return min(valores)

def evaluar_pares(mano):
    """
    Evalúa el valor para el lance de 'pares'.
    """
    print("[DEBUG] Entra en evaluar pares.")
    # Diccionario para convertir valores de cartas
    mapa_valores = {
        "1": 1, "2": 1, "3": 12, "4": 4, "5": 5, "6": 6, "7": 7, "10": 10, "11": 11, "12": 12
    }
    valores = [mapa_valores[carta[:-1]] for carta in mano]
    
    # Contar pares, considerando el tres como rey y el dos como as
    pares = [v for v in valores if valores.count(v) > 1]
    print("evaluar_pares. mano: ", mano, " pares: ", pares, " suma pares: ", sum(pares))
    return sum(pares) if pares else 0

def evaluar_juego(mano):
    """
    Evalúa el valor para el lance de 'juego'.
    """
    print("[DEBUG] Entra en evaluar juego.")        

    # Diccionario para convertir valores de cartas (figuras, treses y sietes cuentan como 10)
    mapa_valores = {
        "1": 1, "2": 1, "3": 10, "4": 4, "5": 5, "6": 6, "7": 7, "10": 10, "11": 10, "12": 10
    }
    valores = [mapa_valores[carta[:-1]] for carta in mano]
    suma = sum(valores)
    print("evaluar_juego. mano: ", mano, " suma: ", suma)
    
    if suma == 31:
        return 100  # Prioridad más alta
    elif suma == 32:
        return 90
    elif 37 <= suma <= 40:
        return suma
    return 0

def analizar_pares(manos, mesa_id):
    """
    Analiza las manos de los jugadores para determinar si tienen pares.
    """
    print("[DEBUG] Entra en analizar pares.")

    mapa_valores = {
        "1": 1, "2": 1, "3": 12, "4": 4, "5": 5, "6": 6, "7": 7, "10": 10, "11": 11, "12": 12
    }
    resultados = {}

    for jugador, mano in manos.items():
        valores = [mapa_valores[carta[:-1]] for carta in mano]
        pares = [v for v in set(valores) if valores.count(v) > 1]
        resultados[jugador] = len(pares) > 0  # True si hay pares, False si no
        print(f"[DEBUG] Jugador: {jugador}, Mano: {mano}, Tiene pares: {resultados[jugador]}")
        if (resultados[jugador]):
            emit('mensaje_mesa', {'msg': f"{jugador} tiene pares.", 'username': 'Pares'}, to=mesa_id)
        else:
            emit('mensaje_mesa', {'msg': f"{jugador} NO tiene pares.", 'username': 'Pares'}, to=mesa_id)
    
    return resultados

def evaluar_condiciones_pares(mesa):
    """
    Evalúa las condiciones especiales para el lance de pares.
    Retorna True si se debe pasar al siguiente lance sin jugar.
    """
    print("[DEBUG] Entra en evaluar condiciones pares.")

    jugadores_con_pares = [
        jugador for jugador, tiene_pares in mesa["pares_confirmados"].items() if tiene_pares
    ]
    if not jugadores_con_pares:
        print("[DEBUG] Ningún jugador tiene pares. Pasando al siguiente lance.")
       # emit('mensaje_mesa', {'msg': f"Ningún jugador tiene pares. Pasamos al juego.", 'username': 'Docemas'}, broadcast=True)
        return
        #return True  # Nadie tiene pares

	# Dividir jugadores en parejas de acuerdo con la formación del mus
    pareja1 = [mesa["jugadores"][0], mesa["jugadores"][2]]  # Primer y tercer jugador
    pareja2 = [mesa["jugadores"][1], mesa["jugadores"][3]]  # Segundo y cuarto jugador

    # Contar jugadores con pares por pareja
    pares_pareja1 = sum(1 for jugador in jugadores_con_pares if jugador in pareja1)
    pares_pareja2 = sum(1 for jugador in jugadores_con_pares if jugador in pareja2)

    if pares_pareja1 > 0 and pares_pareja2 == 0:
        print("[DEBUG] Solo la pareja 1 tiene pares. Finalizando el lance.")
       # emit('mensaje_mesa', {'msg': f"Solo la pareja 1 tiene pares. Pasamos al juego.", 'username': 'Docemas'}, broadcast=True)
        registrar_lance(mesa, pareja1[0], "Pares", mesa["apuesta"][3], 0)
        #return True

    elif pares_pareja2 > 0 and pares_pareja1 == 0:
        print("[DEBUG] Solo la pareja 2 tiene pares. Finalizando el lance.")
        #emit('mensaje_mesa', {'msg': f"Solo la pareja 2 tiene pares. Pasamos al juego.", 'username': 'Docemas'}, broadcast=True)
        # registrar_lance(mesa, None, "Pares", Apusta o deje, 0-Cobrada o 1- pte ver ganador)  # Registrar el resultado para la pareja con pares
        registrar_lance(mesa, pareja2[0], "Pares", mesa["apuesta"][3], 0)
       # return True

   # return False  # Continuar con el lance de pares

def analizar_juego(mesa):
    print("[DEBUG] Entra en analizar juego.")
    manos = mesa["manos"]
    resultados = []
    for jugador, mano in manos.items():
        puntos = calcular_puntos_cartas(mano)  # Suma los puntos de las cartas del jugador
        tiene_juego = puntos >= 31
        resultados.append({"jugador": jugador, "tiene_juego": tiene_juego, "puntos": puntos})
    print("[DEBUG] Entra en analizar juego. Resultados: ", resultados)      
    mesa["estado_juego"] = resultados
    return resultados


def procesar_lance_juego(mesa):

    print("[DEBUG] Entra en procesar lance juego.")

    jugadores = mesa["jugadores"]
    estado_juego = {}

    for jugador in jugadores:
        mano = mesa["manos"].get(jugador)  # Asegúrate de que las manos existen
        if not mano:
            raise ValueError(f"No se encontró una mano para el jugador {jugador}")

        puntos = calcular_puntos_cartas(mano)
        tiene_juego = puntos >= 31
        estado_juego.append({"jugador": jugador, "tiene_juego": tiene_juego, "puntos": puntos})

    mesa["estado_juego"] = estado_juego

    # Si ninguno tiene juego
    if all(not j["tiene_juego"] for j in estado_juego):
        print("[DEBUG] Ningún jugador tiene juego. Cambiando a Punto.")

#####################################################################
# Función que devuelve una respuesta del bot cuando el turno es suyo
#####################################################################

    #print(decision_mus_o_corto(mesa))
    #print(respuesta_bot(mesa))

import random

def decision_mus_o_corto(mesa):
    def evaluar_mano():
        mano_bot = mesa['manos'][mesa['jugadores'][mesa['turno_actual']]]
        cartas = [int(carta[:-1]) for carta in mano_bot]
        return sorted(cartas, reverse=True)

    mano_bot = evaluar_mano()
    juego = sum(mano_bot) in [31, 32, 40]
    pares = len(set(mano_bot)) < len(mano_bot)
    medias_duples = any(mano_bot.count(carta) == 2 for carta in mano_bot)
    
    if mano_bot.count(12) >= 2 and not (juego or pares or medias_duples):
        return 'Mus'
    else:
        return 'Corto'

def respuesta_bot(mesa):
    estadobot = None

    def modo_juego():
        nonlocal estadobot
        puntos_contrarios = mesa['puntos'][1] if mesa['jugadores'][0] in mesa['pareja_contraria'] else mesa['puntos'][0]
        if 1 <= puntos_contrarios <= 30:
            estadobot = 'conservador' if random.random() > 0.1 else 'agresivo'
        else:
            estadobot = 'agresivo'
        if puntos_contrarios >= 37:
            estadobot = 'agresivo'

    def evaluar_mano():
        mano_bot = mesa['manos'][mesa['jugadores'][mesa['turno_actual']]]
        cartas = [int(carta[:-1]) for carta in mano_bot]
        return sorted(cartas, reverse=True)

    def decision_estandar():
        lance_actual = mesa['lance_actual']
        acciones = mesa['acciones']
        if acciones[mesa['lances'].index(lance_actual)] == 'Paso':
            if lance_actual == 'Grande' and evaluar_mano().count(12) >= 2:
                return 'Envido'
            elif lance_actual == 'Chica' and evaluar_mano().count(1) >= 2:
                return 'Envido'
            elif lance_actual == 'Pares' and len(set(evaluar_mano())) < len(mesa['manos'][mesa['jugadores'][mesa['turno_actual']]]):
                return 'Envido'
            elif lance_actual == 'Juego' and sum(evaluar_mano()) == 31:
                return 'Subo 5' if mesa['turno_actual'] == mesa['mano'] else 'Envido'
            elif lance_actual == 'Punto' and sum(evaluar_mano()) in [29, 30]:
                return 'Subo 5' if mesa['turno_actual'] == mesa['mano'] else 'Envido'
        return 'Paso'

    def decision_con_apuesta():
        if mesa['accion'] == 'Órdago' or mesa['apuesta_actual'] > 12:
            if mesa['lance_actual'] == 'Grande' and (evaluar_mano().count(12) >= 3 or (evaluar_mano().count(12) >= 2 and sum(mesa['puntos']) > 30)):
                return 'Veo'
            if mesa['lance_actual'] == 'Chica' and (evaluar_mano().count(1) >= 3 or (evaluar_mano().count(1) >= 2 and sum(mesa['puntos']) > 30)):
                return 'Veo'
        return 'Paso'

    def decision_farol():
        opciones = ['Paso', 'Envido', f'Subo {random.choice([2, 5, 10])}', 'Órdago']
        return random.choice(opciones)

    modo_juego()
    decision = decision_estandar() if mesa['apuesta_actual'] == 0 else decision_con_apuesta()
    
    if estadobot == 'agresivo':
        if 'Subo' in decision:
            nueva_apuesta = int(decision.split()[1]) + random.choice([2, 5])
            decision = f'Subo {nueva_apuesta}'
        elif decision == 'Paso':
            decision = 'Envido'
    
    if random.random() < 0.2:
        return decision_farol()
    
    return decision

##############################################################################################



def debug_manos(mesa):
    if not isinstance(mesa["manos"], dict):
        print("[DEBUG] mesa['manos'] se modificó:")
        print("Contenido actual:", mesa['manos'])
        print("Stack trace:")
        traceback.print_stack()

#########################

if __name__ == '__main__':
    print("🚀 Servidor corriendo en http://localhost:8000")
    socketio.run(app, host='0.0.0.0', port=8000, debug=True)

#if __name__ == '__main__':
#    socketio.run(app, host='0.0.0.0', port=8000)

#if __name__ == '__main__':
#   app.run(host='0.0.0.0', port=8000)

'''
if __name__ == '__main__':
    # Detecta si está en producción o local
    if os.getenv('RENDER') == 'true':
        # Configuración para Render
        socketio.run(app, host='0.0.0.0', port=8000)
    else:
        # Configuración para local
        socketio.run(app, debug=True)
'''
