from Conexion import *

class CEmpleados:

    def mostrarEmpleados():    
        try: 
            cone = CConexion.ConexionBaseDeDatos()
            cursor = cone.cursor()
            cursor.execute ("select * from empleado;")
            miResultado = cursor.fetchall()
            cone.commit()
            cone.close()
            return miResultado

        except mysql.connector.Error as error:
            print("Error al mostrar datos {}".format(error))

    def mostrarUnEmpleado(id):    
        try: 
            cone = CConexion.ConexionBaseDeDatos()
            cursor = cone.cursor()
            sql="select * from empleado where id = "+str(id)+";"
            #valores = (id)
            cursor.execute(sql)
           # cursor.execute("select * from empleado where id = %s;"(id))
            miResultado = cursor.fetchall()
            cone.commit()
            cone.close()
            return miResultado

        except mysql.connector.Error as error:
            print("Error al mostrar un empleado {}".format(error))

    def insertarEmpleados(nombre,correo,imagen):
        try:
            cone = CConexion.ConexionBaseDeDatos()
            cursor = cone.cursor()
            sql = "insert into empleado values( null, %s, %s, %s);"
            # la variable valores tiene que ser una tupla (array que no se puede modificar)
            # como minima expresion es : (valor,). La coma hace que sea una tupla inmutable.
            valores = (nombre,correo,imagen)
            cursor.execute(sql,valores)
            cone.commit()
            print(cursor.rowcount, "Registro insertado")
            cone.close()

        except mysql.connector.Error as error:
            print("error de introduccion de datos {}".format(error))

    def modificarEmpleados(id,nombre,correo,imagen):
        try:
            cone = CConexion.ConexionBaseDeDatos()
            cursor = cone.cursor()
            sql = "update empleado set nombre = %s, correo = %s, imagen = %s where id = %s;"
            valores = (nombre,correo,imagen,id)
            cursor.execute(sql,valores)
            cone.commit()
            print(cursor.rowcount, "Registro actualizado")
            cone.close()

        except mysql.connector.Error as error:
            print("error al actualizar datos {}".format(error))

    def borrarEmpleados(id):
        try:
            cone = CConexion.ConexionBaseDeDatos()
            cursor = cone.cursor()
            sql="delete from empleado where id = "+str(id)+";"
            cursor.execute(sql)
            #valores = (id)
            #sql = "delete from empleado where id = %s;"
            # valores = (id)
            # cursor.execute(sql,valores)
            cone.commit()
            print(cursor.rowcount, "Registro borrado")
            cone.close()

        except mysql.connector.Error as error:
            print("error al borrar datos {}".format(error))