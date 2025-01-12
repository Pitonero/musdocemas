from flask import Flask, request, render_template, redirect, url_for, flash
from flask_mail import Mail, Message
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
import mysql.connector
import hashlib
import os

app = Flask(__name__)
app.secret_key = "tu_clave_secreta"

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "registro"  # Cambia esto a tu página de inicio de sesión

# Configuración para el correo electrónico
app.config['MAIL_SERVER'] = 'smtp.tucorreo.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'tu_correo@example.com'
app.config['MAIL_PASSWORD'] = 'tu_contraseña'

mail = Mail(app)

# Clase de usuario para Flask-Login
class Usuario(UserMixin):
    def __init__(self, id, nombre_usuario, email):
        self.id = id
        self.nombre_usuario = nombre_usuario
        self.email = email

# Función para cargar el usuario desde la base de datos
@login_manager.user_loader
def load_user(user_id):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Usuarios WHERE usuario_id = %s", (user_id,))
    data = cursor.fetchone()
    cursor.close()
    conn.close()
    if data:
        return Usuario(id=data['usuario_id'], nombre_usuario=data['nombre_usuario'], email=data['email'])
    return None

# Función para crear la conexión a MySQL
def create_connection():
    return mysql.connector.connect(
        host="localhost",
        user="tu_usuario_mysql",
        password="tu_contraseña_mysql",
        database="mus_game"
    )

# Resto de tu código para el registro, confirmación, etc.
# Ejemplo de ruta protegida (requiere inicio de sesión)
@app.route('/perfil')
@login_required
def perfil():
    return f"Bienvenido {current_user.nombre_usuario} a tu perfil"



# Ruta para mostrar el formulario de registro
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre_usuario = request.form['nombre_usuario']
        alias = request.form['alias']
        email = request.form['email']
        password = request.form['password']
        avatar_url = request.form['avatar_url']

        # Generar el hash de la contraseña
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        # Insertar el usuario en la base de datos
        try:
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO Usuarios (nombre_usuario, alias, email, password_hash, avatar_url)
                VALUES (%s, %s, %s, %s, %s)
            ''', (nombre_usuario, alias, email, password_hash, avatar_url))
            conn.commit()

            # Enviar email de confirmación
            enviar_email_confirmacion(email)

            flash('Registro exitoso. Verifica tu email para confirmar tu cuenta.', 'success')
            return redirect(url_for('registro'))
        
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'danger')
        
        finally:
            cursor.close()
            conn.close()
    return render_template('registro.html')

# Función para enviar el email de confirmación
def enviar_email_confirmacion(email):
    token = hashlib.sha256(email.encode()).hexdigest()  # Genera un token simple para verificación
    confirm_url = url_for('confirmar_registro', token=token, _external=True)
    msg = Message('Confirma tu cuenta', sender='tu_correo@example.com', recipients=[email])
    msg.body = f'Haz clic en el siguiente enlace para confirmar tu registro: {confirm_url}'
    mail.send(msg)

# Ruta para confirmar el registro
@app.route('/confirmar/<token>')
def confirmar_registro(token):
    # Aquí podrías actualizar el estado del usuario a 'confirmado' en la base de datos
    # usando el token, que en este caso sería un hash basado en el email
    flash('Cuenta confirmada con éxito.', 'success')
    return redirect(url_for('registro'))

if __name__ == '__main__':
    app.run(debug=True)
