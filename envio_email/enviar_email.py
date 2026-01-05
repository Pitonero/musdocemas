import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class Ccorreo:
    def enviar_email(correo_destinatario, codigo_activacion):
        # Configura los detalles del servidor SMTP
        servidor_smtp = "smtp.gmail.com"
        puerto_smtp = 999
        usuario = "xxxxxxxxxxxxs@gmail.com"
        contraseña = "xxxxxxxxxxxxxxxxxxxx"
        #correo_destinatario = 'lpablonieto@gmail.com'
        # Configuración del correo
        mensaje = MIMEMultipart()
        mensaje["From"] = usuario
        mensaje["To"] = correo_destinatario
        mensaje["Subject"] = "Código activación MusDoceMas"
        cuerpo = "Por favor incluye el siguiente codigo de Activacion en el registro: " + codigo_activacion
        mensaje.attach(MIMEText(cuerpo, "plain"))

        #Envio del correo
        try:
            # Establecer conexión con el servidor
            servidor = smtplib.SMTP(servidor_smtp, puerto_smtp)
            servidor.starttls()  # Iniciar la conexión segura
            servidor.login(usuario, contraseña)  # Iniciar sesión

            # Enviar el correo electrónico
            servidor.sendmail(usuario, correo_destinatario, mensaje.as_string())
            print("Correo enviado exitosamente a", correo_destinatario)

        except Exception as e:
            print("Error al enviar el correo:", e)

        finally:
            # Cerrar la conexión con el servidor
            servidor.quit()
 
 
