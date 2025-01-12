const username = document.getElementById('username').getAttribute('data-username');
const socket = io.connect();
// Recuperamos el parámetro username desde el html
socket.emit('join', { username: username });
	
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