// Establece conexión WebSocket
const socket = io.connect('http://' + document.domain + ':' + location.port);

socket.on('connect', () => {
    socket.emit('join_lobby', {'username': 'nombre_usuario'});
});

socket.on('player_joined', (data) => {
    const playerList = document.getElementById('player-list');
    const listItem = document.createElement('li');
    listItem.textContent = data.username;
    playerList.appendChild(listItem);
});

function startGame() {
    socket.emit('start_game', {});
}