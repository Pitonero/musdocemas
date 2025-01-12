from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit
import random

app = Flask(__name__)
app.secret_key = "clave_secreta"
socketio = SocketIO(app)

# Estado global de mesas y jugadores
mesas = {}  # {mesa_id: {"estado": "En espera", "jugadores": [...], "avatares": [...], "descartes": [], "puntos": [0, 0]}}
cartas = [f"{num}{palo}" for palo in "oceb" for num in range(1, 13) if num not in [8, 9]]  # Baraja española

@app.route('/')
def home():
    return redirect(url_for('mesa_juego', mesa_id="Mesa_1"))

@app.route('/mesa_juego/<mesa_id>')
def mesa_juego(mesa_id):
    if mesa_id not in mesas:
        # Inicializar mesa
        mesas[mesa_id] = {
            "estado": "En espera",
            "jugadores": [None, None, None, None],
            "avatares": [None, None, None, None],
            "descartes": [],
            "puntos": [0, 0]
        }
    return render_template('mesa_juego.html', mesa=mesas[mesa_id], mesa_id=mesa_id)

@socketio.on('repartir_cartas')
def handle_repartir_cartas(data):
    mesa_id = data['mesa_id']
    if mesa_id not in mesas:
        return
    mesa = mesas[mesa_id]
    
    # Barajar cartas y repartir
    random.shuffle(cartas)
    mesa['cartas_repartidas'] = {
        i: cartas[i * 4:(i + 1) * 4] for i in range(4)
    }
    
    # Emitir las cartas a todos los jugadores conectados
    emit('actualizar_cartas', {"mesa_id": mesa_id, "cartas": mesa['cartas_repartidas']}, broadcast=True)


if __name__ == '__main__':
    socketio.run(app, debug=True)

