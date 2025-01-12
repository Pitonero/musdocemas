from flask import Flask, render_template
from flask_socketio import SocketIO, join_room, leave_room, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join_room')
def handle_join(data):
    room = data['room']
    username = data['username']
    join_room(room)
    print(f"{username} se unió a la room {room}")
    emit('chat_message', {'username': username, 'message': f'{username} se unió a la room {room}'}, to=room)

@socketio.on('send_message')
def handle_message(data):
    room = data['room']
    message = data['message']
    emit('chat_message', {'username': 'Anon', 'message': message}, to=room)

if __name__ == '__main__':
    socketio.run(app, debug=True)
