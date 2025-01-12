# Definimos el tablero como una lista de 3 listas.
tablero = [ 
    [" ", " ", " "], 
    [" ", " ", " "], 
    [" ", " ", " "], 
] 
  
def mostrar_tablero(tablero): 
    '''
    Función que muestra el tablero por pantalla.
    
    Parámetros:
        - tablero: Es una lista de listas con el tablero.
    '''
    # Bucle iterativo para recorrer por valor la lista del tablero. 
    # fila toma como valores cada una de las listas de la lista tablero.
    for fila in tablero: 
        # Mostramos la fila por pantalla. Se muestra como una lista. 
        print(fila) 
    return True 
  
def poner_ficha(tablero, x, y, ficha):
    '''
    Función que pone una ficha en el tablero.

    Parámetros:
        tablero: Es una lista de listas con el tablero.
        x: Es un entero entre 1 y 3 con la fila donde colocar la ficha.
        y: Es un entero entre 1 y 3 con la columna donde colocar la ficha.
        ficha: Es una cadena con el símbolo a colocar.
    Salida:
        El tablero con la nueva ficha colocada si la posición dada está libre o el tablero original si no.
    '''
    # Condicional para ver si la posición indicada está vacía.
    if tablero[x-1][y-1] == " ": 
        # Si la posición está vacía, colocamos la ficha en la posición.
        tablero[x-1][y-1] = ficha
    else: 
        # Si no está vacía, avisamos al usuario.
        print("Esa coordenada ya está siendo utilizada, use una libre.") 
    return tablero 
  
def final(tablero):
    '''
    Función para comprobar si hay ganador en tablero.

    Parámetros:
        - tablero: Es una lista de listas con el tablero.
    Salida:
        Un cadena vacía si no ha terminado la partida o el carácter de la ficha ganadora si se ha terminado y hay ganador o la cadena EMPATE si se ha terminado y no hay ganador..
    '''
    # Bucle iterativo para comprobar si hay tres en raya en alguna fila.
    for fila in range(3): 
        # Condicional para ver si las fichas de la fila son iguales.
        if tablero[fila][0] == tablero[fila][1] == tablero[fila][2] != " " : 
            # Si las fichas de la fila son iguales el jugador con esa ficha es el ganador y la devolvemos.
            return tablero[fila][0]
    # Bucle iterativo para comprobar si hay tres en raya en alguna columna.
    for columna in range(3):
        # Condicional para ver si las fichas de la columna son iguales. 
        if tablero[0][columna] == tablero[1][columna] == tablero[2][columna] != " " : 
            # Si las fichas de la columna son iguales el jugador con esa ficha es el ganador y la devolvemos.
            return tablero[0][columna]
    # Condicional para comprobar la diagonal principal.
    if tablero[0][0] == tablero[1][1] == tablero[2][2] != " ": 
        # Si las fichas de la diagonal principal son iguales el jugador con esa ficha es el ganador y la devolvemos.
        return tablero[0][0]
    # Condicional para comprobar la diagonal secundaria.
    if tablero[0][2] == tablero[1][1] == tablero[2][0] != str(" "): 
        # Si las fichas de la diagonal secundaria son iguales el jugador con esa ficha es el ganador y la devolvemos.
        return tablero[0][2]
    # Bucle iterativo para recorrer las filas del tablero y ver si quedan casillas sin ocupar. 
    # fila toma como valores las filas del tablero.
    for fila in tablero: 
        # Condicional para ver si la fila contiene un espacio en blanco.
        if " " in fila: 
            return ""
    return "EMPATE"
  
def preguntar_casilla(): 
    '''
    Función que pregunta por la casilla y la ficha a colocar.

    Salida:
        Una tupla con los siguientes elementos:
        - x: Un entero con la fila.
        - y: Un entero con la columna.
        - ficha: Una cadena con el carácter de la ficha.
    '''
    # Bucle condicional infinito para preguntar por la fila, columna y ficha.
    while True: 
        # Preguntamos por la fila.
        x = int(input("Introduce la coordenada X del 1 al 3: ")) 
        # Preguntamos por la columna.
        y = int(input("Introduce la coordenada Y del 1 al 3: ")) 
        # Preguntamos por la ficha.
        ficha = input("Introduce 0 para círculo o X para cruz: ")
        # Condional para ver si la fila y columna son válidas.
        if x >= 1 and x <= 3 and y >= 1 and x <= 3: 
            # Si la fila y columna es válida, condicional para ver si la ficha es X o 0.
            if ficha.lower() == "x" or ficha == "0":
                # Si la ficha es válida, terminamos el bucle y devolvemos la fila, columna y ficha.
                return x, y, ficha 
        else: 
            # Si la fila o columna no son válidas, informamos al usuario y le volvemos a preguntar.
            print("Por favor introduce unas coordenadas válidas.") 

# Programa principal
# Bucle condicional para preguntar por el próximo movimiento, hasta que termine la partida.
while True:
    # Mostramos el tablero por pantalla
    mostrar_tablero(tablero)
    print()
    # Preguntamos por la fila, columna y ficha del siguiente movimiento.
    x, y, ficha = preguntar_casilla()
    # Colocamos la ficha en el tablero.
    poner_ficha(tablero, x, y, ficha) 
    # Comprobamos si la partida ha terminado y hay ganador.
    fin = final(tablero)
    # Condicional para ver si la partida ha terminado y hay ganador.
    if fin: 
        # Si la partida ha terminado mostramos el tablero.
        mostrar_tablero(tablero)
        # Condicional para ver si la partida ha terminado en empate. 
        if fin == "EMPATE":
            print("La partida ha terminado en empate.")
        else:
            print("La partida la ha ganado el jugador con la ficha", fin + ".")
        # Salimos del bucle infinito una vez la partida ha terminado.
        break
