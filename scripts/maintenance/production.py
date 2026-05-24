"""
SERVIDOR DE PRODUÇÃO (WAITRESS)
===============================

Este script inicia o servidor de aplicação WSGI (Waitress) para uso em produção.
Diferente do servidor de desenvolvimento do Flask, o Waitress é robusto, seguro e suporta múltiplas threads.

Fluxo:
1. Verifica/Cria tabelas do banco de dados na inicialização.
2. Inicia uma thread separada para abrir o navegador automaticamente.
3. Inicia o servidor Waitress na porta 5002 (Host 127.0.0.1).
"""

from waitress import serve
from dotenv import load_dotenv
import os
import webbrowser
import time
import threading
import sys
import logging

# Carregar variáveis de ambiente antes de importar app
load_dotenv()

from app import app, db
print("APP LOADED FROM:", app)
print("ROUTES:", app.url_map)

# Enable exception logging
app.config['PROPAGATE_EXCEPTIONS'] = True

# Configura logging basico para stdout (que vai para o arquivo .log)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('waitress')
logger.setLevel(logging.INFO)

def open_browser():
    """Open browser IMMEDIATELY with local splash screen"""
    try:
        # Get absolute path to the local splash loader
        base_dir = os.path.dirname(os.path.abspath(__file__))
        splash_path = os.path.join(base_dir, 'splash_loader.html')
        
        url = f'file:///{splash_path}'
        logging.info(f"Abrindo Splash Screen Imediata: {url}")
        
        # Open immediately (no sleep)
        webbrowser.open(url)
    except Exception as e:
        logging.error(f"Erro ao abrir navegador: {e}")

if __name__ == '__main__':
    try:
        # Open browser in background thread IMMEDIATELY
        threading.Thread(target=open_browser, daemon=True).start()

        # Initialize database using Flask-SQLAlchemy
        with app.app_context():
            db.create_all()
            logging.info("Banco de dados verificado/criado.")
        

        
        # Start production server
        print("=" * 60)
        print("Gestão de Editais - Servidor de Produção")
        print("=" * 60)
        print("Servidor rodando em: http://127.0.0.1:5003")
        print("Consulte startup.log para detalhes.")
        print("=" * 60)
        
        logging.info("Iniciando servidor Waitress na porta 5003...")
        serve(app, host='127.0.0.1', port=5003, threads=1, expose_tracebacks=True)
        
    except Exception as e:
        logging.critical(f"ERRO FATAL ao iniciar servidor: {e}")
        # Re-raise para aparecer no stderr também
        raise e
