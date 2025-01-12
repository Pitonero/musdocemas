const username = document.getElementById('username').getAttribute('data-username');
const socket = io.connect();
// Recuperamos el parámetro username desde el html
socket.emit('join', { username: username });

// Actualiza la lista de jugadores
socket.on('update_players', function(players) {
	alert('Entra en update players');
    const playerList = document.getElementById('player-list');
    playerList.innerHTML = '';
    players.forEach(player => {
        const li = document.createElement('li');
        li.innerText = player;
        playerList.appendChild(li);
    });
});

// Actualiza la lista de mesas
socket.on('update_tables', function(tables) {
    const tableList = document.getElementById('table-list');
    tableList.innerHTML = '';
    tables.forEach(table => {
        const li = document.createElement('li');
        li.innerText = table;
        li.onclick = () => joinTable(table);
        tableList.appendChild(li);
		alert("Mesas ", table);
    });
});

// Recibe y muestra un mensaje de chat
socket.on('chat_message', function(data) {
	alert('Entra en enviar mensaje de chat');
    const chatBox = document.getElementById('chat-box');
    const message = document.createElement('p');
    message.classList.add('message');
    message.innerText = `${data.username}: ${data.message}`;
    chatBox.appendChild(message);
    // Desplazar el contenedor `chat-box` al final
    chatBox.scrollTop = chatBox.scrollHeight;
});

// Enviar mensaje de chat
function sendMessage() {
	alert('el username que llega es :', '{{ username }}' );
    const message = document.getElementById('chat-message').value;
    socket.emit('chat_message', { username: username , message });
    document.getElementById('chat-message').value = '';
}

// Crear una mesa
function createTable() {
    const tableName = document.getElementById('table-name').value;
    socket.emit('create_table', { table_name: tableName });
    document.getElementById('table-name').value = '';
}

// Unirse a una mesa
function joinTable(tableName) {
    socket.emit('join_table', { table_name: tableName });
}