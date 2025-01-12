from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_session import Session

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
socketio = SocketIO(app, manage_session=False)

# Lista para jugadores logados y mesas disponibles
logged_players = []
tables = []

@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('waiting_room.html', username=session['username'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        session['username'] = username
        return redirect(url_for('home'))
    return render_template('login.html')

@socketio.on('join')
def handle_join(data):
    username = data.get('username')
    if username and username not in logged_players:
        logged_players.append(username)
    emit('update_players', logged_players, broadcast=True)

@socketio.on('connect')
def handle_connect():
    username = session.get('username')
    if username and username not in logged_players:
        logged_players.append(username)
    emit('update_players', logged_players, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    username = session.get('username')
    if username in logged_players:
        logged_players.remove(username)
    emit('update_players', logged_players, broadcast=True)

@socketio.on('chat_message')
def handle_chat_message(data):
    username = data.get('username')
    message = data.get('message')
    print(f"chat_message Mensaje recibido de {username}: {message}")  # Para verificar
    emit('chat_message', {'username': username, 'message': message}, broadcast=True)

@socketio.on('create_table')
def handle_create_table(data):
    table_name = data['table_name']
    if table_name not in tables:
        tables.append(table_name)
        emit('update_tables', tables, broadcast=True)

@socketio.on('join_table')
def handle_join_table(data):
    table_name = data['table_name']
    emit('player_joined', {'username': session['username'], 'table_name': table_name}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)

