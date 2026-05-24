"""
GESTÃO DE EDITAIS - SISTEMA DE GERENCIAMENTO DE BOLSAS (V6.2)
=============================================================

Descrição:
    Sistema web desenvolvido em Flask para gerenciamento de Editais, Modalidades e Bolsistas.
    Permite o controle financeiro, acompanhamento de vigências e geração de relatórios.
    
    Principais Funcionalidades:
    - Cadastro de Editais e Modalidades de Bolsa.
    - Gestão de Bolsistas (Vínculo, Dados Bancários, Acadêmicos).
    - Cálculo automático de vigências e datas limite.
    - Controle de Afastamentos (Maternidade, Saúde) com ajuste automático de prazos.
    - Relatórios e Dashboard Financeiro.

Tecnologias:
    - Backend: Python 3.x + Flask (Framework Web)
    - Database: SQLite + SQLAlchemy (ORM)
    - Frontend: HTML5, CSS3, JavaScript (Vanilla)
    - Deploy: Waitress (Servidor de Produção)

Arquitetura:
    - MVC: Model (models.py), View (templates/), Controller (app.py - Rotas)
    - Normalização V5: Uso de tabelas Campus e ProgramaAcademico para integridade.

Histórico de Versões:
    - V5: Normalização de Banco de Dados.
    - V6.0: Inclusão do "Número do Formulário" e melhoria nos filtros.
    - V6.2: Módulo de Certificados, Campos Pós-Doc e Atualização do Dashboard.
    - V7.0: Refatoração de Arquitetura (Tabela 'residentes' separada para Pós-Doc).

Autor: 
    Equipe de Desenvolvimento (Assistente IA)
    Data: Dezembro 2025
"""

# Importações Bibliotecas Padrão (Python)
import os                       # Manipulação de arquivos e sistema operacional
import csv                      # Leitura/Escrita de arquivos CSV
import io                       # Manipulação de streams de dados (para downloads)
from datetime import datetime, date # Manipulação de datas

# Importações de Bibliotecas de Terceiros
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, send_from_directory
from dateutil.relativedelta import relativedelta # Cálculos avançados de data (ex: +1 mês)
from dotenv import load_dotenv                   # Carregar variáveis de ambiente (.env)

# Importações do Próprio Projeto
from models import db, Edital, Modalidade, Campus, ProgramaAcademico, Bolsista, Afastamento, Acompanhamento, Residente, Campus, ProgramaAcademico
import backup_system                             # Módulo de backup automático

# Carregar variáveis de ambiente (Segurança: Senhas e Chaves não ficam no código)
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

app = Flask(__name__)

# Configuração do Banco de Dados
basedir = os.path.abspath(os.path.dirname(__file__))

# Lógica Dual: Docker (Postgres) vs Local (SQLite)
# Se a variável de ambiente DATABASE_URL existir, usamos ela.
# Caso contrário, usamos o SQLite local padrão.
db_url = os.getenv('DATABASE_URL')

if db_url:
    # Docker/Produção (Postgres)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    print(f" * Usando Banco de Dados: PostgreSQL (Produção)")
else:
    # Local/Desenvolvimento (SQLite)
    db_path = os.path.join(basedir, 'instance', 'test_termination.db')
    if os.name == 'nt':
        db_path = db_path.replace('\\', '/')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
    print(f" * Usando Banco de Dados: SQLite (TESTE: {db_path})")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Chave Secreta para Sessão (Flash messages, Login)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', os.urandom(24))

# Inicializar o Banco de Dados com o App
db.init_app(app)




@app.route('/')
def index():
    return render_template('dashboard.html')

# === EDITAIS ===
@app.route('/editais')
def editais_index():
    editais = Edital.query.all()
    return render_template('editais/index.html', editais=editais)

@app.route('/editais/novo', methods=['GET', 'POST'])
def editais_novo():
    if request.method == 'POST':
        novo_edital = Edital(
            numero=request.form['numero'],
            descricao=request.form['descricao'],
            agencia=request.form['agencia'],
            codigo_projeto=request.form['codigo_projeto'],
            descricao_projeto=request.form['descricao_projeto'],
            processo_sei=request.form['processo_sei'], # [NEW] V2
            comentarios=request.form['comentarios'], # [NEW] V2
            # [NEW V11.2 - Prod]
            data_inicio=datetime.strptime(request.form['data_inicio'], '%Y-%m-%d').date() if request.form.get('data_inicio') else None,
            data_fim=datetime.strptime(request.form['data_fim'], '%Y-%m-%d').date() if request.form.get('data_fim') else None,
            
            # [NEW V11.3 - Prod]
            prestacao_contas=True if request.form.get('prestacao_contas') else False
        )
        db.session.add(novo_edital)
        db.session.commit()
        flash('Edital criado com sucesso!', 'success')
        return redirect(url_for('editais_index'))
    return render_template('editais/form.html', edital=None)

@app.route('/editais/<int:id>/editar', methods=['GET', 'POST'])
def editais_editar(id):
    edital = Edital.query.get_or_404(id)
    if request.method == 'POST':
        edital.numero = request.form['numero']
        edital.descricao = request.form['descricao']
        edital.agencia = request.form['agencia']
        edital.codigo_projeto = request.form['codigo_projeto']
        edital.descricao_projeto = request.form['descricao_projeto']
        edital.processo_sei = request.form['processo_sei'] # [NEW] V2
        edital.comentarios = request.form['comentarios'] # [NEW] V2
        
        # [NEW V11.2 - Prod]
        d_inicio = request.form.get('data_inicio')
        d_fim = request.form.get('data_fim')
        edital.data_inicio = datetime.strptime(d_inicio, '%Y-%m-%d').date() if d_inicio else None
        edital.data_fim = datetime.strptime(d_fim, '%Y-%m-%d').date() if d_fim else None
        
        # [NEW V11.3 - Prod]
        edital.prestacao_contas = True if request.form.get('prestacao_contas') else False
        
        db.session.commit()
        flash('Edital atualizado com sucesso!', 'success')
        return redirect(url_for('editais_index'))
    return render_template('editais/form.html', edital=edital)

@app.route('/editais/<int:id>/excluir', methods=['POST'])
def editais_excluir(id):
    edital = Edital.query.get_or_404(id)
    db.session.delete(edital)
    db.session.commit()
    flash('Edital excluído com sucesso!', 'success')
    return redirect(url_for('editais_index'))

# === MODALIDADES ===
import re

# Helper to clean currency
def clean_currency(val):
    if not val: return 0.0
    # Remove everything except digits and comma
    # 1.875,00 -> 1875,00
    # R$ 1.200,00 -> 1200,00
    cleaned = re.sub(r'[^\d,]', '', val)
    # Replace comma with dot
    return float(cleaned.replace(',', '.'))

@app.route('/editais/<int:id>/modalidades', methods=['GET', 'POST'])
def modalidades_gerenciar(id):
    edital = Edital.query.get_or_404(id)
    if request.method == 'POST':
        try:
            nova_mod = Modalidade(
                edital_id=edital.id,
                nivel=request.form['nivel'],
                vagas=int(request.form['vagas']),
                valor_mensal=clean_currency(request.form['valor_mensal']),
                max_meses=int(request.form['max_meses']) if request.form.get('max_meses') else None # [NEW] V2
            )
            db.session.add(nova_mod)
            db.session.commit()
            flash('Modalidade adicionada!', 'success')
            return redirect(url_for('modalidades_gerenciar', id=id))
        except Exception as e:
            app.logger.error(f"Erro ao adicionar modalidade: {e}")
            flash(f'Erro ao adicionar modalidade: {e}', 'danger')
            return redirect(url_for('modalidades_gerenciar', id=id))
    

    
    # [NEW V11.1] Dashboard Logic
    from datetime import date
    today = date.today()
    
    stats = {
        'total_vagas': 0,
        'total_ocupado': 0,
        'by_level': {}
    }
    
    for mod in edital.modalidades:
        # Count active bolsistas
        occupied = 0
        for b in mod.bolsistas:
            if b.check_status_validity() == 'ATIVO':
                occupied += 1
                
        # Aggregate Global
        stats['total_vagas'] += mod.vagas
        stats['total_ocupado'] += occupied
        
        # Aggregate by Level
        lvl = mod.nivel
        if lvl not in stats['by_level']:
            stats['by_level'][lvl] = {'vagas': 0, 'ocupado': 0, 'saldo': 0}
            
        stats['by_level'][lvl]['vagas'] += mod.vagas
        stats['by_level'][lvl]['ocupado'] += occupied
        stats['by_level'][lvl]['saldo'] = stats['by_level'][lvl]['vagas'] - stats['by_level'][lvl]['ocupado']

    return render_template('editais/modalidades.html', edital=edital, stats=stats)

@app.route('/modalidades/<int:id>/editar', methods=['GET', 'POST'])
def modalidades_editar(id):
    mod = Modalidade.query.get_or_404(id)
    edital_id = mod.edital_id
    
    if request.method == 'POST':
        mod.nivel = request.form['nivel']
        mod.vagas = int(request.form['vagas'])
        mod.valor_mensal = clean_currency(request.form['valor_mensal'])
        mod.max_meses = int(request.form['max_meses']) if request.form.get('max_meses') else None
        db.session.commit()
        flash('Modalidade atualizada!', 'success')
        return redirect(url_for('modalidades_gerenciar', id=edital_id))
    
    edital = Edital.query.get_or_404(edital_id)
    return render_template('editais/modalidades.html', edital=edital, modalidade_edit=mod)

@app.route('/modalidades/<int:id>/excluir', methods=['POST'])
def modalidades_excluir(id):
    mod = Modalidade.query.get_or_404(id)
    edital_id = mod.edital_id
    db.session.delete(mod)
    db.session.commit()
    flash('Modalidade removida!', 'success')
    return redirect(url_for('modalidades_gerenciar', id=edital_id))

# === HELPER: CRIAÇÃO/EDIÇÃO CENTRALIZADA ===
def bolsistas_action(action, id=None, is_posdoc=False):
    """
    Função auxiliar para salvar/editar bolsistas e residentes.
    Centraliza validação e persistência.
    """
    if action == 'editar' and id:
        bolsista = Bolsista.query.get_or_404(id)
    else:
        bolsista = Bolsista()
    
    # Coleta de Dados do Formulário
    try:
        # Campos Comuns
        bolsista.nome = request.form.get('nome')
        bolsista.cpf = request.form.get('cpf')
        bolsista.email = request.form.get('email')
        bolsista.banco = request.form.get('banco')
        bolsista.agencia = request.form.get('agencia')
        bolsista.conta = request.form.get('conta')
        
        # Campos de Vinculação
        bolsista.edital_id = request.form.get('edital_id')
        bolsista.modalidade_id = request.form.get('modalidade_id')
        bolsista.programa_id = request.form.get('programa_id')
        
        # Campos Pós-Doc Específicos (mas mapeados para o modelo Bolsista)
        bolsista.orientador = request.form.get('orientador') # Supervisor
        bolsista.projeto_pesquisa = request.form.get('projeto_pesquisa')
        bolsista.agencia_fomento = request.form.get('agencia_fomento')
        bolsista.processo_sei = request.form.get('processo_sei')
        bolsista.numero_formulario = request.form.get('numero_formulario')
        
        # Booleans
        recebe_bolsa = request.form.get('recebe_bolsa')
        bolsista.recebe_bolsa = True if recebe_bolsa == '1' else False
        
        bolsista.ativo = True # Default
        
        # Datas e Prazos
        dt_inicio = request.form.get('data_inicio_bolsa')
        dt_fim = request.form.get('data_fim_bolsa')
        duracao = request.form.get('meses_duracao')
        
        if dt_inicio:
            bolsista.data_inicio_bolsa = datetime.strptime(dt_inicio, '%Y-%m-%d').date()
            if not request.form.get('data_inicio_curso'):
                bolsista.data_inicio_curso = bolsista.data_inicio_bolsa
            else:
                bolsista.data_inicio_curso = datetime.strptime(request.form.get('data_inicio_curso'), '%Y-%m-%d').date()
        
        if dt_fim:
            bolsista.data_fim_bolsa = datetime.strptime(dt_fim, '%Y-%m-%d').date()
            bolsista.previsao_defesa = bolsista.data_fim_bolsa 
        
        if duracao:
            bolsista.meses_duracao = int(duracao)

        # Persistência
        if action == 'novo':
            db.session.add(bolsista)
            flash('Registro criado com sucesso!', 'success')
        else:
            flash('Registro atualizado com sucesso!', 'success')
            
        db.session.commit()
        
        if is_posdoc:
            return redirect(url_for('posdoc_index'))
        return redirect(url_for('bolsistas_index'))

    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao salvar: {str(e)}', 'error')
        if is_posdoc:
            return redirect(url_for('posdoc_novo' if action == 'novo' else 'posdoc_editar', id=id))
        return redirect(url_for('bolsistas_novo' if action == 'novo' else 'bolsistas_editar', id=id))

