"""El laberinto se representará como una una lista de listas, donde cada lista es una fila del laberinto y cada casilla se representará con un espacio ' ' si hay paso o con la letra 'X' si hay un muro, tal y como se muestra a continuación:

laberinto = [
    [' ', 'X', 'X', 'X', 'X'], 
    [' ', 'X', ' ', ' ', ' '],
    [' ', 'X', ' ', 'X', ' '], 
    [' ', ' ', ' ', 'X', ' '], 
    ['X', 'X', 'X', 'X', 'S']
    ]
El laberinto se debe crear a partir de una tupla con las coordenadas de las casillas donde hay muro, como la siguiente:

muro = ((0,1), (0,2), (0,3), (0,4), (1,1), (2,1), (2,3), (3,3), (4,0), (4,1), (4,2), (4,3))
"""
def laberinto(dimension, muros):
    ''' Función que construye un laberinto cuadrado de una dimensión dada poniendo.

    Parámetros:
        - dimension: Es un entero con la dimensión del laberinto. 
        - muros: Es una lista de tuplas con las coordenadas (x,y) donde hay muros.

    Salida: 
        Una matriz (lista de listas) que representa el laberinto. 
    '''

    # Creamos una lista vacía para añadir las filas del laberinto.
    laberinto = []
    # Bucle iterativo para añadir las filas del laberinto.
    # i toma valores de 0 a dimension-1 
    for i in range(dimension):
        # Creamos una lista vacía para añadir las casillas de la fila.
        fila = []
        # Bucle iterativo para recorrer las columnas del laberinto.
        # j toma valores de 0 a dimension-1.
        for j in range(dimension):
            # Condicional para comprobar si la tupla está en el la lista de muros.
            if tuple([i, j]) in muro:
                # Si la tupla está en la lista de muros ponemos una X en la casilla.
                fila.append('X')
            else:
                # Si la tupla no está en el muro ponemos un espacio en blanco en la casilla.
                fila.append(' ')
        laberinto.append(fila)
    return laberinto

# Tupla de coordenadas de las celdas con muro en el laberinto
muro = ((0,1), (0,2), (0,3), (0,4), (1,1), (2,1), (2,3), (3,3), (4,0), (4,1), (4,2), (4,3)) 
lab = laberinto(5, muro)   

# Mostrar el laberinto por pantalla
for i in lab:
    print(''.join(i))