from flask import Flask, render_template, session, request, redirect, url_for
from flask_socketio import SocketIO, emit
from flask_session import Session

app = Flask(__name__)
app.secret_key = 'clave_secreta'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
socketio = SocketIO(app, manage_session=False)

# tables con jugadores
tables = {"table_1": [None, None, None, None]}
logged_players = []

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
    if username and username not in logged_players:
        logged_players.append(username)
    emit('update_player', logged_players, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    username = session.get('username')
    if username in logged_players:
        logged_players.remove(username)
        for table, jugadores in tables.items():
            for i, jugador in enumerate(jugadores):
                if jugador == username:
                    tables[table][i] = None
        emit('update_player', logged_players, broadcast=True)
        emit('actualizar_tables', tables, broadcast=True)

@socketio.on('entrar_asiento')
def handle_entrar_asiento(data):
    username = data['username']
    table_id = data['table_id']
    asiento = data['asiento']

    if table_id in tables and tables[table_id][asiento] is None:
        tables[table_id][asiento] = username
        emit('update_tables', tables, broadcast=True)

@socketio.on('salir_asiento')
def handle_salir_asiento(data):
    username = data['username']
    table_id = data['table_id']
    asiento = data['asiento']

    if table_id in tables and tables[table_id][asiento] == username:
        tables[table_id][asiento] = None
        emit('update_tables', tables, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)