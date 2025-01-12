# app/game_logic.py

class MusGame:
    def __init__(self):
        self.players = []
        self.scores = [0, 0]  # Puntuaciones de ambos equipos
        self.turn = 0  # Control del turno
        self.round_started = False
        self.round_data = {'bets': [], 'moves': []}  # Datos de la ronda actual

    def add_player(self, player_id):
        """Añade un jugador si aún hay espacio."""
        if len(self.players) < 4:
            self.players.append(player_id)
            return True
        return False

    def start_round(self):
        """Inicia una nueva ronda si hay cuatro jugadores."""
        if len(self.players) == 4:
            self.round_data = {'bets': [], 'moves': []}
            self.round_started = True
            self.turn = 0  # Reiniciar turno
            return True
        return False

    def process_move(self, player_id, move):
        """Procesa los movimientos de los jugadores según las reglas."""
        if player_id != self.players[self.turn]:
            return "Not your turn"

        # Procesar los diferentes movimientos del mus
        if move == 'mus':
            self.round_data['moves'].append(f"{player_id} pidió mus")
        elif move == 'no_mus':
            self.round_data['moves'].append(f"{player_id} rechazó el mus")
        elif move == 'envidar':
            self.round_data['bets'].append(f"{player_id} envidó")
        elif move == 'ver':
            self.round_data['moves'].append(f"{player_id} vio")
        else:
            return "Movimiento no válido"

        # Avanzar al siguiente jugador
        self.turn = (self.turn + 1) % 4

        # Verificar si todos los jugadores han realizado sus movimientos
        if len(self.round_data['moves']) >= 4:
            self.calculate_points()

    def calculate_points(self):
        """Calcula los puntos después de una ronda."""
        # Aquí iría la lógica para calcular puntos con base en la ronda
        # En este ejemplo, simplemente sumamos 1 punto al equipo ganador
        team = self.turn % 2
        self.scores[team] += 1
        self.round_started = False  # Terminar ronda