def residentes_action(action, id=None):
    """
    Função auxiliar para salvar/editar RESIDENTES (Pós-Doc).
    Isolada de Bolsistas para garantir integridade e campos específicos.
    """
    if action == 'editar' and id:
        residente = Residente.query.get_or_404(id)
    else:
        residente = Residente()
    
    try:
        # Campos Pessoais
        residente.nome = request.form.get('nome')
        residente.cpf = request.form.get('cpf')
        residente.email = request.form.get('email')
        
        # Vinculação (Nullable/FK)
        residente.edital_id = request.form.get('edital_id')
        residente.modalidade_id = request.form.get('modalidade_id')
        residente.programa_id = request.form.get('programa_id')
        
        # Pós-Doc Específicos
        residente.supervisor = request.form.get('orientador') # Form usa 'orientador'
        residente.projeto_pesquisa = request.form.get('projeto_pesquisa')
        residente.agencia_fomento = request.form.get('agencia_fomento')
        if not residente.agencia_fomento and residente.edital:
             residente.agencia_fomento = residente.edital.agencia
             
        residente.recebe_bolsa = (request.form.get('recebe_bolsa') == '1')
        residente.processo_sei = request.form.get('processo_sei')
        residente.numero_formulario = request.form.get('numero_formulario')
        
        # Datas
        dt_inicio = request.form.get('data_inicio_bolsa')
        dt_fim = request.form.get('data_fim_bolsa')
        duracao = request.form.get('meses_duracao')
        
        if dt_inicio:
            residente.data_inicio = datetime.strptime(dt_inicio, '%Y-%m-%d').date()
        if dt_fim:
            residente.data_fim = datetime.strptime(dt_fim, '%Y-%m-%d').date()
        if duracao:
            residente.meses_duracao = int(duracao)
            
        residente.ativo = (request.form.get('ativo') == 'on')

        # Persistência
        if action == 'novo':
            db.session.add(residente)
            flash('Residente cadastrado com sucesso!', 'success')
        else:
            flash('Residente atualizado com sucesso!', 'success')
            
        db.session.commit()
        return redirect(url_for('posdoc_index'))

    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao salvar residente: {str(e)}', 'error')
        if action == 'novo':
            return redirect(url_for('posdoc_novo'))
        return redirect(url_for('posdoc_editar', id=id))

# === BOLSISTAS ===
@app.route('/bolsistas')
def bolsistas_index():
    edital_id = request.args.get('edital_id', type=int)
    search_q = request.args.get('q', '').strip()
    
    editais = Edital.query.all()
    
    query = Bolsista.query
    if edital_id:
        query = query.filter_by(edital_id=edital_id)
        
    if search_q:
        # Importação local para otimização (Lazy Import)
        from sqlalchemy import or_
        term = f"%{search_q}%"
        
        # Filtros de Busca Textual (Case Insensitive)
        # O operador 'ilike' busca por trechos de texto ignorando maiúsculas/minúsculas.
        conditions = [
            Bolsista.nome.ilike(term),
            Bolsista.cpf.ilike(term),
            Bolsista.programa.ilike(term), # Compatibilidade com registros antigos (Legado)
            Bolsista.email.ilike(term),
            Bolsista.orientador.ilike(term),
            Bolsista.processo_sei.ilike(term),     # [Novo V2] Busca pelo SEI
            Bolsista.numero_formulario.ilike(term) # [Novo V6] Busca pelo Formulário
        ]
        
        # [AVANÇADO] Busca em Tabelas Relacionadas (V5)
        # O método `.has()` permite filtrar bolsistas baseado em campos de tabelas filhas (JOIN automático).
        # Ex: Buscar "Mecânica" encontra bolsistas do "Programa de Engenharia Mecânica".
        conditions.append(Bolsista.programa_link.has(ProgramaAcademico.nome_programa.ilike(term)))
        conditions.append(Bolsista.programa_link.has(ProgramaAcademico.sigla_programa.ilike(term)))
        conditions.append(Bolsista.programa_link.has(ProgramaAcademico.codigo_programa.ilike(term)))
        
        # Combina todas as condições com OR (basta satisfazer uma delas)
        # Combina todas as condições com OR (basta satisfazer uma delas)
        query = query.filter(or_(*conditions))

    # [CHANGE V6.3] Exclude Pós-Doutorado from this main list (Discentes)
    # Replaced simple filter with explicit NOT OR logic to ensure SQLite compatibility
    # and correct handling of duplicates.
    from sqlalchemy import not_, or_
    query = query.join(Modalidade).filter(
        not_(or_(
            Modalidade.nivel.ilike('%PÓS%'),
            Modalidade.nivel.ilike('%Pós%'),
            Modalidade.nivel.ilike('%RESID%'), 
            Modalidade.nivel.ilike('%POS%')
        ))
    )
        
    bolsistas = query.all()

    # --- Sorting/Filtering Logic ---
    sort_by = request.args.get('sort', 'nome') # Default to name
    order = request.args.get('order', 'asc')
    
    # Store original count before filtering
    total_before_filter = len(bolsistas)
    
    if sort_by == 'status':
        # FILTER by status (not just sort)
        if order == 'ativo':
            bolsistas = [b for b in bolsistas if b.check_status_validity() == 'ATIVO']
        elif order == 'inativo':
            bolsistas = [b for b in bolsistas if b.check_status_validity() == 'INATIVO']
        elif order == 'finalizando':
            bolsistas = [b for b in bolsistas if b.check_status_validity() == 'FINALIZANDO']
        # else: show all (no filter)
        
        # Sort filtered results by name
        bolsistas = sorted(bolsistas, key=lambda b: b.nome)

    elif sort_by == 'nivel':
        # Nivel Sorting (keep as sort, alphabetically)
        def nivel_key(b):
            n = (b.modalidade.nivel if b.modalidade else "").upper()
            return (n, b.nome)
        
        reverse = (order == 'desc')
        bolsistas = sorted(bolsistas, key=nivel_key, reverse=reverse)
    
    elif sort_by == 'nome':
         bolsistas = sorted(bolsistas, key=lambda b: b.nome, reverse=(order=='desc'))


    # Calculate Totals
    total_registros = len(bolsistas)
    
    total_ativos = 0
    total_finalizando = 0
    total_inativos = 0
    
    for b in bolsistas:
        status = b.check_status_validity()
        if status == 'ATIVO':
            total_ativos += 1
        elif status == 'FINALIZANDO':
            total_finalizando += 1
        else: # INATIVO
            total_inativos += 1
    
    # Calculate Levels (Case insensitive partial match)
    # Calculate Levels (Case insensitive partial match)
    total_graduacao = sum(1 for b in bolsistas if b.modalidade and 'GRADUA' in b.modalidade.nivel.upper())
    total_mestrado = sum(1 for b in bolsistas if b.modalidade and ('MESTR' in b.modalidade.nivel.upper() or 'MASTER' in b.modalidade.nivel.upper()))
    
    # Pos-Doc (Explicit check first)
    total_posdoc = sum(1 for b in bolsistas if b.modalidade and ('PÓS' in b.modalidade.nivel.upper() or 'RESID' in b.modalidade.nivel.upper()))
    
    # Doutorado (Exclude Pós-Doc to avoid double counting if names overlap, though usually they don't)
    # Looking for 'DOUTOR' but NOT 'PÓS'
    # [DOC V6.2] Ensures Pós-Doc students aren't counted as PhD students
    total_doutorado = sum(1 for b in bolsistas if b.modalidade and 
                          ('DOUTOR' in b.modalidade.nivel.upper() or 'DOCTOR' in b.modalidade.nivel.upper()) and 
                          not ('PÓS' in b.modalidade.nivel.upper()))

    return render_template('bolsistas/index.html', bolsistas=bolsistas, editais=editais, selected_edital=edital_id,
                           search_q=search_q, total_registros=total_registros,
                           total_ativos=total_ativos, total_finalizando=total_finalizando, total_inativos=total_inativos,
                           total_graduacao=total_graduacao, total_mestrado=total_mestrado, total_doutorado=total_doutorado,
                           total_posdoc=total_posdoc, # [NEW V6.2] Pos-Doc Summary
                           current_sort=sort_by, current_order=order, # Pass sort state
                           total_before_filter=total_before_filter) # For filter counter

# Validating / Mapping Sigla
CAMPUS_SIGLA_MAPPING = {
    'Apucarana': 'AP', 'Campo Mourão': 'CM', 'Cornélio Procópio': 'CP', 'Curitiba': 'CT',
    'Dois Vizinhos': 'DV', 'Francisco Beltrão': 'FB', 'Guarapuava': 'GP', 'Londrina': 'LD',
    'Medianeira': 'MD', 'Pato Branco': 'PB', 'Ponta Grossa': 'PG', 'Santa Helena': 'SH', 'Toledo': 'TD'
}

def get_sigla(campus_nome):
    if not campus_nome: return None
    return CAMPUS_SIGLA_MAPPING.get(campus_nome, campus_nome[:2].upper())

