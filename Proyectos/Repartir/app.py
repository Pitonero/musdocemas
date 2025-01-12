import random

# Generar la baraja de cartas (sin 8 y 9)
def crear_baraja():
    palos = ['o', 'c', 'e', 'b']  # oros, copas, espadas, bastos
    valores = [1, 2, 3, 4, 5, 6, 7, 10, 11, 12]  # As, 2-7, Sota, Caballo, Rey
    baraja = [f"{valor}{palo}" for palo in palos for valor in valores]
    return baraja

# Repartir cartas con manejo de descartes
def repartir_cartas(baraja, num_cartas_por_jugador, descartes):
    """
    Reparte cartas de la baraja según el número de cartas solicitado por cada jugador.

    Args:
    - baraja (list): Lista de cartas disponibles.
    - num_cartas_por_jugador (list): Lista de enteros indicando cuántas cartas pide cada jugador.
    - descartes (list): Lista de cartas descartadas disponibles.

    Returns:
    - manos (dict): Diccionario con las cartas repartidas por jugador.
    - baraja (list): Baraja restante tras repartir las cartas.
    - descartes (list): Cartas que quedan como descartadas.
    """
    total_cartas_solicitadas = sum(num_cartas_por_jugador)

    # Si no hay suficientes cartas en la baraja, usar los descartes
    if len(baraja) < total_cartas_solicitadas:
        print("No hay suficientes cartas en la baraja. Usando descartes.")
        baraja.extend(descartes)
        random.shuffle(baraja)
        descartes.clear()

    if len(baraja) < total_cartas_solicitadas:
        raise ValueError("No hay suficientes cartas incluso con descartes.")

    # Mezclar la baraja
    random.shuffle(baraja)

    # Crear las manos de los jugadores
    manos = {f"Jugador {i+1}": [] for i in range(len(num_cartas_por_jugador))}

    for i, num_cartas in enumerate(num_cartas_por_jugador):
        for _ in range(num_cartas):
            carta = baraja.pop()  # Extraer una carta de la baraja
            manos[f"Jugador {i+1}"].append(carta)

    return manos, baraja, descartes

# Ejemplo de uso
def main():
    baraja = crear_baraja()
    descartes = []  # Lista para almacenar las cartas descartadas
    print(f"Baraja inicial ({len(baraja)} cartas): {baraja}")

    # Primera ronda: cada jugador recibe 4 cartas
    num_cartas_por_jugador = [4, 4, 4, 4]

    try:
        manos, baraja_restante, descartes = repartir_cartas(baraja, num_cartas_por_jugador, descartes)
        print("\nCartas repartidas en la primera ronda:")
        for jugador, cartas in manos.items():
            print(f"{jugador}: {cartas}")

        print(f"\nBaraja restante ({len(baraja_restante)} cartas): {baraja_restante}")

        # Simular descartes
        descartes.extend(["2o", "3c", "7e", "10b"])  # Ejemplo de descartes
        print(f"\nDescartes actuales: {descartes}")

        # Segunda ronda: jugadores eligen cuántas cartas quieren (1-4)
        num_cartas_por_jugador = [2, 1, 3, 4]  # Por ejemplo: Jugador 1 pide 2 cartas, Jugador 2 pide 1, etc.
        manos, baraja_restante, descartes = repartir_cartas(baraja_restante, num_cartas_por_jugador, descartes)

        print("\nCartas repartidas en la segunda ronda:")
        for jugador, cartas in manos.items():
            print(f"{jugador}: {cartas}")

        print(f"\nBaraja restante ({len(baraja_restante)} cartas): {baraja_restante}")
        print(f"\nDescartes restantes: {descartes}")
    except ValueError as e:
        print(e)




if __name__ == "__main__":
    main()
