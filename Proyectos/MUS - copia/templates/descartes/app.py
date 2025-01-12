from flask import Flask, render_template, request, session, redirect, url_for, jsonify, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_session import Session
#from app import create_app 
#from flask import Flask, render_template,request,session,redirect,url_for, flash
from flask_login import LoginManager,login_user, logout_user,login_required
#from flask import session
from datetime import datetime, timedelta
#from Proyectos.MUS.envio_email.enviar_email import Ccorreo
from app.models import db, User
from db.usuarios import *
from db.Conexion import *
from envio_email.enviar_email import Ccorreo
#app = create_app() 
#def create_app():

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
socketio = SocketIO(app, manage_session=False)

#Imprime la Ubicación 
#print("Carpeta de plantillas:", app.template_folder)
#db.init_app(app)
#login_manager.init_app(app)
#login_manager.login_view = "registro"

# Lista para jugadores logados y mesas disponibles
logged_players = []
partidas = {}
tables = {}
table_counter = 1  # Contador global para las mesas
#tables = {"Mesa_1": [None, None, None, None]}
#table_counter = 1  # Contador global para las mesas

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/reglas')
def reglas():
    return render_template('reglas.html')

@app.route('/tutorial')
def tutorial():
    return render_template('tutorial.html')

@app.route('/ranking')
def ranking():
    return render_template('estadisticas.html')

@app.route('/iniciosesion')
def iniciosesion():
    return render_template('identificacion.html')
    
@app.route('/logout')
def logout():
    logout_user()
    return render_template('identificacion.html') 

@app.route('/registrarse')
def registrarse():
    return render_template('registro.html')
    
@app.route('/perfilusuario')
def perfilusuario():
    usuario = session.get('usuario')
    datosusuario=CUsuarios.leerUnUsuario(usuario)
    nombre = datosusuario [0] [1]
    usuariobd = datosusuario [0] [2]
    email = datosusuario [0] [3]
    #passwordbd = datosusuario [0] [4]
    avatar= datosusuario [0] [5]
    print("Avatar seleccionado2:" + avatar + " usuario: " + usuario)
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
        flash('Recuerda rellenar todos los campos')
        return redirect(url_for('perfilusuario'))

    CUsuarios.modificarPerfil(nombre,correo,nombreAvatar,alias)
    return render_template('perfilusuario.html',usuario=alias,nombre=nombre,correo=correo, avatar=nombreAvatar)


@app.route('/listar_avatares')
def listar_avatares():
    import os
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
    print('Usuario: ', usuario, " Avatar: ", avatar)
    return render_template('sala_espera.html',usuario=usuario,avatar=avatar)
    #return render_template('sala_espera.html',usuario=usuario,avatar=nombreAvatar)

@app.route('/entrarajugar')
#@login_required
def entrarajugar():
    if session['usuario']:
        return render_template('entrarajugar.html')
    else:
        flash("Debe identificarse primero para entrar a jugar.")

#@app.route('/mesa_juego')
#@login_required
#def mesa_juego():
#    mesa_id = request.args.get('mesa_id')
#    username = session.get('username')
#    asiento = request.args.get('asiento')
#    return render_template('mesa_juego.html', mesa_id=mesa_id, username=username, asiento=asiento)

@app.route('/mesa_juego/<mesa_id>')
def mesa_juego(mesa_id):
    print("Se a a lanzar mesa_juego. El valor de mesa_id es: ", mesa_id)
    if mesa_id in tables:
        mesa = tables[mesa_id]
        print("Se a a lanzar mesa_juego. El valor de mesa es : ", mesa)
        return render_template('mesa_juego.html', mesa=mesa)
    else:
        return f"No se encontró la mesa con ID {mesa_id}", 404


#Función para guardar el registro:
@app.route('/store',methods=['POST'])
def storage():
    nombre =  request.form['nombre_usuario']   
    alias =  request.form['alias']   
    password =  request.form['password']   
    correo =  request.form['email']  
    avatar_url =  '/img/avatar.png'   

    if nombre=='' or correo == '' or alias=='' or password=='':
        flash('Recuerda rellenar todos los campos')
        return redirect(url_for('registrarse'))

    # Generar el hash de la contraseña
    password_hash = hashlib.sha256(password.encode()).hexdigest()

    now = datetime.now()
    #tiempo=now.strftime("%Y%H%M%S")

    #CUsuarios.insertarUsuario(nombre,alias,correo,password_hash,avatar_url,now)
    #Ccorreo.enviar_email(correo, "123456")
    
    #flash('Registro realizado con éxito. Bienvenido ', alias)
    session['usuario'] = alias
    return render_template('entrarajugar.html',usuario=alias,nombre=nombre)