@app.route('/bolsistas/novo', methods=['GET', 'POST'])
def bolsistas_novo():
    editais = Edital.query.all()
    # [NEW] V5: Fetch Lists for Dropdowns
    campuses = Campus.query.order_by(Campus.nome).all()
    programas = ProgramaAcademico.query.order_by(ProgramaAcademico.nome_programa).all()

    if request.method == 'POST':
        modalidade_id = int(request.form['modalidade_id'])
        mod = Modalidade.query.get(modalidade_id)
        


        # --- VALIDAÇÃO E CÁLCULO DE PRAZOS (REGRA DE NEGÓCIO) ---
        # Esta seção garante que as regras da agência de fomento sejam cumpridas.
        #
        # Variáveis Principais:
        #   IC: Data de Início do Curso (Matrícula)
        #   IB: Data de Início da Bolsa (Vigência Inicial)
        #   D:  Duração (Quantidade de mensalidades a pagar)
        #   M:  Máximo da Modalidade (ex: 24 meses para Mestrado)
        
        try:
            # Converte as strings do formulário para objetos Date do Python
            form_IC = datetime.strptime(request.form['data_inicio_curso'], '%Y-%m-%d').date() if request.form['data_inicio_curso'] else None
            form_IB = datetime.strptime(request.form['data_inicio_bolsa'], '%Y-%m-%d').date()
            form_D = int(request.form['meses_duracao'])
            form_M = mod.max_meses if mod.max_meses else 0
            
            # [ADJUSTMENT - V6] Decoupling Academic Limit (Rule 5) from Payment Limit (Rule 6)
            # Rule 6 uses form_M (Max payments defined in Modalidade).
            # Rule 5 uses academic_limit_months (Defined by Level).
            
            academic_limit_months = form_M # Fallback
            
            if mod.nivel:
                n_upper = mod.nivel.upper()
                if 'GRADUA' in n_upper or 'INICIA' in n_upper:
                    academic_limit_months = 60 # 5 Years
                elif 'MESTR' in n_upper or 'MASTER' in n_upper:
                    academic_limit_months = 24 # 2 Years
                elif 'DOUTOR' in n_upper or 'DOCTOR' in n_upper:
                    academic_limit_months = 48 # 4 Years

        except ValueError:
            flash('Dados de data ou duração inválidos.', 'error')
            return render_template('bolsistas/form.html', editais=editais, campuses=campuses, programas=programas, bolsista=None if 'novo' in request.path else bolsista)

        # REGRA 1: Precedência Acadêmica
        # A bolsa (IB) não pode começar antes do aluno iniciar o curso (IC).
        if form_IC and form_IB < form_IC:
            flash(f'Erro: Início da Bolsa ({form_IB}) não pode ser anterior ao Início do Curso ({form_IC}).', 'error')
            return render_template('bolsistas/form.html', editais=editais, campuses=campuses, programas=programas, bolsista=None if 'novo' in request.path else bolsista)

        # REGRA 2: Cálculo de Extensões (Bonificações de Prazo)
        # Certos afastamentos permitidos (Maternidade, Doença) estendem o prazo final.
        # - Maternidade: Adiciona até 6 meses ao "teto" da bolsa.
        # - Suspensões (Trancamento/PDSE): "Congelam" o tempo. O prazo final é empurrado para frente.
        
        ext_maternity = 0  # Bônus de tempo (não suspende, apenas aumenta o teto)
        ext_suspension = 0 # Tempo suspenso (empurra o fim)
        
        current_afastamentos = []
        # Se for edição, carregamos os afastamentos existentes do banco
        if 'novo' not in request.path:
            if 'bolsista' in locals():
                current_afastamentos = bolsista.afastamentos 

        for afast in current_afastamentos:
            if afast.tipo == 'maternidade':
                ext_maternity += min(afast.duracao_meses, 6) # Limite legal de 6 meses
            elif afast.tipo in ['trancamento', 'saude', 'pdse']: 
                ext_suspension += afast.duracao_meses

        # REGRA 3: Data Limite (Fatal)
        # Data máxima absoluta que o aluno pode manter vínculo.
        # REGRA 3: Data Limite (Fatal)
        # Data máxima absoluta que o aluno pode manter vínculo.
        # Fórmula: Limit = IC + (AcademicLimit + BônusMaternidade + Suspensões) - 1 mês.
        # Exemplo: Início 01/01/2024 + 24 meses -> Fim 01/12/2025.
        from dateutil.relativedelta import relativedelta
        
        M_extended = academic_limit_months + ext_maternity + ext_suspension
        
        if form_IC:
            # Calcula a data limite projetada
            limit_date = form_IC + relativedelta(months=M_extended)
            # Ajuste de "mês anterior ao aniversário" (Convenção -1 mês)
            limit_date = limit_date - relativedelta(months=1)
        else:
            # Caso sem IC (ex: Pós-Doc), definimos um limite distante
            limit_date = date(2099, 12, 31)

        # REGRA 4: Cálculo da Data Final Real (Fim da Bolsa)
        # Quando a bolsa efetivamente termina, considerando pagamentos e suspensões.
        # Fórmula: Fim = IB + (MesesPagos - 1) + TempoSuspenso
        
        end_date = form_IB + relativedelta(months=(form_D - 1 + ext_suspension))
        
        # REGRA 5: Verificação de Limite (Data vs Data)
        # A data final calculada não pode ultrapassar a Data Limite do vínculo.
        limit_tuple = (limit_date.year, limit_date.month)
        end_tuple = (end_date.year, end_date.month)

        if end_tuple > limit_tuple:
            # [EXCEPTION] Allow if Previsão de Defesa covers the scholarship end date
            # This handles cases where the student has an approved extension beyond the standard academic limit.
            try:
                pd_str = request.form.get('previsao_defesa')
                form_PD = datetime.strptime(pd_str, '%Y-%m-%d').date() if pd_str else None
            except:
                form_PD = None

            allow_exception = False
            if form_PD:
                pd_tuple = (form_PD.year, form_PD.month)
                # If Scholarship End <= Previsão End, we allow.
                if end_tuple <= pd_tuple:
                    allow_exception = True
            
            if not allow_exception:
                flash(f'Erro de Prazo: Data Final ({end_date.strftime("%m/%Y")}) excede o limite do vínculo ({limit_date.strftime("%m/%Y")}, {academic_limit_months} meses).', 'error')
                return render_template('bolsistas/form.html', editais=editais, campuses=campuses, programas=programas, bolsista=None if 'novo' in request.path else bolsista)

        # REGRA 6: Limite de Pagamentos (Meses vs Teto)
        # O número de mensalidades pagas (D) não pode ser maior que o permitido pela modalidade,
        # somado ao bônus maternidade. (Suspensão não dá direito a mais pagamentos, apenas mais tempo).
        if form_D > (form_M + ext_maternity):
            flash(f'Erro de Duração: {form_D} meses excede o limite da modalidade ({form_M} + {ext_maternity} bônus).', 'error')
            return render_template('bolsistas/form.html', editais=editais, campuses=campuses, programas=programas, bolsista=None if 'novo' in request.path else bolsista)

        # --- FIM DAS VALIDAÇÕES ---

        # [NEW] V5: Get Normalized IDs
        prog_id = int(request.form['programa_id']) if request.form.get('programa_id') else None
        
        # Fetch Objects for Legacy Compatibility
        prog_obj = ProgramaAcademico.query.get(prog_id) if prog_id else None
        campus_text = prog_obj.campus.nome if prog_obj else request.form.get('campus', '')
        campus_sigla = prog_obj.campus.sigla_campus if prog_obj else get_sigla(campus_text)
        prog_text = prog_obj.nome_programa if prog_obj else request.form.get('programa', '')

        novo_bolsista = Bolsista(
            edital_id=mod.edital_id,
            modalidade_id=mod.id,
            programa_id=prog_obj.id if prog_obj else None, # [NEW] V5
            data_fim_bolsa=end_date, # FIX: Save calculated end date
            nome=request.form['nome'],
            cpf=request.form['cpf'],
            email=request.form['email'],
            orientador=request.form['orientador'],
            email_orientador=request.form['email_orientador'], # V2
            campus=campus_text, # Legacy
            campus_sigla=campus_sigla, # Legacy
            programa=prog_text, # Legacy
            data_inicio_curso=datetime.strptime(request.form['data_inicio_curso'], '%Y-%m-%d').date() if request.form['data_inicio_curso'] else None,
            previsao_defesa=datetime.strptime(request.form['previsao_defesa'], '%Y-%m-%d').date() if request.form['previsao_defesa'] else None,
            banco=request.form['banco'],
            agencia=request.form['agencia'],
            conta=request.form['conta'],
            tipo_conta=request.form['tipo_conta'],
            data_inicio_bolsa=datetime.strptime(request.form['data_inicio_bolsa'], '%Y-%m-%d').date(),
            meses_duracao=int(request.form['meses_duracao']),
            processo_sei=request.form.get('processo_sei', ''), # V2
            numero_formulario=request.form.get('numero_formulario', ''), # V6
            comentarios=request.form.get('comentarios', ''), # V2
            is_pdse='is_pdse' in request.form, # V3
            pais_destino=request.form.get('pais_destino', ''), # V3
            # [NEW] Fields V6.2 (Pos-Doc Specifics)
            # These fields are conditionally visible in the UI based on Modality
            projeto_pesquisa=request.form.get('projeto_pesquisa', ''),
            recebe_bolsa=request.form.get('recebe_bolsa') == '1',
            agencia_fomento=request.form.get('agencia_fomento', '')
        )
        db.session.add(novo_bolsista)
        db.session.commit()
        flash('Bolsista cadastrado com sucesso!', 'success')
        return redirect(url_for('bolsistas_index'))

    return render_template('bolsistas/form.html', editais=editais, campuses=campuses, programas=programas, bolsista=None)

