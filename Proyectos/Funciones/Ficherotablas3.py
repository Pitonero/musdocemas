# Función que pida dos números n y m entre 1 y 10, lea el fichero tabla-n.txt 
# con la tabla de multiplicar de ese número, y muestre por pantalla la línea m 
# del fichero. Si el fichero no existe debe mostrar un mensaje por pantalla informando de ello.

n = int(input('Introduce un número entero entre 1 y 10: '))
m = int(input('Introduce otro número entero entre 1 y 10: '))
nombre_fichero = 'tabla-' + str(n) + '.txt'
try: 
    with open(nombre_fichero, 'r') as f:
        lineas = f.readlines()
    print(lineas[m - 1])
except FileNotFoundError:
    print('No existe el fichero con la tabla del ', n)