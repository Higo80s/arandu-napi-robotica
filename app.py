"""
GESTÃO DE EDITAIS - SISTEMA ARANDÚ NAPI-ROBÓTICA (V11.1)
=============================================================
DescriÃ§Ã£o:
    Sistema web desenvolvido em Flask para gerenciamento de Editais, Modalidades e Bolsistas.
    Refatorado para arquitetura modular (Blueprints) em Março de 2026.
"""

import os
import matplotlib
matplotlib.use('Agg') # Fix for Waitress/Threaded Context

from datetime import datetime, date, timedelta
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_cors import CORS
from dotenv import load_dotenv

# Importações do Próprio Projeto
from extensions import db, mail, login_manager, csrf, migrate
from flask_wtf.csrf import CSRFError
from models import Edital, Modalidade, Campus, ProgramaAcademico, Bolsista, User, Residente, UIState
from utils import format_date_br, format_date_iso

# Carregar variÃ¡veis de ambiente
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

app = Flask(__name__)
CORS(app)

# Configuração do Banco de Dados
db_url = os.getenv('DATABASE_URL')
# Em modo de teste (pytest), permitimos fallback ou SQLite in-memory
is_testing = os.getenv('FLASK_ENV') == 'testing' or 'pytest' in os.environ.get('_', '')

if not db_url and not is_testing:
    print(" [FATAL] DATABASE_URL não configurada. O Arandú Napi-Robótica exige PostgreSQL para Produção.")
    exit(1)

if db_url:
    is_local = any(host in db_url for host in ['localhost', '127.0.0.1'])
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "connect_args": {"sslmode": "require"} if not is_local else {}
    }
elif is_testing:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {}

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', os.urandom(24))
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=4)
app.config['WTF_CSRF_TIME_LIMIT'] = None

# Inicializar extensões
db.init_app(app)
migrate.init_app(app, db)
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
mail.init_app(app)
csrf.init_app(app)

# Login Manager
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_request
def require_login():
    allowed_endpoints = ['auth.login', 'static', 'reports_bp.static_files', 'splash'] 
    if not current_user.is_authenticated and \
       request.endpoint and \
       request.endpoint not in allowed_endpoints and \
       not request.endpoint.startswith('static'):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
             return jsonify({'error': 'Login required', 'redirect': url_for('auth.login')}), 401
        # [REBIRTH] Fluxo Neon: Splash -> Login
        return redirect(url_for('splash', next=request.url))

@login_manager.unauthorized_handler
def unauthorized():
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'error': 'Login required', 'redirect': url_for('auth.login')}), 401
    return redirect(url_for('auth.login', next=request.url))

# Erro CSRF
@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'error': 'CSRF Error', 'message': 'Sessão expirada. Recarregue a página.', 'redirect': url_for('auth.login')}), 401
    if request.method == 'POST':
        return render_template('errors/csrf_retry.html', request_url=request.url, form_data=request.form), 400
    flash('Sua sessão expirou por inatividade. Faça login novamente.', 'warning')
    return redirect(url_for('auth.login', next=request.url))

# Registro de Blueprints
from reports_bp import reports_bp
from dashboard_bp import dashboard_bp
from blueprints.auth import auth_bp
from blueprints.proap import proap_bp
from blueprints.internacionalizacao import inter_bp
from blueprints.api_utils import api_utils_bp
from blueprints.api_v1 import api_v1_bp
from blueprints.admin import admin_bp
from blueprints.editais import editais_bp
from blueprints.bolsistas import bolsistas_bp
from blueprints.admin_users import admin_users_bp
from blueprints.ui_editor import ui_editor_bp
from blueprints.database_explorer import database_explorer_bp