@app.route('/bolsistas/<int:id>/editar', methods=['GET', 'POST'])
def bolsistas_editar(id):
    bolsista = Bolsista.query.get_or_404(id)
    editais = Edital.query.all()
    #V5: Fetch Lists
    campuses = Campus.query.order_by(Campus.nome).all()
    programas = ProgramaAcademico.query.order_by(ProgramaAcademico.nome_programa).all()
    
    if request.method == 'POST':
        # --- INPUT HANDLING ---
        # Modalidade
        modalidade_id_raw = request.form.get('modalidade_id')
        if modalidade_id_raw:
            modalidade_id = int(modalidade_id_raw)
            mod = Modalidade.query.get(modalidade_id)
            bolsista.edital_id = mod.edital_id
            bolsista.modalidade_id = mod.id
        else:
            mod = bolsista.modalidade

        bolsista.nome = request.form['nome']
        bolsista.cpf = request.form['cpf']
        bolsista.email = request.form['email']
        bolsista.orientador = request.form['orientador']
        bolsista.email_orientador = request.form['email_orientador']
        
        # V5 Logic
        prog_id = int(request.form['programa_id']) if request.form.get('programa_id') else None
        if prog_id:
            prog_obj = ProgramaAcademico.query.get(prog_id)
            bolsista.programa_id = prog_id
            bolsista.campus = prog_obj.campus.nome
            bolsista.campus_sigla = prog_obj.campus.sigla_campus
            bolsista.programa = prog_obj.nome_programa
        
        bolsista.data_inicio_curso = datetime.strptime(request.form['data_inicio_curso'], '%Y-%m-%d').date() if request.form['data_inicio_curso'] else None
        bolsista.previsao_defesa = datetime.strptime(request.form['previsao_defesa'], '%Y-%m-%d').date() if request.form['previsao_defesa'] else None
        bolsista.banco = request.form['banco']
        bolsista.agencia = request.form['agencia']
        bolsista.conta = request.form['conta']
        bolsista.tipo_conta = request.form['tipo_conta']
        bolsista.data_inicio_bolsa = datetime.strptime(request.form['data_inicio_bolsa'], '%Y-%m-%d').date()
        bolsista.meses_duracao = int(request.form['meses_duracao'])
            
        # --- STRICT VALIDATION ---
        form_IC = bolsista.data_inicio_curso
        form_IB = bolsista.data_inicio_bolsa
        form_D = bolsista.meses_duracao
        form_M = mod.max_meses if mod.max_meses else 0
        
        # [ADJUSTMENT - V6] Decoupling Academic Limit
        academic_limit_months = form_M
        if mod.nivel:
             n_upper = mod.nivel.upper()
             if 'GRADUA' in n_upper or 'INICIA' in n_upper:
                 academic_limit_months = 60
             elif 'MESTR' in n_upper or 'MASTER' in n_upper:
                 academic_limit_months = 24
             elif 'DOUTOR' in n_upper or 'DOCTOR' in n_upper:
                 academic_limit_months = 48

        # 1. Precedence
        if form_IC and form_IB < form_IC:
            flash(f'Erro: Início ({form_IB}) anterior ao Curso ({form_IC}).', 'error')
            return render_template('bolsistas/form.html', editais=editais, campuses=campuses, programas=programas, bolsista=bolsista)

        # 2. Extensions
        ext_maternity = 0
        ext_suspension = 0
        current_afastamentos = bolsista.afastamentos
        for afast in current_afastamentos:
            if afast.tipo == 'maternidade':
                ext_maternity += min(afast.duracao_meses, 6)
            elif afast.tipo in ['trancamento', 'saude', 'pdse']:
                ext_suspension += afast.duracao_meses

        # 3. Limit (Using Academic Limit)
        from dateutil.relativedelta import relativedelta
        M_extended = academic_limit_months + ext_maternity + ext_suspension
        if form_IC:
            limit_date = form_IC + relativedelta(months=M_extended) - relativedelta(months=1)
        else:
            limit_date = date(2099, 12, 31)

        # 4. End Date
        end_date = form_IB + relativedelta(months=(form_D - 1 + ext_suspension))
        
        # 5. Check Limit
        limit_tuple = (limit_date.year, limit_date.month)
        end_tuple = (end_date.year, end_date.month)

        if end_tuple > limit_tuple:
             # [EXCEPTION] Allow if Previsão de Defesa covers the scholarship end date
             try:
                 pd_str = request.form.get('previsao_defesa')
                 form_PD = datetime.strptime(pd_str, '%Y-%m-%d').date() if pd_str else None
             except:
                 form_PD = None
 
             allow_exception = False
             if form_PD:
                 pd_tuple = (form_PD.year, form_PD.month)
                 if end_tuple <= pd_tuple:
                     allow_exception = True
 
             if not allow_exception:
                 flash(f'Erro de Prazo: Data Final ({end_date.strftime("%m/%Y")}) excede o limite do vínculo ({limit_date.strftime("%m/%Y")}, {academic_limit_months} meses).', 'error')
                 return render_template('bolsistas/form.html', editais=editais, campuses=campuses, programas=programas, bolsista=bolsista)

        # 6. Check Max Paid
        if form_D > (form_M + ext_maternity):
            flash(f'Erro de Duração: {form_D} meses excede o limite ({form_M} + {ext_maternity}).', 'error')
            return render_template('bolsistas/form.html', editais=editais, campuses=campuses, programas=programas, bolsista=bolsista)

        # --- SAVE ---
        # FIX: Ensure calculated end_date is saved!
        bolsista.data_fim_bolsa = end_date 
        
        bolsista.processo_sei = request.form.get('processo_sei', '')
        bolsista.numero_formulario = request.form.get('numero_formulario', '') # V6
        bolsista.comentarios = request.form.get('comentarios', '')
        bolsista.is_pdse = 'is_pdse' in request.form
        bolsista.pais_destino = request.form.get('pais_destino', '')
        if 'ativo' not in request.form:
             # TERMINATION LOGIC
             bolsista.ativo = False
             
             # If previously active (or verifying logic), set Data Final to TODAY
             from datetime import date
             today = date.today()
             
             # Set Data Desligamento if not set
             if not bolsista.data_desligamento:
                 bolsista.data_desligamento = today
                 
             # Truncate Data Fim Bolsa to Today
             bolsista.data_fim_bolsa = today
             
             # Add motif if empty
             if not bolsista.motivo_desligamento:
                 bolsista.motivo_desligamento = "Desligamento Manual via Sistema"
                 
        else:
             # REACTIVATION LOGIC
             bolsista.ativo = True
             # Reset Data Desligamento
             bolsista.data_desligamento = None
             # Ensure Data Fim Bolsa is correct (Recalculated above as 'end_date')
             bolsista.data_fim_bolsa = end_date
             # Clear motif? Optional. Let's keep history or clear. 
             # bolsista.motivo_desligamento = None # Uncomment to clear
        
        # [NEW] PosDoc Fields Update
        bolsista.projeto_pesquisa = request.form.get('projeto_pesquisa', '')
        bolsista.recebe_bolsa = (request.form.get('recebe_bolsa') == '1')
        bolsista.agencia_fomento = request.form.get('agencia_fomento', '')
        # bolsista.ativo = 'ativo' in request.form # REMOVED (Handled above)

        db.session.commit()
        flash('Bolsista atualizado (DEBUG V5)!', 'success')
        return redirect(url_for('bolsistas_index'))

    return render_template('bolsistas/form.html', bolsista=bolsista, editais=editais, campuses=campuses, programas=programas)

@app.route('/bolsistas/<int:id>/excluir', methods=['POST'])
def bolsistas_excluir(id):
    bolsista = Bolsista.query.get_or_404(id)
    
    # Check if PosDoc for correct redirect
    is_posdoc = False
    if bolsista.modalidade and any(x in bolsista.modalidade.nivel.upper() for x in ['PÓS', 'POS', 'RESID']):
        is_posdoc = True
        
    db.session.delete(bolsista)
    db.session.commit()
    flash('Registro excluído com sucesso!', 'success')
    
    if is_posdoc:
        return redirect(url_for('posdoc_index'))
    return redirect(url_for('bolsistas_index'))

# === AFASTAMENTOS (LEAVES) ===
@app.route('/bolsistas/<int:id>/afastamento/novo', methods=['POST'])
def afastamento_novo(id):
    try:
        bolsista = Bolsista.query.get_or_404(id)
        tipo = request.form['tipo']
        data_inicio = datetime.strptime(request.form['data_inicio'], '%Y-%m-%d').date()
        duracao = int(request.form['duracao_meses'])
        observacao = request.form['observacao']
        
        # 1. Register Leave
        novo_afastamento = Afastamento(
            bolsista_id=id,
            tipo=tipo,
            data_inicio=data_inicio,
            duracao_meses=duracao,
            observacao=observacao
        )
        db.session.add(novo_afastamento)
        
        # 2. Logic: Extend Scholarship End Date
        # For both Suspension and Maternity, we shift the end date by the duration
        from dateutil.relativedelta import relativedelta
        if bolsista.data_fim_bolsa:
            bolsista.data_fim_bolsa += relativedelta(months=duracao)
        
        db.session.commit()
        flash(f'Afastamento registrado. Término da bolsa estendido em {duracao} meses.', 'success')
        return redirect(url_for('bolsistas_editar', id=id))
    except Exception as e:
        import traceback
        with open('debug_error.txt', 'a') as f:
            f.write(f"\n--- ERROR AFASTAMENTO NOVO ---\n{traceback.format_exc()}")
        return f"Erro interno: {e}", 500

@app.route('/bolsistas/afastamento/<int:id>/excluir', methods=['POST'])
def afastamento_excluir(id):
    afastamento = Afastamento.query.get_or_404(id)
    bolsista_id = afastamento.bolsista_id
    bolsista = Bolsista.query.get(bolsista_id)
    
    # Revert extension
    from dateutil.relativedelta import relativedelta
    bolsista.data_fim_bolsa -= relativedelta(months=afastamento.duracao_meses)
    
    db.session.delete(afastamento)
    db.session.commit()
    flash('Afastamento removido. Data de término ajustada.', 'success')
    return redirect(url_for('bolsistas_editar', id=bolsista_id))

@app.route('/bolsistas/limpar_edital/<int:edital_id>', methods=['POST'])
def bolsistas_limpar_edital(edital_id):
    try:
        edital = Edital.query.get_or_404(edital_id)
        count = Bolsista.query.filter_by(edital_id=edital_id).delete()
        db.session.commit()
        flash(f'{count} bolsistas excluídos do Edital {edital.numero}.', 'warning')
    except Exception as e:
        flash(f'Erro ao excluir: {str(e)}', 'danger')
        
    return redirect(url_for('bolsistas_index', edital_id=edital_id))

# === PROGRAMA MANGEMENT API ===
@app.route('/api/programas', methods=['POST'])
def api_programas_create():
    try:
        data = request.json
        campus_id = int(data.get('campus_id'))
        
        novo_prog = ProgramaAcademico(
            codigo_programa=data.get('codigo') or None,
            nome_programa=data.get('nome'),
            sigla_programa=data.get('sigla'),
            campus_id=campus_id
        )
        db.session.add(novo_prog)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'id': novo_prog.id,
            'nome': novo_prog.nome_programa,
            'sigla': novo_prog.sigla_programa,
            'campus_id': novo_prog.campus_id
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/programas/<int:id>', methods=['GET'])
def api_programas_get(id):
    prog = ProgramaAcademico.query.get_or_404(id)
    return jsonify({
        'id': prog.id,
        'codigo': prog.codigo_programa,
        'nome': prog.nome_programa,
        'sigla': prog.sigla_programa,
        'campus_id': prog.campus_id
    })

@app.route('/api/programas/<int:id>', methods=['PUT'])
def api_programas_update(id):
    try:
        prog = ProgramaAcademico.query.get_or_404(id)
        data = request.json
        
        prog.codigo_programa = data.get('codigo') or None
        prog.nome_programa = data.get('nome')
        prog.sigla_programa = data.get('sigla')
        prog.campus_id = int(data.get('campus_id'))
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'id': prog.id,
            'nome': prog.nome_programa,
            'sigla': prog.sigla_programa,
            'campus_id': prog.campus_id
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# === MODALIDADES API ===
@app.route('/api/modalidades/<int:edital_id>')
def api_modalidades(edital_id):
    modalidades = Modalidade.query.filter_by(edital_id=edital_id).all()
    return jsonify([{
        'id': m.id, 
        'nivel': m.nivel, 
        'valor': m.valor_mensal, 
        'vagas': m.vagas,
        'max_meses': m.max_meses # [NEW] V2
    } for m in modalidades])

# === RELATÓRIOS ===
from reports import gerar_relatorio_excel, gerar_relatorio_pdf, gerar_relatorio_graficos

# === PÓS-DOUTORADO E RESIDÊNCIA (V6.3) ===
@app.route('/posdoc')
def posdoc_index():
    from sqlalchemy import or_ # Import at top of function
    search_q = request.args.get('q', '').strip()
    
    # Base Query: Residente Table (No longer need generic filter)
    query = Residente.query

    if search_q:
        term = f"%{search_q}%"
        query = query.filter(
            or_(
                Residente.nome.ilike(term),
                Residente.cpf.ilike(term),
                Residente.projeto_pesquisa.ilike(term),
                Residente.processo_sei.ilike(term)
            )
        )
    
    posdocs = query.all()
    total_registros = len(posdocs)

    return render_template('posdoc/index.html', posdocs=posdocs, search_q=search_q, total_registros=total_registros)



