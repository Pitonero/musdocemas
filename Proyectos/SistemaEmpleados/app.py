from flask import Flask
from flask import render_template, request,redirect,url_for, flash
from flask import send_from_directory
from Empleados import *
from Conexion import *
from datetime import datetime
import os

app= Flask(__name__)

app.secret_key="Develoteca"

#CARPETA= os.path.join('Proyectos/SistemaEmpleados/uploads/')
CARPETA= os.path.join('E:/Pablo/Util/Python/LIVE/Proyectos/SistemaEmpleados/uploads/')
app.config['CARPETA']=CARPETA

@app.route('/uploads/<nombrefoto>')
def uploads(nombrefoto):
    return send_from_directory(CARPETA,nombrefoto)

@app.route('/')
def index():

    empleados=CEmpleados.mostrarEmpleados()
    #print(empleados)

    return render_template('empleados/index.html', empleados=empleados, CARPETA=CARPETA)

@app.route('/elegante')
def hola_mundo_elegante():
    return """
    <html>
        <body>
            <h1>saludos!!</h1>
            <p>Hola Mundo!!</p>
        </body>    
    </html>    
"""  

@app.route('/create')
def create():
    return render_template('empleados/create.html')

@app.route('/store',methods=['POST'])
def storage():
    nombre =  request.form['txtNombre']   
    correo =  request.form['txtCorreo']  
    imagen =  request.files['txtFoto']   

    if nombre=='' or correo == '' or imagen=='':
        flash('Recuerda rellenar todos los campos')
        return redirect(url_for('create'))

    now= datetime.now()
    tiempo=now.strftime("%Y%H%M%S")

    if imagen.filename!='':
        nuevoNombreImagen=tiempo+imagen.filename
        imagen.save(CARPETA+nuevoNombreImagen)

    CEmpleados.insertarEmpleados(nombre, correo, nuevoNombreImagen)
    return redirect('/')
 
@app.route('/update',methods=['POST'])
def update():
    id = request.form['txtID']
    nombre =  request.form['txtNombre']   
    correo =  request.form['txtCorreo']  
    imagen =  request.files['txtFoto']  
    empleados=CEmpleados.mostrarUnEmpleado(id)

    imagenanterior=empleados[0] [3]
    archivo = CARPETA+imagenanterior

    if os.path.exists(archivo):
       os.remove(archivo)
    else:
        print("El fichero a borrar no existe:",archivo)
    
    now= datetime.now()
    tiempo=now.strftime("%Y%H%M%S")

    if imagen.filename!='':
        nuevoNombreImagen=tiempo+imagen.filename
        imagen.save(CARPETA+nuevoNombreImagen)
    
    CEmpleados.modificarEmpleados(id, nombre, correo, nuevoNombreImagen)
    return redirect('/')


@app.route('/destroy/<int:id>,<fichero>')


def destroy(id,fichero):
    archivo = CARPETA+fichero
    CEmpleados.borrarEmpleados(id)
    print("se va a borrar el fichero: ",archivo)
    if os.path.exists(archivo):
       os.remove(archivo)
    else:
        print("El fichero a borrar no existe:",archivo)
    return redirect('/')

@app.route('/edit/<int:id>')
def edit(id):
    empleados=CEmpleados.mostrarUnEmpleado(id)
    print(empleados)
    return render_template('empleados/edit.html', empleados=empleados)

if __name__== '__main__':
    app.run(debug=True)