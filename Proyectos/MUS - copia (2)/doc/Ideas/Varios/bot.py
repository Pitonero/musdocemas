from flask import Flask, jsonify, request
import random

app = Flask(__name__)

# Estado del juego
game_state = {
    "player_hand": [],
    "ai_hand": [],
    "message": "Turno del jugador"
}

# Función para repartir cartas (simulación básica)
def deal_cards():
    return [random.choice(["Oros", "Copas", "Espadas", "Bastos"]) for _ in range(4)]

# Generar el estado inicial de la partida
@app.route('/start')
def start_game():
    game_state["player_hand"] = deal_cards()
    game_state["ai_hand"] = deal_cards()
    game_state["message"] = "Juego iniciado. Tu turno."
    return jsonify(game_state)

# Acción del jugador y respuesta de ChatGPT
@app.route('/move')
def player_move():
    action = request.args.get("action")
    
    # Decisión básica de la IA en función de la acción del jugador
    if action == "apuesta":
        ai_action = random.choice(["igualo", "paso"])
    elif action == "pasa":
        ai_action = "pasa"
    elif action == "envite":
        ai_action = random.choice(["veo", "no veo"])
    elif action == "órdago":
        ai_action = random.choice(["acepto", "no acepto"])
    else:
        ai_action = "pasa"
    
    # Actualiza el estado del juego
    game_state["message"] = f"Tú elegiste {action}. ChatGPT respondió con {ai_action}."
    return jsonify(game_state)

if __name__ == '__main__':
    app.run(debug=True)
