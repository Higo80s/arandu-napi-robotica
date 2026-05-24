"""
Development Server - Gestão de Editais
Starts Flask in debug mode with full error reporting
"""
from app import app, db
import webbrowser
import threading
import time

def open_browser():
    """Open browser after waiting for server to start"""
    time.sleep(2)
    print("Tentando abrir o navegador...")
    webbrowser.open('http://127.0.0.1:5003/bolsistas')

if __name__ == '__main__':
    print("=" * 60)
    print("Gestão de Editais - Servidor de Desenvolvimento")
    print("=" * 60)
    print(f"Banco de Dados: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print("Servidor rodando em: http://127.0.0.1:5003")
    print("=" * 60)
    
    # Initialize database
    with app.app_context():
        db.create_all()
        print("Banco de dados inicializado.")
    
    # Schedule browser open
    threading.Thread(target=open_browser, daemon=True).start()

    # Start Flask development server
    app.run(
        debug=True,
        host='127.0.0.1',
        port=5003,
        use_reloader=False  # Disable reloader to avoid double initialization
    )
