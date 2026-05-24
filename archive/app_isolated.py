"""
APP ISOLADO - GERAÇÃO DE RELATÓRIOS
===================================
Ambiente seguro para geração de relatórios financeiros sem impactar a produção.
Porta: 5001
"""

import os
from flask import Flask, render_template
from dotenv import load_dotenv

# Importar modelos existentes (sem modificar nada neles)
from models import db
from reports_isolated import reports_bp

# Carregar ambiente
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

app = Flask(__name__)

# Configuração de Banco (Mesma da Produção)
basedir = os.path.abspath(os.path.dirname(__file__))
db_url = os.getenv('DATABASE_URL')
if db_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
else:
    db_path = os.path.join(basedir, 'instance', 'gestao_editais_new.db')
    if os.name == 'nt':
        db_path = db_path.replace('\\', '/')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'chave-secreta-isolada-dev-mode'

# Inicializar DB
db.init_app(app)

# Registrar Filtro de Formatação
@app.template_filter('format_currency')
def format_currency(value):
    try:
        if not value: return "R$ 0,00"
        return f"R$ {float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "R$ 0,00"

# Registrar Blueprint de Relatórios
app.register_blueprint(reports_bp, url_prefix='/reports')

@app.route('/')
def index():
    """
    Dashboard do Ambiente Isolado
    Lista os links diretos para os relatórios para facilitar o teste.
    """
    from models import Edital, Bolsista, Residente
    
    # Buscar dados para listar (limitado a 20 para não poluir)
    editais = Edital.query.all()
    bolsistas = Bolsista.query.limit(50).all()
    residentes = Residente.query.limit(20).all()
    
    return render_template('isolated/dashboard.html', 
                           editais=editais, 
                           bolsistas=bolsistas, 
                           residentes=residentes)

if __name__ == '__main__':
    print(">>> Iniciando Ambiente Isolado na porta 5001...")
    print(">>> ACESSE: http://localhost:5001")
    app.run(port=5001, debug=True)
