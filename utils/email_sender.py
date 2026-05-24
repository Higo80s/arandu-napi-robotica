"""
Módulo de Envio de E-mails
==========================
Responsável por gerenciar o envio assíncrono de notificações por e-mail.
Requer Flask-Mail.
"""
import os
from flask import current_app
from flask_mail import Message
from threading import Thread
from extensions import mail # [REFATORACAO] Instancia centralizada

# Instância global do Mail (sera inicializada no app.py)
# mail = Mail() -> Removido (v6.3)

def send_async_email(app, msg):
    """Função background para envio real"""
    with app.app_context():
        try:
            mail.send(msg)
            print(f"📧 [EMAIL] Enviado com sucesso para: {msg.recipients}")
        except Exception as e:
            print(f"❌ [EMAIL ERRO] Falha no envio: {e}")

def send_email(subject, recipients, html_body, text_body=None):
    """
    Dispara um e-mail em background (Thread).
    
    Args:
        subject (str): Assunto
        recipients (list): Lista de e-mails (strings)
        html_body (str): Conteúdo HTML
        text_body (str): Conteúdo Texto Puro (Opcional)
    """
    # Verifica configuração dummy
    mail_user = os.getenv('MAIL_USERNAME', '')
    if not mail_user or 'seu_email' in mail_user:
        print("⚠️  [EMAIL SIMULADO] Configuração SMTP ausente.")
        print(f"   Assunto: {subject}")
        print(f"   Para: {recipients}")
        return

    app = current_app._get_current_object()
    msg = Message(subject, recipients=recipients)
    msg.html = html_body
    msg.body = text_body or "Visualize este e-mail em formato HTML."
    
    # Sender Default
    sender = os.getenv('MAIL_DEFAULT_SENDER')
    if sender:
        msg.sender = sender

    # Threading para não bloquear request
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
