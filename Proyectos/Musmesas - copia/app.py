from flask import Flask, render_template, session, request, redirect, url_for
from flask_socketio import SocketIO, emit
from flask_session import Session

app = Flask(__name__)
app.secret_key = 'clave_secreta'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
socketio = SocketIO(app, manage_session=False)

# Mesas con jugadores
mesas = {"mesa_1": [None, None, None, None]}
usuarios_conectados = []

@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('mesa_mus.html', usuario=session['username'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        session['username'] = username
        return redirect(url_for('home'))
    return render_template('login.html')

@socketio.on('connect')
def handle_connect():
    username = session.get('username')
    if username and username not in usuarios_conectados:
        usuarios_conectados.append(username)
    emit('actualizar_jugadores', usuarios_conectados, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    username = session.get('username')
    if username in usuarios_conectados:
        usuarios_conectados.remove(username)
        for mesa, jugadores in mesas.items():
            for i, jugador in enumerate(jugadores):
                if jugador == username:
                    mesas[mesa][i] = None
        emit('actualizar_jugadores', usuarios_conectados, broadcast=True)
        emit('actualizar_mesas', mesas, broadcast=True)

@socketio.on('entrar_asiento')
def handle_entrar_asiento(data):
    username = data['username']
    mesa_id = data['mesa_id']
    asiento = data['asiento']

    if mesa_id in mesas and mesas[mesa_id][asiento] is None:
        mesas[mesa_id][asiento] = username
        emit('actualizar_mesas', mesas, broadcast=True)

@socketio.on('salir_asiento')
def handle_salir_asiento(data):
    username = data['username']
    mesa_id = data['mesa_id']
    asiento = data['asiento']

    if mesa_id in mesas and mesas[mesa_id][asiento] == username:
        mesas[mesa_id][asiento] = None
        emit('actualizar_mesas', mesas, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)