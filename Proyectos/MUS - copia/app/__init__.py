from flask_login import LoginManager,login_user, logout_user,login_required
from flask_session import Session
from db.usuarios import *
from db.Conexion import *


login_manager = LoginManager()

# Función para cargar el usuario desde la base de datos
#@login_manager.user_loader
#def load_user(user_id):
 #   conn = create_connection()
 #   cursor = conn.cursor(dictionary=True)
 #   cursor.execute("SELECT * FROM Usuarios WHERE usuario_id = %s", (user_id,))
 #   data = cursor.fetchone()
#    cursor.close()
#    conn.close()
 #   if data:
 #       return Usuario(id=data['usuario_id'], nombre_usuario=data['nombre_usuario'], email=data['email'])
 #   return None

  #from .auth import auth_bp
    #app.register_blueprint(auth_bp, url_prefix='/auth')

    #from .sockets import setup_sockets
    #setup_sockets(socketio)

    #return app

#@login_manager.user_loader
#def load_user(user_id):
 #   return User.query.get(int(user_id))