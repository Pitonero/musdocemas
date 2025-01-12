import tkinter as tk 

# Importar módulos restantes de tkinter
from tkinter import *
from tkinter import ttk
from tkinter import messagebox 
from Clientes import *
from Conexion import *

class formularioClientes: 
 global base
 base = None
 global texBoxId
 texBoxId = None
 global texBoxNombres
 texBoxNombres = None
 global texBoxApellidos
 texBoxApellidos = None
 global combo
 combo = None
 global groupBox
 groupBox = None
 global tree
 tree = None

def Formulario():
  global base
  global texBoxId
  global texBoxNombres
  global texBoxApellidos
  global combo
  global groupBox
  global tree

  try:
        base= Tk()
        base.geometry("1200x300")
        base.title("Formulario Python")
        
        groupBox = LabelFrame(base,text="Datos del personal",padx=5,pady=5) 
        groupBox.grid(row=0,column=0,padx=10, pady=10)
        
        labelId=Label(groupBox,text="Id:",width=13,font=("arial",12)).grid(row=0,column=0)
        texBoxId= Entry(groupBox)
        texBoxId.grid(row=0,column=1)
        labelNombres=Label(groupBox,text="Nombre:",width=13,font=("arial",12)).grid(row=1,column=0)
        texBoxNombres= Entry(groupBox)
        texBoxNombres.grid(row=1,column=1)       
        labelapellidos=Label(groupBox,text="Apellidos:",width=13,font=("arial",12)).grid(row=2,column=0)
        texBoxApellidos= Entry(groupBox)
        texBoxApellidos.grid(row=2,column=1)
        labelSexo=Label(groupBox,text="Sexo:",width=13,font=("arial",12)).grid(row=3,column=0)
        seleccionSexo = tk.StringVar()
        combo= ttk.Combobox(groupBox, values=["Masculino", "Femenino"],textvariable=seleccionSexo)
        combo.grid(row=3, column=1)
        seleccionSexo.set("Masculino")

        Button(groupBox,text="Guardar",width=10,command=guardarRegistros).grid(row=4,column=0)
        Button(groupBox,text="Modificar",width=10,command=modificarRegistros).grid(row=4,column=1)
        Button(groupBox,text="Eliminar",width=10,command=borrarRegistros).grid(row=4,column=2)

        groupBox = LabelFrame(base,text="Lista del personal",padx=5,pady=5,)
        groupBox.grid(row=0,column=1,padx=5,pady=5)

        # Ahora vamos a cfrear un TreeView
        # Configuramos las columnas

        tree = ttk.Treeview(groupBox,columns=("Id", "Nombre", "Apellidos", "Sexo"),show='headings',height=5)
        tree.column("# 1", anchor=CENTER)
        tree.heading("# 1",text="Id")
        tree.column("# 2", anchor=CENTER)
        tree.heading("# 2",text="Nombre")
        tree.column("# 3", anchor=CENTER)
        tree.heading("# 3",text="Apellidos")
        tree.column("# 4", anchor=CENTER)
        tree.heading("# 4",text="Sexo")

       # agregar los datos a la tabla y mostrar los datos 
        for row in CClientes.mostrarClientes():
          tree.insert("","end",values=row)

       # Refrescar los teck box al hacer click en una línea cualquiera del árbol:

        tree.bind("<<TreeviewSelect>>", seleccionarRegistro)    

        tree.pack() 

        base.mainloop()

  except ValueError as error:
        print("Error al mostrar la interfaz,error:{}".format(error))

def guardarRegistros():

     global texBoxNombres, texBoxApellidos, combo, groupBox

     try:
       # Verificar si los widgets están inicializados

        if texBoxNombres is None or texBoxApellidos is None or combo is None:
            print("Los widgets no están inicializados")
            return
        nombres = texBoxNombres.get()
        apellidos = texBoxApellidos.get()
        sexo = combo.get()

        CClientes.insertarClientes(nombres, apellidos, sexo)
        messagebox.showinfo("Informacion", "Los datos se insertaron en BBDD")
        
        actualizarTreeView()

        # Limpiamos los campos
        texBoxNombres.delete(0,END)
        texBoxApellidos.delete(0,END)
        combo.delete(0,END)

     except ValueError as error:
        print("Error al insertar los datos:{}".format(error))

def modificarRegistros():

     global texBoxId, texBoxNombres, texBoxApellidos, combo, groupBox

     try:
       # Verificar si los widgets están inicializados

        if texBoxId is None or texBoxNombres is None or texBoxApellidos is None or combo is None:
            print("Los widgets no están inicializados")
            return
        idUsuario = texBoxId.get()
        nombres = texBoxNombres.get()
        apellidos = texBoxApellidos.get()
        sexo = combo.get()

        CClientes.modificarClientes(idUsuario, nombres, apellidos, sexo)
        messagebox.showinfo("Informacion", "Los datos se actualizaron en BBDD")
        
        actualizarTreeView()

        # Limpiamos los campos
        texBoxId.delete(0,END)
        texBoxNombres.delete(0,END)
        texBoxApellidos.delete(0,END)
        combo.delete(0,END)

     except ValueError as error:
        print("Error al insertar los datos:{}".format(error))


def borrarRegistros():

     global texBoxId, texBoxNombres, texBoxApellidos

     try:
       # Verificar si los widgets están inicializados

        if texBoxId is None :
            print("Los widgets no están inicializados")
            return
        idUsuario = texBoxId.get()

        CClientes.borrarClientes(idUsuario)
        messagebox.showinfo("Informacion", "Los datos se borraron en BBDD")
        
        actualizarTreeView()

        # Limpiamos los campos
        texBoxId.delete(0,END)
        texBoxNombres.delete(0,END)
        texBoxApellidos.delete(0,END)

     except ValueError as error:
        print("Error al borrar los datos:{}".format(error))


def actualizarTreeView():  
    global tree

    try:
      # Borrar todos los elementos del arbol menos la cabecera
        tree.delete(*tree.get_children()) 

      # Refrescamos con los nuevos datos
        datos = CClientes.mostrarClientes()
        for row in CClientes.mostrarClientes():
            tree.insert("","end",values=row)

    except ValueError as error:
        print("Error al actualizar tabla:{}".format(error))

def seleccionarRegistro(event):
     try:
      # Obtener el ID del elemento seleccionado:
            itemSeleccionado = tree.focus()

      # Obtener los valores por columnas
            values = tree.item(itemSeleccionado)['values']

      # Establecer los valores en sus casilleros:
            texBoxId.delete(0,END)
            texBoxId.insert(0,values[0])
            texBoxNombres.delete(0,END)
            texBoxNombres.insert(0,values[1])
            texBoxApellidos.delete(0,END)
            texBoxApellidos.insert(0,values[2])
            combo.set(values[3])

     except ValueError as error:
        print("Error al actualizar los text box desde el árbol:{}".format(error))

Formulario()