@app.route('/posdoc/importar', methods=['GET', 'POST'])
def posdoc_importar():
    editais = Edital.query.order_by(Edital.numero.desc()).all()
    resultado = None
    
    if request.method == 'POST':
        # Reuse file upload logic
        if 'arquivo' not in request.files:
            flash('Nenhum arquivo enviado', 'error')
            return redirect(request.url)
        
        file = request.files['arquivo']
        if file.filename == '':
            flash('Nenhum arquivo selecionado', 'error')
            return redirect(request.url)
        
        # [CHANGE V6.3] Auto-select "Residência Pós-Doutoral" (ID 21) or search by name
        # User requested to remove manual selection.
        # Fallback to ID 21 if name fails, or searching.
        target_name = "Residência Pós-Doutoral"
        edital = Edital.query.filter(Edital.numero.ilike(f'%{target_name}%')).first()
        
        if not edital:
            # Fallback ID 21 (Hardcoded based on exploration)
            edital = Edital.query.get(21)
        
        if not edital:
             flash(f'Edital "{target_name}" não encontrado. Contate o suporte.', 'error')
             return redirect(request.url)
        
        # edital_id = request.form.get('edital_id') -- REMOVED
        
        # Determine format
        filename = file.filename
        import pandas as pd
        
        try:
            if filename.endswith('.csv'):
                # [IMPROVEMENT] Auto-detect separator (common issue with Excel/CSV variants)
                try:
                    df = pd.read_csv(file, encoding='utf-8', sep=None, engine='python')
                except:
                    # Fallback to latin-1 if utf-8 fails
                    file.seek(0)
                    df = pd.read_csv(file, encoding='latin-1', sep=None, engine='python')
            elif filename.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(file)
            else:
                 flash('Formato inválido. Use .csv ou .xlsx', 'error')
                 return redirect(request.url)
            
            # --- POS-DOC IMPORT LOGIC ---
            # It's safer to have a dedicated processor for PosDoc structure.
            # Usually: Nome, CPF, Programa, Projeto, Supervisor, Inicio, Fim.
            
            sucesso = 0
            erros = 0
            log = []
            
            # Mapping Modalidades for this Edital (Cache)
            # Filter only PosDoc modalities?
            modalidades = Modalidade.query.filter_by(edital_id=edital.id).all()
            modalidades_map = {m.nivel.upper(): m for m in modalidades} # 'POS-DOUTORADO': obj
            
            # Helper for normalizing Programas
            programas_db = ProgramaAcademico.query.all()
            # Create a loose map: 'MECANICA' -> ID, 'PPGEM' -> ID
            prog_map = {}
            for p in programas_db:
                prog_map[p.nome_programa.upper()] = p
                prog_map[p.sigla_programa.upper()] = p
            
            for index, row in df.iterrows():
                row_num = index + 2 # Header is 1
                
                # Check empty rows (Support 'Residente' alias)
                nome_check = row.get('Nome') if 'Nome' in row else row.get('Residente')
                cpf_check = row.get('CPF')
                if pd.isna(nome_check) and pd.isna(cpf_check): continue

                res = processar_importacao_posdoc(row, edital, modalidades_map, prog_map, log, row_num)
                if res:
                    db.session.add(res)
                    sucesso += 1
                else:
                    erros += 1
            
            db.session.commit()
            
            resultado = {'sucesso': sucesso, 'erro': erros, 'log_erros': log}
            if sucesso > 0:
                flash(f'Importação Pós-Doc finalizada. {sucesso} importados.', 'success')
            else:
                flash('Nenhum registro importado.', 'warning')

        except Exception as e:
            flash(f'Erro ao processar arquivo: {str(e)}', 'error')
    
    # We can reuse the same template 'bolsistas/importar.html' or a new one?
    # Let's reuse 'bolsistas/importar.html' but maybe pass title/flag?
    return render_template('bolsistas/importar.html', editais=editais, resultado=resultado, title="Importar Residentes (Pós-Doc)")


def processar_importacao_posdoc(row, edital, modalidades_map, prog_map, log, row_num):
    import pandas as pd
    try:
        # COLUMNS/ALIASES
        # Nome: 'Residente' or 'Nome' [Mandatory]
        # CPF: 'CPF' [Optional]
        # Programa: 'Programa' [Optional]
        # Projeto: 'Projeto' or 'Título' [Optional]
        # Supervisor: 'Supervisor' [Optional]
        # Inicio: 'Data Inicio', 'Início' [Optional]
        # Fim: 'Data Fim', 'Fim', 'Previsão' [Optional]
        # Bolsa: 'Bolsa', 'Recebe Bolsa' (Sim/Nao) [Optional]
        # SEI: 'SEI', 'Processo SEI' [Optional]
        # Campus: 'Campus' [Optional, used for logging/debug or map help]

        # 1. PERSON (Name is mandatory)
        nome = str(row.get('Residente') or row.get('Nome', '')).strip()
        if not nome or nome.lower() == 'nan':
             raise ValueError("Nome do Residente obrigatório")
        
        # CPF (Optional - generated placeholder if missing? Or allow Null? Model allows Null technically, but uniqueness might be tricky)
        # Decision: Allow Null.
        cpf = str(row.get('CPF', '')).strip()
        if not cpf or cpf.lower() == 'nan':
            cpf = None
        else:
            # Check existence if CPF provided
            exists = Bolsista.query.filter_by(cpf=cpf).first()
            if exists: raise ValueError(f"CPF {cpf} já cadastrado ({exists.nome})")

        # 2. MODALITY (Auto-Select 'Pós-Doutorado' if available)
        mod_obj = None
        for k, v in modalidades_map.items():
            if 'POS' in k or 'PÓS' in k or 'RESID' in k:
                mod_obj = v
                break
        
        if not mod_obj: raise ValueError("Nenhuma modalidade de Pós-Doutorado encontrada neste Edital.")

        # 3. PROGRAM (Generic Map)
        prog_raw = str(row.get('Programa', '')).strip().upper()
        programa_obj = None
        if prog_raw and prog_raw != 'NAN':
            if prog_raw in prog_map:
                programa_obj = prog_map[prog_raw]
            else:
                 # Fuzzy?
                 for k, v in prog_map.items():
                     if k in prog_raw or prog_raw in k:
                         programa_obj = v
                         break
            if not programa_obj:
                log.append(f"Linha {row_num}: Programa '{prog_raw}' não encontrado. Vinculado sem programa.")
        
        # 4. DATES (Inicio / Fim)
        fmt_list = ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y']
        dt_inicio = None
        dt_fim = None
        
        val_ini = row.get('Data Inicio') or row.get('Início') or row.get('Inicio')
        val_fim = row.get('Data Fim') or row.get('Fim') or row.get('Previsão') or row.get('Previsao')

        from datetime import datetime
        def parse_dt(val):
            if pd.isna(val): return None
            val_str = str(val).strip()
            if not val_str or val_str.lower() == 'nan': return None
            for f in fmt_list:
                try:
                    return datetime.strptime(val_str, f).date()
                except: continue
            return None

        dt_inicio = parse_dt(val_ini)
        dt_fim = parse_dt(val_fim)
        
        # Defaults
        if not dt_inicio: dt_inicio = date.today()
        if not dt_fim: 
            from dateutil.relativedelta import relativedelta
            dt_fim = dt_inicio + relativedelta(months=12) # Default 12m
            
        # Calc Duration
        from dateutil.relativedelta import relativedelta
        diff = relativedelta(dt_fim, dt_inicio)
        meses = diff.years * 12 + diff.months
        if diff.days > 15: meses += 1
        
        # 5. EXTRAS
        supervisor = str(row.get('Supervisor', '')).strip()
        if supervisor.lower() == 'nan': supervisor = ''
        
        projeto = str(row.get('Projeto') or row.get('Título', '')).strip()
        if projeto.lower() == 'nan': projeto = ''
        
        agencia = str(row.get('Agencia', '')).strip() # Not in requested list, but loop?
        if agencia.lower() == 'nan': agencia = ''
        
        # Bolsa
        bolsa_val = str(row.get('Bolsa') or row.get('Recebe Bolsa', '0')).upper()
        recebe_bolsa = (bolsa_val in ['SIM', 'S', 'YES', '1', 'TRUE'])
        
        # SEI
        sei = str(row.get('SEI') or row.get('Processo SEI', '')).strip()
        if sei.lower() == 'nan': sei = ''

        # CREATE RESIDENTE
        # [CHANGE V7] Use Residente model instead of Bolsista
        novo = Residente(
            edital_id=edital.id,
            modalidade_id=mod_obj.id,
            programa_id=programa_obj.id if programa_obj else None,
            nome=nome,
            cpf=cpf, # Can be None
            email=str(row.get('Email', '')).strip().replace('nan', ''), 
            data_inicio=dt_inicio, # Note: field name changed from data_inicio_bolsa
            data_fim=dt_fim,       # Note: field name changed from data_fim_bolsa
            meses_duracao=meses,
            ativo=True,
            
            # PosDoc Fields
            supervisor=supervisor,             # Direct mapping
            projeto_pesquisa=projeto,          # Direct mapping
            agencia_fomento=agencia,
            recebe_bolsa=recebe_bolsa,
            processo_sei=sei
        )
        
        db.session.add(novo)
        return novo
    
    except Exception as ex:
        log.append(f"Linha {row_num}: {str(ex)}")
        return None

@app.route('/posdoc/novo', methods=['GET', 'POST'])
def posdoc_novo():
    if request.method == 'POST':
        return residentes_action('novo') # Use residentes_action
    
    # GET
    editais = Edital.query.order_by(Edital.numero.desc()).all()
    programas = ProgramaAcademico.query.join(Campus).order_by(ProgramaAcademico.nome_programa).all()
    campuses = Campus.query.order_by(Campus.nome).all() # Pass campuses for form
    
    # Use 'bolsista' context key to reuse template logic
    return render_template('posdoc/form.html', editais=editais, programas=programas, campuses=campuses, bolsista=None)

@app.route('/posdoc/<int:id>/editar', methods=['GET', 'POST'])
def posdoc_editar(id):
    if request.method == 'POST':
        return residentes_action('editar', id=id)

    residente = Residente.query.get_or_404(id) # Query Residente
    
    editais = Edital.query.order_by(Edital.numero.desc()).all()
    programas = ProgramaAcademico.query.join(Campus).order_by(ProgramaAcademico.nome_programa).all()
    campuses = Campus.query.order_by(Campus.nome).all()
    
    # Pass 'residente' as 'bolsista' to reuse the form template
    return render_template('posdoc/form.html', bolsista=residente, editais=editais, programas=programas, campuses=campuses)

@app.route('/posdoc/<int:id>/excluir', methods=['POST'])
def posdoc_excluir(id):
    residente = Residente.query.get_or_404(id)
    try:
        db.session.delete(residente)
        db.session.commit()
        flash('Residente excluído com sucesso.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir residente: {str(e)}', 'error')
    return redirect(url_for('posdoc_index'))

@app.route('/relatorios')
def relatorios_index():
    return render_template('relatorios/index.html')

# === DOCUMENTATION ===
@app.route('/docs/download/<filename>')
def docs_download(filename):
    """Serve documentation PDFs from static/docs folder"""
    try:
        docs_dir = os.path.join(app.root_path, 'static', 'docs')
        return send_from_directory(docs_dir, filename, as_attachment=True)
    except FileNotFoundError:
        flash('Arquivo de documentação não encontrado.', 'error')
        return redirect(url_for('index'))