app.register_blueprint(reports_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(proap_bp)
app.register_blueprint(inter_bp)
app.register_blueprint(api_utils_bp)
app.register_blueprint(api_v1_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(editais_bp)
app.register_blueprint(bolsistas_bp)
app.register_blueprint(admin_users_bp)
app.register_blueprint(ui_editor_bp)
app.register_blueprint(database_explorer_bp)

# Filtros Jinja2
@app.template_filter('format_currency')
def format_currency_filter(value):
    try:
        if value is None: return "0,00"
        return f"{float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except: return "0,00"

@app.template_filter('date_br')
def date_br_filter(date_obj): return format_date_br(date_obj)

@app.template_filter('date_iso')
def date_iso_filter(date_obj): return format_date_iso(date_obj)

# Globais Jinja2
app.jinja_env.globals.update(getattr=getattr)

# Rotas de Nível Superior
from flask_login import current_user

@app.route('/')
def index():
    """
    Landing Page / Dashboard Admin Central
    """
    if current_user.is_authenticated:
        if current_user.role == 'master': return redirect(url_for('dashboard.master'))
        if current_user.role == 'coordenador_programa': return redirect(url_for('dashboard.coordenacao'))
        if current_user.role == 'diretor_campus': return redirect(url_for('dashboard.direcao'))

@app.route('/splash')
def splash():
    """Rota gerenciada pelo Flask para o Splash Screen Neon."""
    from models import UIState
    # Verifica o estado da UI para carregar textos dinâmicos (Fase Rebirth)
    try:
        ui_records = UIState.query.filter_by(page_context='splash').all()
        ui_context = {rec.element_key: rec.current_text for rec in ui_records}
    except:
        ui_context = {}
    return render_template('splash.html', ui=ui_context)
    
    from sqlalchemy import func, or_, not_
    
    # [V11.2] Queries otimizadas via Singleton DB
    total_programas = db.session.query(func.count(func.distinct(ProgramaAcademico.codigo_programa))).filter(not_(ProgramaAcademico.nome_programa.ilike('%*%'))).scalar()
    total_vagas_ofertadas = db.session.query(func.sum(Modalidade.vagas)).join(Edital).filter(Edital.prestacao_contas == False).filter(or_(Edital.data_fim >= date.today(), Edital.data_fim == None)).scalar()
    
    marco_zero = date.today().replace(day=1)
    pendencias_count = Bolsista.query.filter(Bolsista.ativo == True, Bolsista.data_fim_bolsa < marco_zero).count()
    impacto_financeiro = db.session.query(func.sum(Modalidade.valor_mensal)).join(Bolsista, Modalidade.id == Bolsista.modalidade_id).filter(Bolsista.ativo == True, Bolsista.data_fim_bolsa < marco_zero).scalar() or 0.0

    stats = {
        'total_programas': total_programas,
        'total_discentes': Bolsista.query.filter_by(ativo=True).count(),
        'total_campi': Campus.query.filter(Campus.sigla_campus != 'MULTI').count(),
        'total_editais': Edital.query.filter(Edital.prestacao_contas == False).filter(or_(Edital.data_fim >= date.today(), Edital.data_fim == None)).count(),
        'total_vagas': int(total_vagas_ofertadas) if total_vagas_ofertadas else 0,
        'pendencias_criticas': pendencias_count,
        'impacto_financeiro': impacto_financeiro
    }
    return render_template('dashboard.html', **stats)

# Context Processors Globais
@app.context_processor
def inject_ui_texts():
    """
    Injeta o dicionário 'ui' com todos os textos editáveis da tabela UIState.
    Implementa Graceful Degradation conforme recomendação (Yoko/Higo).
    """
    try:
        ui_records = UIState.query.all()
        ui_dict = {rec.element_key: rec.current_text for rec in ui_records}
        
        # Helper interno para facilitar o acesso no Jinja2: {{ ui.get('chave', 'default') }}
        # Se quiser usar {{ ui.chave }}, precisaria transformar em um objeto ou similar.
        # Por enquanto, retornamos o dict para uso padrão .get()
        return dict(ui=ui_dict)
    except Exception as e:
        print(f" [ERRO] Falha ao injetar textos da UI: {e}")
        return dict(ui={})

@app.context_processor
def inject_alerts():
    from datetime import date, timedelta
    import calendar
    hoje = date.today()
    proximos_30_dias = hoje + timedelta(days=30)
    ultimo_dia_mes = calendar.monthrange(hoje.year, hoje.month)[1]
    fim_mes = date(hoje.year, hoje.month, ultimo_dia_mes)

    try:
        count_expiring = Edital.query.filter(Edital.data_fim >= hoje, Edital.data_fim <= proximos_30_dias).count()
        count_pending = Edital.query.filter(Edital.data_fim < hoje, Edital.prestacao_contas == False).count()
        count_bolsistas = Bolsista.query.filter(Bolsista.data_fim_bolsa >= hoje, Bolsista.data_fim_bolsa <= fim_mes, Bolsista.ativo == True).count()
        count_titulacao = Bolsista.query.filter(Bolsista.ativo == True, Bolsista.previsao_defesa != None, Bolsista.previsao_defesa < hoje, Bolsista.data_fim_bolsa >= hoje).count()
        total_alerts = count_expiring + count_pending + count_bolsistas + count_titulacao
        return dict(total_alerts=total_alerts, count_titulacao_antecipada=count_titulacao)
    except: return dict(total_alerts=0)

@app.context_processor
def inject_director_programs():
    if current_user.is_authenticated and current_user.role == 'diretor_campus' and current_user.campus_id:
        from sqlalchemy import not_
        programs = ProgramaAcademico.query.filter(ProgramaAcademico.campus_id == current_user.campus_id, not_(ProgramaAcademico.nome_programa.ilike('%*%'))).order_by(ProgramaAcademico.nome_programa).all()
        return dict(director_programs=programs)
    return dict(director_programs=[])

# CLI Tasks
from tasks.cobranca_cancelamento import init_app_tasks
init_app_tasks(app)

if __name__ == '__main__':
    with app.app_context():
        import time
        from sqlalchemy.exc import OperationalError
        print("\n [ARANDÚ] Iniciando verificações de banco de dados...")
        max_retries = 10
        for i in range(max_retries):
            try:
                # Testa ativamente a conexão executando uma query crua
                db.session.execute(db.text('SELECT 1'))
                db.create_all()
                print(" [ARANDÚ] Banco de dados conectado com sucesso!")
                break
            except OperationalError as e:
                print(f" [AVISO] Banco de Dados (PostgreSQL) ainda não está pronto. Tentativa {i+1}/{max_retries}. Aguardando 3 segundos...")
                time.sleep(3)
        else:
            print(" [FATAL] O PostgreSQL não respondeu após várias tentativas. Verifique o serviço do Windows.")
            # Não vai matar a execução abruptamente caso seja apenas sobrecarga.
            
    app.run(debug=True, port=5005)
