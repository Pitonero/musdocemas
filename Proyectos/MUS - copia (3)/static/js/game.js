// Establece conexión WebSocket para la sala de juego
const socket = io.connect('http://' + document.domain + ':' + location.port);

socket.on('connect', () => {
    socket.emit('join_game', {});
});

socket.on('game_update', (data) => {
    document.getElementById('score1').innerText = data.score1;
    document.getElementById('score2').innerText = data.score2;
});

function sendMove(move) {
    socket.emit('player_move', { 'move': move });
}