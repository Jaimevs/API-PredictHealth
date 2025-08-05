# email_service.py
import os
import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.settings import settings

def generate_verification_code(length=6):
    """Genera un código de verificación aleatorio"""
    return ''.join(random.choices(string.digits, k=length))

async def send_verification_email(to_email: str, verification_code: str):
    """Envía un correo de verificación con código"""
    try:
        # Crear mensaje
        message = MIMEMultipart()
        message['From'] = settings.EMAIL_FROM
        message['To'] = to_email
        message['Subject'] = 'Código de Verificación - Predict Health API'
        
        # Contenido HTML
        html_content = f"""
        <html>
          <body>
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
              <h2 style="color: #333; text-align: center;">Bienvenido a Predict Health</h2>
              <p>Gracias por registrarte. Tu código de verificación es:</p>
              <div style="text-align: center; margin: 30px 0;">
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 4px; font-size: 24px; letter-spacing: 5px; font-weight: bold; color: #007bff;">
                  {verification_code}
                </div>
              </div>
              <p>Introduce este código en la aplicación para verificar tu cuenta.</p>
              <p style="color: #dc3545; font-weight: bold;">El código expirará en 24 horas.</p>
              <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #666; font-size: 12px;">
                &copy; 2025 Predict Health API. Todos los derechos reservados.
              </div>
            </div>
          </body>
        </html>
        """
        
        # Adjuntar contenido HTML al mensaje
        message.attach(MIMEText(html_content, 'html'))
        
        # Conectar al servidor SMTP
        server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
        server.starttls()  # Activar encriptación
        server.login(settings.EMAIL_FROM, settings.EMAIL_PASSWORD)
        
        # Enviar correo
        server.send_message(message)
        server.quit()
        
        print(f"Correo enviado exitosamente a {to_email}")
        return {'success': True, 'message': 'Correo enviado exitosamente'}
        
    except Exception as e:
        print(f'Error al enviar email: {e}')
        return {'success': False, 'error': str(e)}