@app.route('/admin/backup', methods=['POST'])
def admin_backup():
    try:
        # 1. Create Local Backup
        backup_path = backup_system.create_backup()
        
        if backup_path:
            # 2. Copy to Cloud (if configured)
            cloud_destination = backup_system.copy_to_cloud(backup_path)
            
            # 3. Clean Old Backups (Local & Cloud)
            backup_system.clean_old_backups(backup_system.BACKUP_DIR)
            
            # Prepare feedback message
            msg = "Backup realizado com sucesso e baixado para seu computador."
            if cloud_destination:
                msg += f" Cópia na Nuvem: {cloud_destination}"
            
            flash(msg, 'success')
            
            # 4. DOWNLOAD to User's PC
            return send_file(backup_path, as_attachment=True, download_name=os.path.basename(backup_path))
        else:
            flash('Erro ao criar backup local. Verifique o console.', 'danger')
            
    except Exception as e:
        flash(f'Erro crítico no backup: {str(e)}', 'danger')
        
    return redirect(request.referrer or url_for('index'))

@app.route('/api/dashboard-data')
def dashboard_data():
    from sqlalchemy import func
    from datetime import date, datetime
    
    current_year = datetime.now().year
    today = date.today()
    
    # Fetch ALL bolsistas to calculate "Theoretical" values based on strict dates
    # ensuring accuracy even if 'Acompanhamento' is empty or 'Ativo' flag is stale.
    all_bolsistas = Bolsista.query.all()
    
    total_anual_ytd = 0
    total_mensal = 0
    
    total_anual_ytd = 0.0
    total_mensal = 0.0
    
    # Datas Base (Travadas em 2026 para Staging/QA conforme pedido)
    year_ref = 2026
    year_start = date(year_ref, 1, 1)
    year_end = date(year_ref, 12, 31)
    
    # Estruturas para Gráficos (Baseado no Orçamento Anual 2026)
    invest_edital = {}
    invest_campus = {}
    invest_programa = {}
    invest_nivel = {}

    for b in all_bolsistas:
        if not b.modalidade: continue
        
        # --- 1. CÁLCULO ACUMULADO DO ANO (YTD) 2026 ---
        # Verifica se o bolsista receberá algo em 2026
        val_ytd = 0.0
        start = b.data_inicio_bolsa
        end = b.data_fim_bolsa
        
        if start and end:
            # Interseção com o Ano Fiscal 2026
            inter_start = max(start, year_start)
            inter_end = min(end, year_end)
            
            if inter_start <= inter_end:
                 # Conta meses de pagamento em 2026
                 months = (inter_end.year - inter_start.year) * 12 + (inter_end.month - inter_start.month) + 1
                 val_ytd = months * b.modalidade.valor_mensal
                 total_anual_ytd += val_ytd
                 
                 # [AJUSTE QA] Gráficos agora refletem o INVESTIMENTO ANUAL (Orçamento)
                 # e não apenas a folha do mês. 
                 
                 # Por Edital
                 ed_label = b.edital.numero
                 if "recursos pr" in (b.edital.descricao or "").lower():
                     ed_label = "Recursos Próprios"
                 elif "edital" not in ed_label.lower():
                     ed_label = f"Ed. {ed_label}"
                 invest_edital[ed_label] = invest_edital.get(ed_label, 0) + val_ytd
                 
                 # Por Nível
                 nivel = b.modalidade.nivel
                 invest_nivel[nivel] = invest_nivel.get(nivel, 0) + val_ytd
                 
                 # Por Campus
                 c_sigla = "N/I"
                 if b.programa_link and b.programa_link.campus:
                     c_sigla = b.programa_link.campus.sigla_campus
                 elif b.campus_sigla:
                     c_sigla = b.campus_sigla
                 elif b.campus:
                     c_sigla = b.campus[:3].upper()
                 invest_campus[c_sigla] = invest_campus.get(c_sigla, 0) + val_ytd
                 
                 # Por Programa
                 p_sigla = "N/I"
                 if b.programa_link:
                     p_sigla = b.programa_link.sigla_programa
                 elif b.programa:
                     p_sigla = b.programa.split(' - ')[0] if ' - ' in b.programa else b.programa[:10]
                 invest_programa[p_sigla] = invest_programa.get(p_sigla, 0) + val_ytd

        # --- 2. CÁLCULO MENSAL (Vigente Hoje) ---
        # "Bolsas pagas no mês corrente"
        if start and end and start <= today <= end:
            val = b.modalidade.valor_mensal
            total_mensal += val

    # 3. ACADÊMICO: Duração Média (Apenas Ativos)
    # Lista de durações dos bolsistas ativos
    active_durations = [b.meses_duracao for b in all_bolsistas if b.modalidade and b.data_inicio_bolsa and b.data_fim_bolsa and b.data_inicio_bolsa <= today <= b.data_fim_bolsa]
    avg_duration = sum(active_durations) / len(active_durations) if active_durations else 0
    avg_duration = round(avg_duration, 1)

    # 4. OCUPAÇÃO (Lista Texto)
    # Precisamos consultar as modalidades para pegar 'vagas totais'
    modalidades = Modalidade.query.all()
    vacancy_data = [] # Lista de dados de vagas
    
    nivel_map = {
        'Mestrado': 'M', 'Doutorado': 'D', 
        'Pós-Doutorado': 'PD', 'Pos-Doutorado': 'PD',
        'Iniciação Científica': 'IC', 'Iniciacao Cientifica': 'IC',
        'Graduação': 'G', 'Graduacao': 'G'
    }
    
    for mod in modalidades:
        # Contar ativos estritamente pela data
        occupied = 0
        for b in mod.bolsistas:
            if b.data_inicio_bolsa and b.data_fim_bolsa and b.data_inicio_bolsa <= today <= b.data_fim_bolsa:
                occupied += 1
        
        # Formatação do Rótulo
        short_nivel = nivel_map.get(mod.nivel, mod.nivel[0].upper())
        ed_name = mod.edital.numero
        if "recursos pr" in (mod.edital.descricao or "").lower():
            ed_name = "Recursos Próprios"
        elif "edital" not in ed_name.lower():
            ed_name = f"Ed. {ed_name}"
            
        label = f"{ed_name} ({short_nivel})"
        
        vacancy_data.append({
            'label': label,
            'vagas': mod.vagas,
            'occupied': occupied,
            'vacant': max(0, mod.vagas - occupied)
        })

    # Sort maps
    def sort_map(m):
        return sorted([{'label': k, 'value': v} for k, v in m.items()], key=lambda x: x['value'], reverse=True)

    return jsonify({
        'financeiro': {
            'anual_ytd': total_anual_ytd,
            'mensal_atual': total_mensal,
            'por_edital': sort_map(invest_edital),
            'por_nivel': sort_map(invest_nivel),
            'por_campus': sort_map(invest_campus),
            'por_programa': sort_map(invest_programa)
        },
        'academico': {
            'duracao_media': avg_duration
        },
        'ocupacao': vacancy_data
    })




@app.route('/capes/dashboard')
def capes_dashboard():
    # 1. Fetch Quotas
    # Join with Programa to get Name/Code
    # Join with Modalidade because `distribuicao_cotas` has modalidade_id
    
    # We want a list of programs, with nested Mestrado/Doutorado info
    
    # SQL: SELECT p.id, p.nome, m.nivel, c.qtd_concedida 
    # FROM distribuicao_cotas c 
    # JOIN programa p ON c.prog = p.id
    # JOIN modalidade m ON c.mod = m.id
    # WHERE c.edital_id = 14
    
    sql = """
    SELECT 
        p.id, p.nome_programa, p.codigo_programa,
        cp.sigla_campus,
        m.nivel, c.qtd_concedida
    FROM distribuicao_cotas c
    JOIN programa_academico p ON c.programa_id = p.id
    JOIN campus cp ON p.campus_id = cp.id
    JOIN modalidades m ON c.modalidade_id = m.id
    WHERE c.edital_id = 14
    ORDER BY cp.sigla_campus, p.nome_programa
    """
    
    # Use SQLAlchemy session for raw query
    from sqlalchemy import text
    result = db.session.execute(text(sql))

    # Map: ProgramID -> {nome, code, campus, mestrado: {}, doutorado: {}}
    data_map = {}
    
    for r in result:
        pid = r.id
        nome = r.nome_programa
        code = r.codigo_programa
        campus = r.sigla_campus
        nivel = r.nivel
        cota = r.qtd_concedida
        
        if pid not in data_map:
            data_map[pid] = {
                'nome': nome, 
                'codigo': code, 
                'campus': campus,
                'mestrado': {'cota': 0, 'ocupado': 0},
                'doutorado': {'cota': 0, 'ocupado': 0}
            }
            
        key = 'mestrado' if 'mestrado' in nivel.lower() else 'doutorado'
        data_map[pid][key]['cota'] = cota
        
    # 2. Calculate Occupation
    # Count Active Bolsistas linked to Edital 14 (CAPES DS) grouped by Program
    # We need to distinguish Modality (Mestrado/Doutorado) via the Modalidade table linked to Bolsista?
    # Actually Bolsista links to Edital directly, but usually we link Modality too?
    # `Bolsista` model has `modalidade_id`.
    
    sql_occ = """
    SELECT b.programa_id, m.nivel, COUNT(*) as count
    FROM bolsistas b
    JOIN modalidades m ON b.modalidade_id = m.id
    WHERE b.ativo = 1 AND b.edital_id = 14
    GROUP BY b.programa_id, m.nivel
    """
    
    occ_result = db.session.execute(text(sql_occ))
    
    for r in occ_result:
        pid = r.programa_id
        if pid in data_map:
            nivel = r.nivel
            count = r.count
            key = 'mestrado' if 'mestrado' in nivel.lower() else 'doutorado'
            data_map[pid][key]['ocupado'] = count
            
    # Remove conn.close() as db.session handles it
    
    # Convert map to sorted list
    result = sorted(data_map.values(), key=lambda x: x['nome'])
    
    return render_template('capes/dashboard.html', dados=result)

@app.route('/tutorial') # [NEW] V2
def tutorial():
    return render_template('tutorial.html')

@app.route('/relatorios/gerar', methods=['POST'])
def relatorios_gerar():
    """
    Central de Geração de Relatórios.
    
    Tipos Suportados:
    - Excel (.xlsx): Planilha detalhada de pagamentos (biblioteca pandas).
    - PDF (.pdf): Documento formal de folha de pagamento (biblioteca reportlab).
    - Gráficos (.pdf): Dashboard visual de distribuição de recursos.
    """
    tipo = request.form['tipo'] # excel or pdf
    mes = request.form['mes'] # YYYY-MM
    
    if tipo == 'excel':
        output = gerar_relatorio_excel(mes)
        return send_file(output, download_name=f'pagamento_{mes}.xlsx', as_attachment=True)
    elif tipo == 'pdf':
        output = gerar_relatorio_pdf(mes)
        return send_file(output, download_name=f'pagamento_{mes}.pdf', as_attachment=True)
    elif tipo == 'graficos':
        output = gerar_relatorio_graficos(mes)
        return send_file(output, download_name=f'relatorio_grafico_{mes}.pdf', as_attachment=True)
    elif tipo == 'programas_excel':
        # [NEW] Relatório de Programas 2025
        output = gerar_relatorio_programas_excel()
        return send_file(output, download_name='programas_posgraduacao_2025.xlsx', as_attachment=True)
    
    return redirect(url_for('relatorios_index'))