@app.route('/acceso', methods=['POST'])
def acceso():
    mensaje_error = None  # Inicializamos el mensaje de error en None
    usuario = request.form['username']
    password = request.form['password']
    
    # Simulación de lógica de autenticación
    if not usuario:
        mensaje_error = "Debe teclear el usuario."
    elif not password:  
        mensaje_error = "Debe teclear la password."
    
    datosusuario=CUsuarios.leerUnUsuario(usuario)
    nombre = datosusuario [0] [1]
    usuariobd = datosusuario [0] [2]
    passwordbd = datosusuario [0] [4]
    avatar = datosusuario [0] [5]
    #print("Losdatos recuperados del usuario son:", datosusuario)
    #print ("La clave:", usuariobd)
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    if usuario != usuariobd:
        mensaje_error = "Usuario no existe."
    elif password_hash != passwordbd:
        mensaje_error = "Contraseña incorrecta."
    else:
        mensaje_error = "Datos correctos."
        session['usuario'] = usuario
        session['avatar'] = avatar
        #app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=7)  # Mantener sesión por 7 días
        #login_user(usuario, remember=True)
        return render_template('entrarajugar.html',usuario=usuario,nombre=nombre,avatar=avatar)
        # return render_template('salajuego.html',usuario=usuario)  # Redirige a la sala de espera perfil si es exitoso   

    return render_template('identificacion.html', usuario=usuario,password=password,mensaje_error=mensaje_error)

@socketio.on('join')
def handle_join(data):
    username = data.get('username')
    print('Entra en Join de usuarios. Usuario connet: ', username)
    if username and username not in logged_players:
        logged_players.append(username)
    emit('update_players', logged_players, broadcast=True)  # Envía la lista de usuarios a todos los clientes
    emit('update_screen', tables, broadcast=False) # envía la lista de mesas solo al cliente recien conectado

@socketio.on('connect')
def handle_connect():
    username = session.get('username')
    print('Entra en Connect. Usuario connet: ', username)    
    if username and username not in logged_players:
        logged_players.append(username)
    # Emitir la lista actualizada de jugadores a todos los clientes
    #emit('update_players', logged_players, broadcast=True)
    # Emitir el estado actual de las mesas solo al cliente recién conectado
    #emit('update_screen', tables, broadcast=False) 

@socketio.on('disconnect')
def handle_disconnect():
    username = session.get('username')
    if username in logged_players:
        logged_players.remove(username)
        for table, jugadores in tables.items():
            for i, jugador in enumerate(jugadores):
                if jugador == username:
                    tables[table][i] = None
        emit('update_players', logged_players, broadcast=True)
       # emit('update_tables', tables, broadcast=True)

@socketio.on('chat_message')
def handle_chat_message(data):
    username = data.get('username')
    message = data.get('message')
    emit('chat_message', {'username': username, 'message': message}, broadcast=True)
    
@socketio.on('message')
def handle_message(data):
    print("Mensaje genérico recibido:", data)
    emit('message', data, broadcast=True)

@socketio.on('create_table')
def handle_create_table():
    global table_counter
    table_id = f"Mesa_{table_counter}"
    print("En create_table, la mesa a crear es:", table_id)
    tables[table_id] = {
        "nombre": f"Mesa_{table_counter}",
        "estado": "En espera",
        "jugadores": [None, None, None, None],  # Asientos vacíos
        "avatares": [None, None, None, None]  # Avatares vacíos
    }
   # print('Va a hacer el emit desde create_table: ',  table_id)  
    emit('crear_mesaPY', { 'table_name': table_id, 'nro_table': table_counter }, broadcast=True)
    table_counter += 1

@socketio.on('join_table')
def handle_join_table(data):
    print('Entgra en join_table')
    table_name = data['table_name']
    emit('player_joined', {'username': session['username'], 'table_name': table_name}, broadcast=True)


@socketio.on('entrar_asiento')
def handle_entrar_asiento(data):
    username = data['username']
    table_id = data['table_id']
    asiento = data['asiento']
    avatar = data['avatar']
    print("Asiento en entrar: ", asiento, " Table: ", table_id, " usuario: ", username, " avatar: ", avatar)
    #if table_id in tables and tables[table_id][asiento] is None:
    mesa = tables[table_id]
    if mesa["jugadores"][asiento] is None:
        mesa["jugadores"][asiento] = username
        mesa["avatares"][asiento] = avatar
    print(f"{username} entró en el asiento {asiento} de {table_id} con el avatar {avatar}")
    emit('update_tables', tables, broadcast=True)

@socketio.on('salir_asiento')
def handle_salir_asiento(data):
    username = data['username']
    table_id = data['table_id']
    asiento = data['asiento']
    mesa = tables[table_id]
    if mesa["jugadores"][asiento] == username:
        mesa["jugadores"][asiento] = None
    print("Asiento en salir: ", asiento, "usuario: ", username)
   # if table_id in tables and tables[table_id][asiento] == username:
    #tables[table_id][asiento] = None
    emit('update_tables', tables, broadcast=True)

# Código para entrar a la mesa de juego:
@socketio.on('iniciar_partida')
def iniciar_partida(data):
    #print("Evento iniciar_partida recibido con datos:", data)
    table_id = data['table_id']    
    mesa = tables[table_id]
   # jugadores = data['jugadores']
   # avatares = data['avatares']
    try:
        #print("Partida creada en el servidor. Emitiendo evento 'partida_iniciada'.")
        emit('partida_iniciada', { "mesa_id": table_id, "mesa": mesa }, broadcast=True)
    except Exception as e:
        print(f"Error al iniciar la partida: {e}")

@socketio.on('actualizar_mesa')
def handle_actualizar_mesa(data):
    mesa_id = data['mesa_id']
    if mesa_id in tables:
        emit('mesa_actualizada', tables[mesa_id], broadcast=True)



if __name__ == '__main__':
    socketio.run(app, debug=True)
