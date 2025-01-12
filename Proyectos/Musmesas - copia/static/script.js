const socket = io.connect();

const usuario = document.getElementById('usuario').dataset.usuario;

// Inicializar eventos
socket.on('connect', () => {
    console.log('Conectado al servidor');
});

socket.on('actualizar_jugadores', (jugadores) => {
    const listaJugadores = document.getElementById('lista-jugadores');
    listaJugadores.innerHTML = '';
    jugadores.forEach(jugador => {
        const li = document.createElement('li');
        li.textContent = jugador;
        listaJugadores.appendChild(li);
    });
});

socket.on('actualizar_mesas', (mesas) => {
    for (const [mesaId, jugadores] of Object.entries(mesas)) {
        const mesa = document.getElementById(mesaId);
        if (mesa) {
            const asientos = mesa.querySelectorAll('.jugador');
            jugadores.forEach((jugador, index) => {
                const asiento = asientos[index];
                if (jugador) {
                    asiento.style.backgroundImage = `url('avatar.png')`;
                    asiento.nextElementSibling.textContent = jugador;
                } else {
                    asiento.style.backgroundImage = '';
                    asiento.nextElementSibling.textContent = `Jugador ${index + 1}`;
                }
            });
        }
    }
});

function toggleAsiento(elemento, mesaId, asientoIndex) {
    if (!elemento.classList.contains('ocupado')) {
        elemento.classList.add('ocupado');
        socket.emit('entrar_asiento', { username: usuario, mesa_id: mesaId, asiento: asientoIndex });
    } else {
        elemento.classList.remove('ocupado');
        socket.emit('salir_asiento', { username: usuario, mesa_id: mesaId, asiento: asientoIndex });
    }
}