def gerar_relatorio_programas_excel():
    """
    Gera planilha com dados completos dos PPGs (incluindo Nota CAPES, Áreas, etc)
    """
    import pandas as pd
    import io
    import sys
    from sqlalchemy import text
    
    sql = """
    SELECT 
        p.codigo_programa as "Código PPG",
        p.nome_programa as "Nome do Curso",
        p.sigla_programa as "Sigla",
        c.nome as "Campus",
        p.nota_capes as "Nota CAPES",
        p.area_avaliacao as "Área Avaliação",
        p.area_basica as "Área Básica",
        p.ano_inicio as "Ano Início"
    FROM programa_academico p
    JOIN campus c ON p.campus_id = c.id
    ORDER BY p.nome_programa, c.nome
    """
    
    try:
        # Use Pandas for easy Excel generation
        # [FIX] SQLAlchemy 2.0+ requires a connection, not just an engine, for some operations.
        # Flask-SQLAlchemy 3.x: Access engine via db.engine
        with db.engine.connect() as conn:
            df = pd.read_sql(text(sql), conn)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Programas 2025')
            
            # Auto-adjust columns width
            worksheet = writer.sheets['Programas 2025']
            for column in worksheet.columns:
                max_length = 0
                column = [cell for cell in column]
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = (max_length + 2)
                worksheet.column_dimensions[column[0].column_letter].width = adjusted_width
        
        output.seek(0)
        return output

    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        # Write to file for easier access
        with open("last_excel_error.txt", "w", encoding="utf-8") as f:
            f.write(f"Timestamp: {pd.Timestamp.now()}\n")
            f.write(error_msg)
            
        print("❌ ERRO CRÍTICO NA GERAÇÃO DO EXCEL (Salvo em last_excel_error.txt):", file=sys.stderr)
        print(error_msg, file=sys.stderr)
        raise e


# === IMPORTAÇÃO EM MASSA (CAPES DS) ===
@app.route('/bolsistas/importar', methods=['GET', 'POST'])
def bolsistas_importar():
    """
    Rota para importação em massa de bolsistas via planilha (CAPES IES/DS).
    
    Lógica de Processamento:
    1. Upload: Aceita arquivos CSV ou 'fakes' CSV (separados por TAB).
    2. Detecção: Sniffer detecta delimitador (TAB, ;, ,) e encoding (UTF-8/Latin-1).
    3. Parsing:
       - 'Tipo Vínculo': Extrai código do programa (ex: 40006018008P6). *Opcional.
       - 'Modalidade': Mapeia Mestrado/Doutorado para IDs do Edital selecionado.
       - 'Beneficiário': Separa CPF e Nome.
       - 'Vigência': Calcula duração em meses.
    4. Feedback: Retorna contagem de sucessos e logs de erro/aviso.
    """
    editais = Edital.query.all()
    resultado = None

    if request.method == 'POST':
        if 'arquivo' not in request.files:
            flash('Nenhum arquivo enviado', 'danger')
            return redirect(request.url)
        
        file = request.files['arquivo']
        edital_id = request.form.get('edital_id')
        
        if not edital_id or file.filename == '':
            flash('Selecione um edital e um arquivo válido', 'danger')
            return redirect(request.url)

        tipo_importacao = request.form.get('tipo_importacao', 'padrao')


        # Determine File Type
        is_excel = file.filename.lower().endswith(('.xlsx', '.xls'))
        csv_input = []
        
        if is_excel:
            try:
                from openpyxl import load_workbook
                wb = load_workbook(filename=file)
                ws = wb.active
                
                # Iterator to list of dicts
                rows = list(ws.iter_rows(values_only=True))
                if not rows:
                    flash('Arquivo Excel vazio.', 'danger')
                    return redirect(request.url)
                    
                header = list(rows[0])
                # Normalize headers
                header = [str(h).strip() for h in header if h is not None]
                
                for row_idx, row_values in enumerate(rows[1:], start=2):
                    # Create dict from header + values
                    # Handle case where row length < header length
                    row_dict = {}
                    for i, h in enumerate(header):
                        val = row_values[i] if i < len(row_values) else None
                        row_dict[h] = str(val).strip() if val is not None else ''
                    
                    # Add line_num for logging compatibility
                    row_dict['_line_num'] = row_idx
                    csv_input.append(row_dict)
                    
                headers = header
            except Exception as e:
                flash(f'Erro ao ler Excel: {str(e)}', 'danger')
                return redirect(request.url)

        else:
            # CSV Logic (Updated for Consistency)
            # Read content
            file_bytes = file.stream.read()
            text_content = ""
            try:
                text_content = file_bytes.decode("utf-8")
            except UnicodeDecodeError:
                text_content = file_bytes.decode("latin-1")

            # Detect Delimiter
            try:
                dialect = csv.Sniffer().sniff(text_content[:1024], delimiters='\t;,')
                delimiter = dialect.delimiter
            except:
                delimiter = ';' # Fallback
            
            # Force TAB if user implies Copy-Paste from HTML/Excel which is often TAB
            if '\t' in text_content[:100]: delimiter = '\t'

            stream = io.StringIO(text_content, newline=None)
            reader = csv.DictReader(stream, delimiter=delimiter)
            
            # Normalize Headers (Strip Bom, WhiteSpace, LowerCase)
            if reader.fieldnames:
                reader.fieldnames = [f.strip().replace('\ufeff', '') for f in reader.fieldnames]
            
            headers = reader.fieldnames or []
            
            # Convert to list to unify processing (and add line_num)
            for i, row in enumerate(reader, start=1):
                row['_line_num'] = i + 1 # Header is 1
                csv_input.append(row)

        # Validate Headers (Common)
        required_padrao = ['Tipo Vínculo', 'Tipo Vinculo']
        # FA: agencia_fomento, SEI, Projeto, formulario, cpf...
        # We check minimal FA columns to identify or assume user selected correct type
        
        if tipo_importacao == 'padrao':
            if not any(h in headers for h in required_padrao):
                  flash(f'Erro: Cabeçalho inválido para Padrão CAPES. Colunas detectadas: {headers}.', 'danger')
                  return redirect(request.url)
        elif tipo_importacao == 'fa':
             # Check for at least one FA specific column to confirm
             if 'nome_bolsista' not in headers and 'cpf' not in headers:
                  flash(f'Erro: Cabeçalho inválido para Padrão FA. Verifique se as colunas (cpf, nome_bolsista, etc) estão corretas. Detectado: {headers}', 'danger')
                  return redirect(request.url)

        sucesso = 0
        erros = 0
        log = []
        
        edital = Edital.query.get(edital_id)
            
        # Helper to normalize map
        def normalize_map(items):
            m = {}
            for x in items:
                m[x.nivel.upper()] = x
                if 'DOCTOR' in x.nivel.upper() or 'DOUTOR' in x.nivel.upper(): m['DOUTORADO'] = x
                if 'MASTER' in x.nivel.upper() or 'MESTR' in x.nivel.upper(): m['MESTRADO'] = x
            return m
        
        modalidades_map = normalize_map(edital.modalidades)

        for row in csv_input:
            row_num = row.get('_line_num', 0)
            try:
                if tipo_importacao == 'fa':
                     novo = processar_importacao_fa(row, edital, modalidades_map, log, row_num)
                     if novo:
                         db.session.add(novo)
                         sucesso += 1
                     else:
                         erros += 1 # Logged inside helper
                elif tipo_importacao == 'posdoc':
                    try:
                        # COLUMNS: SEI, Residente, Programa, Campus, Projeto, Bolsa (sim/não)
                        nome = (row.get('Residente') or 'Nome Desconhecido').strip()
                        if not nome or nome == 'Nome Desconhecido':
                            raise ValueError("Campo 'Residente' obrigatório.")

                        sei = (row.get('SEI') or '').strip()
                        projeto = (row.get('Projeto') or '').strip()
                        
                        # Parsing Bolsa (sim/não)
                        bolsa_raw = (row.get('Bolsa (sim/não)') or row.get('Bolsa') or '').strip().lower()
                        recebe_bolsa = bolsa_raw in ['sim', 's', 'yes', 'true', '1']
                        
                        # Parsing Programa & Campus
                        # Tenta localizar o programa acadêmico pelo nome ou sigla.
                        # O Campus é utilizado como filtro adicional para evitar ambiguidades.
                        prog_nome = (row.get('Programa') or '').strip()
                        campus_nome = (row.get('Campus') or '').strip()
                        
                        programa = None
                        if prog_nome:
                            # Try to find by Name or Sigla
                            # Optionally filter by Campus if provided
                            query = ProgramaAcademico.query.filter(
                                (ProgramaAcademico.nome_programa.ilike(f"%{prog_nome}%")) | 
                                (ProgramaAcademico.sigla_programa == prog_nome)
                            )
                            if campus_nome:
                                query = query.join(Campus).filter(Campus.nome.ilike(f"%{campus_nome}%"))
                                
                            programa = query.first()
                            
                            if not programa:
                                log.append(f"Aviso (Linha {row_num}): Programa '{prog_nome}' não encontrado. Vínculo pendente.")

                        # Modality Strategy: Find 'Pós-Doutorado' based on text pattern.
                        # Busca qualquer modalidade que contenha 'POS' ou 'DOC' no mapa normalizado.
                        mod_posdoc = None
                        for txt, m in modalidades_map.items():
                            if 'POS' in txt or 'DOC' in txt:
                                mod_posdoc = m
                                break
                        if not mod_posdoc:
                            # Fallback to first available if strictly necessary? 
                            # Better to error if no suitable modality fits?
                            # For now, pick first to ensure import works if any modality exists.
                            if edital.modalidades:
                                mod_posdoc = edital.modalidades[0]
                            else:
                                raise ValueError("Edital não possui modalidades cadastradas.")

                        novo = Bolsista(
                            edital_id=edital.id,
                            modalidade_id=mod_posdoc.id,
                            programa_id=programa.id if programa else None,
                            campus=campus_nome,       # Legacy / Fallback
                            programa=prog_nome,       # Legacy / Fallback
                            nome=nome,
                            processo_sei=sei,
                            projeto_pesquisa=projeto, # NEW Field
                            recebe_bolsa=recebe_bolsa,# NEW Field
                            # Defaults required by DB constraints
                            data_inicio_bolsa=date.today(),
                            data_fim_bolsa=date.today(),
                            meses_duracao=12,
                            cpf=None # Allow NULL
                        )
                        db.session.add(novo)
                        sucesso += 1
                        
                    except Exception as e:
                        erros += 1
                        log.append(f"Linha {row_num}: {str(e)}")

                else:
                    # IMPORTACAO PADRAO (CAPES)
                    # 1. PARSE PROGRAM & CAMPUS from "Tipo Vínculo"
                    vinculo = row.get('Tipo Vínculo') or row.get('Tipo Vinculo')
                    if not vinculo: 
                        continue # Skip empty lines

                    # Extract Code: look for pattern digits-P-digits
                    # Ex: "Discente ... - 40006018008P6 - ..."
                    import re
                    match = re.search(r'\b(\d+[A-Z]?\d+)\b', vinculo) 
                    # Code is usually long. e.g. 40006018008P6 (13 chars)
                    # Improve regex: 
                    # Use split strategy as backup
                    prog_code = None
                    if match:
                        prog_code = match.group(1)
                    else:
                        parts = vinculo.split(' - ')
                        for p in parts:
                            if len(p) > 8 and any(c.isdigit() for c in p):
                                prog_code = p.strip()
                                break
                    
                    if not prog_code:
                        # User Request: Not mandatory. Set None if not found.
                        programa = None
                        log.append(f"Aviso (Linha {row_num}): Código do programa não encontrado. Vínculo pendente.")
                    else:
                        programa = ProgramaAcademico.query.filter_by(codigo_programa=prog_code).first()
                        if not programa:
                            # Code found but not in DB
                            programa = None
                            log.append(f"Aviso (Linha {row_num}): Programa '{prog_code}' não existe. Vínculo pendente.")

                    # 2. PARSE MODALIDADE
                    mod_text = (row.get('Modalidade') or '').strip().upper()
                    modalidade = modalidades_map.get(mod_text)
                    if not modalidade:
                        if 'DOUTOR' in mod_text: modalidade = modalidades_map.get('DOUTORADO')
                        elif 'MESTR' in mod_text: modalidade = modalidades_map.get('MESTRADO')
                    
                    if not modalidade:
                        raise ValueError(f"Modalidade '{mod_text}' não encontrada no Edital {edital.numero}")

                    # 3. PARSE BENEFICIARIO (CPF - NOME)
                    benef = row.get('Beneficiário') or row.get('Beneficiario') # '123.456... - NAME'
                    if ' - ' in benef:
                        cpf_raw, nome = benef.split(' - ', 1)
                    else:
                        cpf_raw = benef # Maybe just CPF?
                        nome = "Nome Desconhecido" # Should allow user to fix?
                    
                    cpf = cpf_raw.strip()
                    nome = nome.strip()
                    
                    # Check duplicate in general or edital?
                    # Ideally CPF is unique per person.
                    exists = Bolsista.query.filter_by(cpf=cpf).first()
                    if exists:
                        # Log only or skip?
                        # Usually skip to avoid dupes.
                        raise ValueError(f"CPF {cpf} já existente no sistema (Bolsista: {exists.nome})")

                    # 4. PARSE VIGENCIA
                    vigencia = row.get('Vigência') or row.get('Vigencia')
                    if ' - ' in vigencia:
                        inicio_str, fim_str = vigencia.split(' - ')
                        dt_inicio = datetime.strptime(inicio_str.strip(), '%d/%m/%Y').date()
                        dt_fim = datetime.strptime(fim_str.strip(), '%d/%m/%Y').date()
                        
                        diff = relativedelta(dt_fim, dt_inicio)
                        meses = diff.years * 12 + diff.months
                        if diff.days > 15: meses += 1
                    else:
                        # Fallback defaults?
                        raise ValueError("Formato de vigência inválido (Esperado: DD/MM/AAAA - DD/MM/AAAA)")

                    # CREATE
                    novo = Bolsista(
                        edital_id=edital.id,
                        modalidade_id=modalidade.id,
                        programa_id=programa.id if programa else None,
                        nome=nome,
                        cpf=cpf,
                        email="", # Empty for now
                        data_inicio_bolsa=dt_inicio,
                        data_fim_bolsa=dt_fim,
                        meses_duracao=meses,
                        ativo=True
                    )
                    db.session.add(novo)
                    sucesso += 1
                
            except Exception as e:
                erros += 1
                log.append(f"Linha {row_num}: {str(e)}")
        
        db.session.commit()
        resultado = {'sucesso': sucesso, 'erro': erros, 'log_erros': log}
        if sucesso > 0:
            flash(f'Processamento finalizado. {sucesso} importados.', 'success')
        else:
             flash('Processamento finalizado sem sucessos.', 'warning')

    return render_template('bolsistas/importar.html', editais=editais, resultado=resultado)


