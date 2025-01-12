
#archivo = open("frases_famosas.txt", "w")
#archivo.write("¡Hola, Python!")
#archivo.close()
print("Primer open")
archivo = open("frases_famosas.txt", "r")
contenido = archivo.read()
print(contenido)
archivo.close()
print("Segundo open")
with open("frases_famosas.txt") as archivo:
    for linea in archivo:
        print(linea)

print("Va a escribir")
palabras = ["Genial", "Verde", "Python", "Código"]

# Abre el fichero y escribe perdiéndose lo que tuviera antes
#with open("frases_famosas.txt", "w") as archivo:
#    for palabra in palabras:
#        archivo.write(palabra + "\n")
# Con este ejemplo, se añade al fichero la información:
palabras = ["Genial", "Verde", "Python", "Código"]

with open("frases_famosas.txt", "a") as archivo:
    for palabra in palabras:
        archivo.write(palabra + "\n")

import os

if os.path.exists("frases_famosas.txt"):
  print("Este archivo si existe y lo va a borrar.")
#  os.remove("frases_famosas.txt")
else:
  print("Este archivo no existe.")

  # Módulos
import random
numero_aleatorio = random.randint(1, 100)
print(numero_aleatorio)

# Excepciones
try:
    resultado = 10 / 0
except ZeroDivisionError:
    print("Error: división por cero")

# Funciones
def suma(a, b):
    return a + b

resultado = suma(2, 3)
print(resultado)

# Listas
frutas = ["manzana", "plátano", "naranja"]
print(frutas)

# Acceder a un elemento de la lista
print(frutas[0])

# Agregar un elemento a la lista
frutas.append("pera")
print(frutas)

# Longitud de la lista
print(len(frutas))