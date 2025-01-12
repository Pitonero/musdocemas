#El fichero cotizacion.csv contiene las cotizaciones de las empresas del IBEX35 con las siguientes columnas: 
# Nombre (nombre de la empresa), Final (precio de la acción al cierre de bolsa), Máximo (precio máximo de la 
# acción durante la jornada), Mínimo (precio mínimo de la acción durante la jornada), Volumen (Volumen al 
# cierre de bolsa), Efectivo (capitalización al cierre en miles de euros).

#Construir una función reciba el fichero de cotizaciones y devuelva un diccionario con los datos del fichero por columnas.

#Construir una función que reciba el diccionario devuelto por la función anterior y cree un fichero en formato csv 
# con el mínimo, el máximo y la media de dada columna.


def limpiar(cifra):
    """
    Función que elimina los puntos de separación de miles y cambia las comas de separación de decimales por puntos.
    Parámetros:
        - cifra: Es una cadena con una cifra
    Devuelve:
        Un real con la cifra de la cadena después de eliminar el separador de miles y cambiar el separador de decimales por punto.
    """
    cifra = cifra.replace('.', '')
    cifra = cifra.replace(',','.')
    return float(cifra) 

def preprocesado(ruta):
    """
    Función que preprocesa los datos contenidos en un fichero con formato csv y devuelve un diccionario con los nombres de las columnas como claves y las listas de valores asociados a ellas.
    Parámetros:
        - ruta: Es una cadena con la ruta del fichero.
    Devuelve:
        Un diccionario con pares formados por los nombres de las columnas y las listas de valores en las columnas.
    """
    try:
        # Abrimos el fichero en modo lectura
        with open(ruta, 'r') as f:
            # Leemos el fichero por líneas en una lista
            lineas = f.read().split('\n')
    except FileNotFoundError:
        print('El fichero no existe.')
        return
    
    # Leemos las claves del primer elemento de la lista y creamos una lista dividiendo la línea por el punto y coma.
    claves = lineas.pop(0).split(";")
    # Creamos el diccionario para guardar las cotizaciones
    cotizaciones = {}
    # Inicializamos el diccionario con listas vacías
    for i in claves:
        cotizaciones[i] = []
    # Bucle iterativo para recorrer la lista de lineas
    for linea in lineas:
        # Creamos una lista con los campos dividiendo la línea por el punto y coma
        campos = linea.split(';')
        # Añadimos el primer campo (el nombre de la empresa) a la lista del diccionario
        cotizaciones[claves[0]].append(campos[0])
        # Bucle iterativo para añadir el resto de los campos a las listas correspondientes del diccionario. 
        # Previamente los campos se limpian del carácter de separación de miles y se sustituye la coma por el punto para el separador de decimales.
        for i in range(1, len(campos)):
            cotizaciones[claves[i]].append(limpiar(campos[i]))
    return cotizaciones


def resumen_cotizacion(cotizaciones, ruta):
    """
    Función que recibe un diccionario con los valores de cotización y crear un fichero con un resumen con el mínimo, el máximo y la media.
    Parámetros:
        - cotizaciones: Es un diccionario con pares cuyas claves son los nombres de la variables medidas y cuyos valores son las listas de valores de cada variable.
        - ruta: Es una cadena con la ruta del fichero.
    """
    # Eliminamos el primer par del diccionario que contiene los nombres de las empresas.
    del(cotizaciones['Nombre'])
    # Inicializamos una cadena con el contenido que después se escribirá en el fichero.
    contenido = ""
    # Escribimos en la primera línea los nombres de las columnas.
    contenido += 'Nombre'
    # Bucle iterativo para crear los encabezados de las cotizaciones.
    for i in cotizaciones:
        contenido += ";" + i
    # Calculamos los mínimos de cada lista y los escribimos en las columnas correspondientes
    contenido += '\nMínimo'
    for i in cotizaciones.values():
        contenido += ';' + str(min(i))
    # Calculamos los máximos de cada lista y los escribimos en las columnas correspondientes
    contenido += '\nMáximo'
    for i in cotizaciones.values():
        contenido += ';' + str(max(i))
    # Calculamos las medias de cada lista y las escribimos en las columnas correspondientes
    contenido += '\nMedia'
    for i in cotizaciones.values():
        contenido += ';' + str(sum(i)/len(i))
    # Abrimos el fichero en modo escritura.
    with open(ruta, 'w') as f:
        # Escribimos el contenido en el fichero
        f.write(contenido)
    return


# Llamada a las funciones de prueba
cotizaciones = preprocesado('cotizacion.csv')
print(cotizaciones)
resumen_cotizacion(cotizaciones, 'resumen-cotizacion.csv')