# Helper function for FA import
def processar_importacao_fa(row, edital, modalidades_map, log, row_num):
    # Mapping: agencia_fomento, SEI, Projeto, formulario, cpf, nome_bolsista, Nível, valor, tipo de conta, banco, agência, conta, Orientador, Data de Ingresso, tema, Data Prevista para Conclusão do Curso, Relatório
    
    try:
        # 1. Basic Fields
        cpf = (row.get('cpf') or '').strip()
        nome = (row.get('nome_bolsista') or 'Nome Desconhecido').strip()
        
        if not cpf:
             # Skip if no CPF
             return None

        # Check existence
        exists = Bolsista.query.filter_by(cpf=cpf).first()
        if exists:
             raise ValueError(f"CPF {cpf} já existente (Bolsista: {exists.nome})")

        # 2. Modalidade (Nível)
        mod_text = (row.get('Nível') or '').strip().upper()
        modalidade = modalidades_map.get(mod_text)
        if not modalidade:
                if 'DOUTOR' in mod_text: modalidade = modalidades_map.get('DOUTORADO')
                elif 'MESTR' in mod_text: modalidade = modalidades_map.get('MESTRADO')
        
        if not modalidade:
            # Fallback or Error? User said "dados não são obrigatórios", but modalidade is required for DB relationship.
            # We will try to guess or error. Error is safer.
            raise ValueError(f"Nível '{mod_text}' não encontrado no Edital.")

        # 3. Dates
        # Data de Ingresso -> Assume Inicio Bolsa + Inicio Curso
        # Data Prevista -> Previsao Defesa
        # Vigência not explicitly in FA columns -> Default to 12 months or Calc from dates?
        # User said "seguem a mesma dinâmica".
        
        fmt = '%d/%m/%Y'
        dt_ingresso_raw = row.get('Data de Ingresso')
        dt_prevista_raw = row.get('Data Prevista para Conclusão do Curso')
        
        dt_inicio = date.today()
        if dt_ingresso_raw:
            try:
                dt_inicio = datetime.strptime(str(dt_ingresso_raw).strip(), fmt).date()
            except:
                pass # Keep today or None? DB requires Not Null for data_inicio_bolsa
                
        dt_previsao = None
        if dt_prevista_raw:
             try:
                 dt_previsao = datetime.strptime(str(dt_prevista_raw).strip(), fmt).date()
             except:
                 pass

        # Calculate End Date (Sem vigencia explicita, usamos 12 meses ou ate a previsao?)
        # Let's use 12 months default as common practice if not specified
        meses = 12
        from dateutil.relativedelta import relativedelta
        dt_fim = dt_inicio + relativedelta(months=meses)
        
        # 4. Banking & Others
        banco = (row.get('banco') or '').strip()
        agencia = (row.get('agência') or '').strip()
        conta = (row.get('conta') or '').strip()
        tipo_conta = (row.get('tipo de conta') or '').strip()
        
        orientador = (row.get('Orientador') or '').strip()
        processo_sei = (row.get('SEI') or '').strip()
        num_form = (row.get('formulario') or '').strip()
        
        # Comments
        comentarios = []
        if row.get('agencia_fomento'): comentarios.append(f"Fomento: {row.get('agencia_fomento')}")
        if row.get('Projeto'): comentarios.append(f"Projeto: {row.get('Projeto')}")
        if row.get('tema'): comentarios.append(f"Tema: {row.get('tema')}")
        if row.get('Relatório'): comentarios.append(f"Relatório: {row.get('Relatório')}")
        
        comments_str = " | ".join(comentarios)

        # 5. Create Object
        novo = Bolsista(
            edital_id=edital.id,
            modalidade_id=modalidade.id,
            programa_id=None, # Not in FA columns explicitly? Or use Project?
            nome=nome,
            cpf=cpf,
            email="",
            data_inicio_bolsa=dt_inicio,
            data_fim_bolsa=dt_fim,
            meses_duracao=meses,
            ativo=True,
            data_inicio_curso=dt_inicio,
            previsao_defesa=dt_previsao,
            banco=banco,
            agencia=agencia,
            conta=conta,
            tipo_conta=tipo_conta,
            orientador=orientador,
            processo_sei=processo_sei,
            numero_formulario=num_form,
            comentarios=comments_str
        )
        return novo

    except Exception as e:
        log.append(f"Linha {row_num}: {str(e)}")
        return None

# [NOVO V11.4] Processador de Contexto para Notificações (Sidebar)
# ---------------------------------------------------------------------
# Esta função é um "Context Processor". O Flask executa ela antes de renderizar
# qualquer template. O objetivo é injetar variáveis globais (neste caso, a contagem de alertas)
# para que estejam disponíveis em todas as páginas (como na barra lateral "base.html").
@app.context_processor
def inject_alerts():
    from datetime import date, timedelta
    
    # Datas de referência
    hoje = date.today()
    proximos_30_dias = hoje + timedelta(days=30) # Definimos o horizonte de alertas para 30 dias
    
    # Lógica para Bolsistas [V11.4.1]
    # Calculamos o primeiro e o último dia do mês atual para filtrar bolsistas que vencem este mês.
    import calendar
    ultimo_dia_mes = calendar.monthrange(hoje.year, hoje.month)[1]
    fim_mes = date(hoje.year, hoje.month, ultimo_dia_mes)

    try:
        # 1. Editais a Vencer
        # Filtra editais cuja data final está entre hoje e daqui a 30 dias.
        count_expiring = Edital.query.filter(
            Edital.data_fim >= hoje,
            Edital.data_fim <= proximos_30_dias
        ).count()
        
        # 2. Pendência de Prestação de Contas
        # Filtra editais que JÁ venceram (data_fim < hoje) e ainda não foram prestados contas.
        count_pending = Edital.query.filter(
            Edital.data_fim < hoje,
            Edital.prestacao_contas == False
        ).count()
        
        # 3. Bolsas Finalizando (Mês Atual) [V11.4.1]
        # Filtra bolsistas ATIVOS cuja bolsa termina dentro deste mês.
        count_bolsistas = Bolsista.query.filter(
            Bolsista.data_fim_bolsa >= hoje,
            Bolsista.data_fim_bolsa <= fim_mes,
            Bolsista.ativo == True 
        ).count()
        
        # Soma total para exibir no badge (círculo vermelho)
        total_alerts = count_expiring + count_pending + count_bolsistas
        return dict(total_alerts=total_alerts)
    except Exception as e:
        # Em caso de erro (ex: tabela ainda não criada), retorna 0 para não quebrar o site.
        return dict(total_alerts=0)

# [NOVO V11.4] Página de Relatório de Ações Pendentes
# ---------------------------------------------------------------------
# Rota responsável por exibir a página detalhada dos alertas.
# Busca os dados completos no banco para listar na tela.
@app.route('/alertas')
def alertas_index():
    from datetime import date, timedelta
    import calendar
    
    hoje = date.today()
    proximos_30_dias = hoje + timedelta(days=30)
    
    # Cálculo do fim do mês
    ultimo_dia_mes = calendar.monthrange(hoje.year, hoje.month)[1]
    fim_mes = date(hoje.year, hoje.month, ultimo_dia_mes)
    
    # 1. Busca Editais a Vencer (.all() retorna a lista de objetos, não só a contagem)
    expiring_editais = Edital.query.filter(
        Edital.data_fim >= hoje,
        Edital.data_fim <= proximos_30_dias
    ).all()
    
    # 2. Busca Pendências de Contas
    pending_accountability = Edital.query.filter(
        Edital.data_fim < hoje,
        Edital.prestacao_contas == False
    ).all()
    
    # 3. Busca Bolsistas Finalizando [V11.4.1]
    alert_bolsistas = Bolsista.query.filter(
        Bolsista.data_fim_bolsa >= hoje,
        Bolsista.data_fim_bolsa <= fim_mes,
        Bolsista.ativo == True
    ).all()
    
    # Renderiza o template HTML passando as listas de dados
    return render_template('alertas/index.html', 
                         expiring=expiring_editais, 
                         pending=pending_accountability,
                         bolsistas=alert_bolsistas)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # For development, use: app.run(debug=True)
    # For production, use production.py with Waitress server
    app.run(debug=True, port=5022)
