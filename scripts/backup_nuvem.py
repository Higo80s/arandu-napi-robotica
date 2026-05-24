import os
import subprocess
import datetime
import zipfile
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from urllib.parse import urlparse

# Carregar variáveis do .env
load_dotenv()

# Configurações do Banco de Dados
DB_URL = os.getenv('DATABASE_URL')

# Configurações da Nuvem UTFPR
# Ex: https://nuvem.utfpr.edu.br/remote.php/dav/files/395170b0-6581-1040-9e93-17a32228ba8c/
CLOUD_BASE_URL = os.getenv('CLOUD_WEBDAV_URL')
CLOUD_USER = os.getenv('CLOUD_USER')
CLOUD_PASS = os.getenv('CLOUD_PASSWORD')

# Configurações de E-mail
MAIL_SERVER = os.getenv('MAIL_SERVER')
MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
MAIL_USER = os.getenv('MAIL_USERNAME')
MAIL_PASS = os.getenv('MAIL_PASSWORD')
MAIL_SENDER = os.getenv('MAIL_DEFAULT_SENDER')
DEST_EMAIL = os.getenv('NOTIFICATION_EMAIL')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKUP_LOCAL_DIR = os.path.join(PROJECT_ROOT, 'backups')

def enviar_email_confirmacao(assunto, corpo):
    if not MAIL_USER or not MAIL_PASS or not DEST_EMAIL:
        print("⚠️ Configurações de e-mail incompletas. Pulando notificação.")
        return

    try:
        msg = MIMEMultipart()
        msg['From'] = MAIL_SENDER
        msg['To'] = DEST_EMAIL
        msg['Subject'] = assunto
        msg.attach(MIMEText(corpo, 'plain'))

        server = smtplib.SMTP(MAIL_SERVER, MAIL_PORT)
        server.starttls()
        server.login(MAIL_USER, MAIL_PASS)
        server.send_message(msg)
        server.quit()
        print(f"📧 E-mail de confirmação enviado para {DEST_EMAIL}")
    except Exception as e:
        print(f"❌ Erro ao enviar e-mail: {e}")

def run_backup():
    if not CLOUD_BASE_URL or not CLOUD_USER or not CLOUD_PASS:
        print("❌ Erro: Credenciais da Nuvem não configuradas no .env")
        return

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    db_filename = f"napi_db_{file_timestamp}.sql"
    db_path = os.path.join(BACKUP_LOCAL_DIR, db_filename)
    zip_filename = f"arandu_backup_{file_timestamp}.zip"
    zip_path = os.path.join(BACKUP_LOCAL_DIR, zip_filename)

    logs = []
    success = False

    # 1. Gerar Dump do PostgreSQL
    try:
        parsed = urlparse(DB_URL)
        env = os.environ.copy()
        env['PGPASSWORD'] = parsed.password
        
        print(f"📦 Gerando dump do banco de dados...")
        pg_dump_path = r"C:\Program Files\PostgreSQL\17\bin\pg_dump.exe"
        
        cmd = [
            pg_dump_path,
            '-h', parsed.hostname or 'localhost',
            '-U', parsed.username,
            '-d', parsed.path.lstrip('/'),
            '-f', db_path
        ]
        
        subprocess.run(cmd, env=env, check=True)
        logs.append(f"[{timestamp}] ✅ Dump do banco gerado com sucesso.")
    except Exception as e:
        err_msg = f"[{timestamp}] ❌ ERRO ao gerar dump: {e}"
        print(err_msg)
        logs.append(err_msg)
        enviar_email_confirmacao("⚠️ FALHA NO BACKUP - Arandu NAPI", "\n".join(logs))
        return

    # 2. Criar ZIP
    try:
        print(f"🗜️ Criando arquivo ZIP...")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.write(db_path, db_filename)
            if os.path.exists(os.path.join(PROJECT_ROOT, 'requirements.txt')):
                zf.write(os.path.join(PROJECT_ROOT, 'requirements.txt'), 'requirements.txt')
        os.remove(db_path)
        logs.append(f"[{timestamp}] ✅ Arquivo ZIP compactado.")
    except Exception as e:
        err_msg = f"[{timestamp}] ❌ ERRO ao criar ZIP: {e}"
        print(err_msg)
        logs.append(err_msg)
        enviar_email_confirmacao("⚠️ FALHA NO BACKUP - Arandu NAPI", "\n".join(logs))
        return

    # 3. Upload WebDAV
    try:
        print(f"☁️ Enviando para a Nuvem UTFPR...")
        base_url = CLOUD_BASE_URL.rstrip('/') + '/'
        upload_url = f"{base_url}Backups_Arandu/{zip_filename}"
        
        # Tentar criar a pasta (MKCOL)
        requests.request('MKCOL', f"{base_url}Backups_Arandu/", auth=(CLOUD_USER, CLOUD_PASS))

        with open(zip_path, 'rb') as f:
            response = requests.put(upload_url, data=f, auth=(CLOUD_USER, CLOUD_PASS))
        
        if response.status_code in [201, 204]:
            print(f"🚀 BACKUP ENVIADO COM SUCESSO!")
            logs.append(f"[{timestamp}] 🚀 Backup enviado para Nuvem UTFPR com sucesso.")
            success = True
        else:
            logs.append(f"[{timestamp}] ❌ Erro no upload WebDAV: Status {response.status_code}")
    except Exception as e:
        logs.append(f"[{timestamp}] ❌ Erro na comunicação WebDAV: {e}")

    # Notificação Final
    if success:
        corpo = f"Olá,\n\nO backup automático do sistema Arandu NAPI-Robótica foi concluído com sucesso.\n\n"
        corpo += f"Arquivo: {zip_filename}\n"
        corpo += f"Data/Hora: {timestamp}\n"
        corpo += f"Local: Nuvem UTFPR / Backups_Arandu\n\nDetalhes:\n" + "\n".join(logs)
        enviar_email_confirmacao("✅ Backup Concluído - Arandu NAPI", corpo)
    else:
        enviar_email_confirmacao("⚠️ FALHA NO BACKUP - Arandu NAPI", "\n".join(logs))

if __name__ == "__main__":
    run_backup()
