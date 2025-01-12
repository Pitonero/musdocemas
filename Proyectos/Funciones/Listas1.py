def filtra_lista(funcion, lista):
    '''Función que filtra los elementos de una lista que devuelven true al aplicarle una función booleana.

    Parámetros:
        - funcion: Es una función booleana (devuleve true o false)
        - lista: Es una lista con valores que se pasarán como argumentos a funcion.
    Devuelve:
        Una lista con los elementos de la lista que devuelven true al aplicarles la función booleana.
    '''
    l = []
    for i in lista:
        if funcion(i):
            l.append(i)
    return l

def par(n):
    return n % 2 == 0

print(filtra_lista(par, [1, 2, 3, 4, 5, 6]))