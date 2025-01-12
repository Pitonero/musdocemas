# sockets.py
from flask_socketio import emit, join_room, leave_room
from app.models import Room
from app.game_logic import MusGame

def setup_sockets(socketio):
    @socketio.on('join_lobby')
    def handle_join_lobby(data):
        room_name = data['room']
        join_room(room_name)
        emit('player_joined', {'username': data['username']}, room=room_name)

    @socketio.on('start_game')
    def handle_start_game(data):
        room_name = data['room']
        # Lógica para iniciar partida
        emit('game_started', {}, room=room_name)

    # Otros eventos (como chat, actualizar puntuaciones, etc.)
    
    # sockets.py (continuación)

# Crear instancia de juego por sala
    games = {}

    @socketio.on('join_game')
    def join_game(data):
        room = data['room']
        join_room(room)
        if room not in games:
            games[room] = MusGame()  # Crear una nueva partida si no existe

    @socketio.on('player_move')
    def player_move(data):
       room = data['room']
       move = data['move']
       game = games[room]
    
    # Procesar movimiento en la lógica del juego
       game.process_move(request.sid, move)
    
    # Enviar estado actualizado a todos los jugadores de la sala
       emit('game_update', {'score1': game.scores[0], 'score2': game.scores[1]}, room=room)

