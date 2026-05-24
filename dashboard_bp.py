from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from models import db, Bolsista, Edital, Modalidade, ProgramaAcademico, Campus, LogAutomacao, UIMementoHistory
from sqlalchemy import func, text, or_
from datetime import date, datetime
import time
from decimal import Decimal
from services.financeiro_service import FinanceiroService

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

from decorators import require_role

@dashboard_bp.route('/Coordenacao')
@login_required
def coordenacao():
    from flask_login import current_user
    from models import ProgramaAcademico
    
    if current_user.role != 'coordenador_programa':
        return render_template('dashboard/modern.html', error="Acesso restrito a Coordenadores.")

    if not current_user.programa_id:
            return render_template('dashboard/modern.html', error="Usuário sem programa vinculado.")
        
    prog = ProgramaAcademico.query.get(current_user.programa_id)
    if not prog:
        return render_template('dashboard/modern.html', error="Programa não encontrado.")

    stats, alerts = get_program_metrics(prog.id)
    scope_title = f"{prog.sigla_programa} - {prog.nome_programa}"
            
    return render_template('dashboard/coordinator.html', title=scope_title, stats=stats, alerts=sorted(alerts, key=lambda x: x['days']))

@dashboard_bp.route('/Direcao')
@login_required
def direcao():
    from flask_login import current_user
    from models import Bolsista, ProgramaAcademico, Campus, DadosSociais, MobilidadeInternacional
    from flask import request
    from sqlalchemy import text # correct import here
    from datetime import date, timedelta
    
    if current_user.role != 'diretor_campus':
         return render_template('dashboard/modern.html', error="Acesso restrito a Diretores.")

    if not current_user.campus_id:
            return render_template('dashboard/modern.html', error="Usuário sem campus vinculado.")
        
    campus = Campus.query.get(current_user.campus_id)
    
    # Check for filtered program
    selected_prog_id = request.args.get('programa_id', type=int)
    
    if selected_prog_id:
        # Validate if program belongs to campus
        prog = ProgramaAcademico.query.get(selected_prog_id)
        if prog and prog.campus_id == campus.id:
            # Render Coordinator-style Dashboard for this Program
            stats, alerts = get_program_metrics(prog.id)
            title = f"{prog.sigla_programa} - {prog.nome_programa}"
            return render_template('dashboard/coordinator.html', 
                                   title=title, 
                                   stats=stats, 
                                   alerts=sorted(alerts, key=lambda x: x['days']),
                                   panel_subtitle="Painel do(a) Diretor(a)")
        else:
            return render_template('dashboard/modern.html', error="Programa inválido ou não pertence ao seu campus.")

    # Default View: Aggregated for Campus
    scope_title = f"Campus {campus.nome}" if campus else "Campus não encontrado"
    current_year = date.today().year
    
    stats = {}
    alerts = []
    
    if campus:
        # Aggregated Data Fetching
        from sqlalchemy import not_
        progs = ProgramaAcademico.query.filter(
            ProgramaAcademico.campus_id == campus.id,
            not_(ProgramaAcademico.nome_programa.ilike('%*%'))
        ).all()
        prog_ids = [p.id for p in progs]
        
        if not prog_ids:
             return render_template('dashboard/coordinator.html', title=scope_title, stats={}, alerts=[])

        # 1. Counts
        bol_list = Bolsista.query.filter(Bolsista.programa_id.in_(prog_ids), Bolsista.ativo==True).all()
        
        stats['bolsistas_count'] = len(bol_list)
        stats['bolsistas_count'] = len(bol_list)
        
        # 2. Financials (Aggregated)
        inv_bolsistas = sum(b.modalidade.valor_mensal for b in bol_list if b.recebe_bolsa and b.modalidade)
        stats['invest_mensal_bolsistas'] = inv_bolsistas
        
        # 2. Financials (Aggregated)

        # 3. Vagas Ociosas (Aggregated)
        total_cotas = 0
        try:
            sql_cotas = "SELECT SUM(qtd_concedida) FROM distribuicao_cotas WHERE programa_id IN :pids"
            # SQLAlchemy handles tuple binding for IN clause manually or via expand_op? 
            # Safer to loop or use ORM if possible. 
            # Or use text with tuple:
            result = db.session.execute(text("SELECT SUM(qtd_concedida) FROM distribuicao_cotas WHERE programa_id = ANY(:pids)"), {'pids': prog_ids}).scalar()
            # Note: ANY(:pids) is postgres specific. IN :pids might not work directly with text().
            # Let's simple loop since number of programs per campus is small (usually < 20).
            # actually better:
            # result = db.session.execute(text(f"SELECT SUM(qtd_concedida) FROM distribuicao_cotas WHERE programa_id IN ({','.join(map(str, prog_ids))})")).scalar()
            # safe enough since prog_ids are ints from DB.
            if prog_ids:
                safe_ids = ",".join(map(str, prog_ids))
                sql_cotas = f"SELECT SUM(qtd_concedida) FROM distribuicao_cotas WHERE programa_id IN ({safe_ids})"
                result = db.session.execute(text(sql_cotas)).scalar()
                if result: total_cotas = int(result)
        except: pass
        
        if total_cotas > 0:
            stats['vagas_ociosas'] = f"{max(0, total_cotas - len(bol_list))} (de {total_cotas})"
        else:
            stats['vagas_ociosas'] = "N/A"

        # 4. PROAP (Aggregated)
        proap_total = Decimal('0')
        try:
             if prog_ids:
                 safe_ids = ",".join(map(str, prog_ids))
                 sql_proap = f"""
                    SELECT SUM(d.valor_distribuido)
                    FROM proap_distribuicoes d
                    JOIN proap_repasses r ON d.repasse_id = r.id
                    WHERE d.programa_id IN ({safe_ids}) AND r.ano = :year
                 """
                 res_proap = db.session.execute(text(sql_proap), {'year': current_year}).scalar()
                 if res_proap: proap_total = Decimal(str(res_proap))
        except: pass
        
        stats['proap_total'] = proap_total
        stats['ano_atual'] = current_year

        # 5. Diversity & Inter (Aggregated)
        stats['diversidade_count'] = db.session.query(DadosSociais).join(Bolsista).filter(Bolsista.programa_id.in_(prog_ids), Bolsista.ativo == True).count()
        stats['inter_count'] = db.session.query(MobilidadeInternacional).join(Bolsista).filter(Bolsista.programa_id.in_(prog_ids), Bolsista.ativo == True).count()

        # 6. Alerts
        limit_date = date.today() + timedelta(days=90)
        for b in bol_list:
            if b.data_fim_bolsa and b.data_fim_bolsa <= limit_date:
                # Use programa_link relationship
                p_sigla = b.programa_link.sigla_programa if b.programa_link else '-'
                p_name = b.programa_link.nome_programa if b.programa_link else '-'
                
                alerts.append({
                    'name': b.nome, 
                    'type': 'Discente', 
                    'date': b.data_fim_bolsa, 
                    'days': (b.data_fim_bolsa - date.today()).days, 
                    'sei': b.processo_sei, 
                    'form': b.numero_formulario,
                    'prog_sigla': p_sigla,
                    'prog_name': p_name
                })

    return render_template('dashboard/coordinator.html', 
                           title=scope_title, 
                           stats=stats, 
                           alerts=sorted(alerts, key=lambda x: x['days']),
                           panel_subtitle="Painel do(a) Diretor(a)")

@dashboard_bp.route('/Master')
@login_required
def master():
    """
    Dashboard Cockpit (NAPI-Robótica): Visão de Alto Nível para a Coordenação Geral.
    Implementa a estética Neon e o monitoramento do PI 33/2025.
    """
    if current_user.role != 'master' and current_user.role != 'admin':
        return redirect(url_for('index'))

    # Coleta Métricas do FinanceiroService (DNA do NAPI)
    metrics = FinanceiroService.get_project_metrics()
    
    # Busca snapshots de integridade recentes
    recente_mementos = UIMementoHistory.query.order_by(UIMementoHistory.timestamp.desc()).limit(5).all()
    
    return render_template('dashboard/master_neon.html', 
                           title="Cockpit NAPI-Robótica", 
                           metrics=metrics, 
                           mementos=recente_mementos)


def get_program_metrics(programa_id):
    """
    Helper para calcular métricas de um programa específico.
    Reutilizado por Coordenadores e Diretores (quando filtram).
    """
    from models import Bolsista, DadosSociais, MobilidadeInternacional
    from datetime import date, timedelta
    from sqlalchemy import text

    stats = {}
    alerts = []
    current_year = date.today().year

    # 1. Fetch Lists (Active)
    # 1. Fetch Lists (Active)
    bolsistas = Bolsista.query.filter_by(programa_id=programa_id, ativo=True).all()
    
    stats['bolsistas_count'] = len(bolsistas)
    stats['bolsistas_count'] = len(bolsistas)
    
    # 2. Financials
    inv_bolsistas = sum(b.modalidade.valor_mensal for b in bolsistas if b.recebe_bolsa and b.modalidade)
    stats['invest_mensal_bolsistas'] = inv_bolsistas
    
    # 2. Financials

    # 3. Vagas Ociosas
    total_cotas = 0
    try:
        sql_cotas = "SELECT SUM(qtd_concedida) FROM distribuicao_cotas WHERE programa_id = :pid"
        result = db.session.execute(text(sql_cotas), {'pid': programa_id}).scalar()
        if result: total_cotas = int(result)
    except: pass
    
    if total_cotas > 0:
        stats['vagas_ociosas'] = f"{max(0, total_cotas - len(bolsistas))} (de {total_cotas})"
    else:
        stats['vagas_ociosas'] = "N/A"

    # 4. PROAP
    proap_total = Decimal('0')
    try:
         sql_proap = """
            SELECT SUM(d.valor_distribuido)
            FROM proap_distribuicoes d
            JOIN proap_repasses r ON d.repasse_id = r.id
            WHERE d.programa_id = :pid AND r.ano = :year
         """
         res_proap = db.session.execute(text(sql_proap), {'pid': programa_id, 'year': current_year}).scalar()
         if res_proap: proap_total = Decimal(str(res_proap))
    except: pass
    
    stats['proap_total'] = proap_total
    stats['ano_atual'] = current_year

    # 5. Diversity & Inter
    stats['diversidade_count'] = db.session.query(DadosSociais).join(Bolsista).filter(Bolsista.programa_id == programa_id, Bolsista.ativo == True).count()
    stats['inter_count'] = db.session.query(MobilidadeInternacional).join(Bolsista).filter(Bolsista.programa_id == programa_id, Bolsista.ativo == True).count()

    # 6. Alerts
    limit_date = date.today() + timedelta(days=90)
    
    # Fetch program object for metadata (since we are inside helper, program is known by ID, but let's query just in case or use relationship)
    # Actually, we have resident object which has relationship to program
    
    for b in bolsistas:
        if b.data_fim_bolsa and b.data_fim_bolsa <= limit_date:
            try:
                p_sigla = b.programa_link.sigla_programa if b.programa_link else '-'
                p_name = b.programa_link.nome_programa if b.programa_link else '-'
            except:
                p_sigla = '-'
                p_name = '-'
                
            alerts.append({
                'name': b.nome, 
                'type': 'Discente', 
                'date': b.data_fim_bolsa, 
                'days': (b.data_fim_bolsa - date.today()).days, 
                'sei': b.processo_sei, 
                'form': b.numero_formulario,
                'prog_sigla': p_sigla,
                'prog_name': p_name
            })

    return stats, alerts


@dashboard_bp.route('/advanced')
@login_required
def advanced():
    """Renderiza a página do dashboard avançado."""
    # 1. Totais Gerais
    total_ativos = Bolsista.query.filter_by(ativo=True).count()
    total_inativos = Bolsista.query.filter_by(ativo=False).count()
    total_editais = Edital.query.count()
    
    # 2. Distribuição por Modalidade (Apenas Ativos)
    modalidades_query = db.session.query(
        Modalidade.nivel, func.count(Bolsista.id)
    ).join(Bolsista).filter(Bolsista.ativo == True).group_by(Modalidade.nivel).all()
    
    # Preparar dados para Gráfico de Barras CSS
    total_mod = sum(m[1] for m in modalidades_query)
    modalidade_data = []
    colors = ['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b', '#858796', '#5a5c69', '#2c9faf']
    
    for i, (nivel, count) in enumerate(modalidades_query):
        pct = (count / total_mod * 100) if total_mod > 0 else 0
        modalidade_data.append({
            'label': nivel,
            'count': count,
            'pct': pct,
            'color': colors[i % len(colors)]
        })
        
    # Ordenar por contagem decrescente
    modalidade_data.sort(key=lambda x: x['count'], reverse=True)

    # 3. Evolução Temporal (Inícios de Bolsa por Mês)
    dates = db.session.query(Bolsista.data_inicio_bolsa).filter(Bolsista.ativo == True).all()
    
    from collections import Counter
    evolution_counts = Counter()
    
    for d in dates:
        if d[0]:
            key = d[0].strftime('%Y-%m')
            evolution_counts[key] += 1
            
    evolution_sorted = dict(sorted(evolution_counts.items()))

    stats = {
        'summary': {
            'active_scholars': total_ativos,
            'inactive_scholars': total_inativos,
            'total_edicts': total_editais
        },
        'modalidade_data': modalidade_data,
        'evolution': evolution_sorted
    }
    
    return render_template('dashboard/advanced.html', stats=stats)

@dashboard_bp.route('/api/stats')
@login_required
def get_stats():
    """
    API mantida para compatibilidade ou uso externo secundário.
    """
    return jsonify({'status': 'ok'})

@dashboard_bp.route('/data')
@login_required
def dashboard_data_api():
    """
    Retorna os dados reais agregados do banco de dados para os gráficos do Dashboard.
    Refatorado para priorizar NAPI-Robótica (Fase 2.2).
    """
    from models import Bolsista, Modalidade, ProgramaAcademico, Campus, Edital
    from sqlalchemy import func, text
    import time
    start_time = time.time()
    
    # 1. Financeiro: Por Nível (Valores em R$)
    financeiro_por_nivel = db.session.query(
        Modalidade.nivel, 
        func.sum(Modalidade.valor_mensal)
    ).join(Bolsista, Modalidade.id == Bolsista.modalidade_id)\
     .filter(Bolsista.ativo == True).group_by(Modalidade.nivel).all()

    # 2. Financeiro: Por Campus
    financeiro_por_campus = db.session.query(
        Campus.sigla_campus, 
        func.sum(Modalidade.valor_mensal)
    ).join(ProgramaAcademico, Campus.id == ProgramaAcademico.campus_id)\
     .join(Bolsista, ProgramaAcademico.id == Bolsista.programa_id)\
     .join(Modalidade, Bolsista.modalidade_id == Modalidade.id)\
     .filter(Bolsista.ativo == True).group_by(Campus.sigla_campus).all()

    # 3. Financeiro: Por Edital
    financeiro_por_edital_raw = db.session.query(
        Edital.numero_edital,
        Edital.ano_edital,
        Edital.descricao,
        func.sum(Modalidade.valor_mensal)
    ).join(Bolsista, Edital.id == Bolsista.edital_id)\
     .join(Modalidade, Bolsista.modalidade_id == Modalidade.id)\
     .filter(Bolsista.ativo == True).group_by(Edital.numero_edital, Edital.ano_edital, Edital.descricao).all()
     
    financeiro_por_edital = []
    for row in financeiro_por_edital_raw:
        label = f"{row[0] or 'S/N'}"
        if row[1]: label += f" / {row[1]}"
        if row[2]: label += f" - {row[2]}"
        financeiro_por_edital.append((label, row[3]))
      
    # 5. Ocupação de Vagas (Foco Editais 2026)
    try:
        # Busca editais de 2026
        editais_2026 = Edital.query.filter(Edital.ano_edital == 2026).all()
        ocupacao_list = []
        
        for ed in editais_2026:
            # Vagas ofertadas via Modalidades
            total_vagas = db.session.query(func.sum(Modalidade.vagas)).filter(Modalidade.edital_id == ed.id).scalar() or 0
            ativos = Bolsista.query.filter_by(edital_id=ed.id, ativo=True).count()
            
            label_edital = f"Edital {ed.numero_edital or ed.numero}/{ed.ano_edital}"
            
            ocupacao_list.append({
                "label": label_edital,
                "vagas": total_vagas,
                "vacant": max(0, total_vagas - ativos),
                "preenchido_pct": (ativos / total_vagas * 100) if total_vagas > 0 else 0
            })
    except:
        ocupacao_list = []

    # 6. Montagem do Payload Final
    real_payload = {
        "financeiro": {
            "mensal_atual": sum(item[1] for item in financeiro_por_nivel) if financeiro_por_nivel else 0.0,
            "por_nivel": [{"label": item[0], "value": float(item[1])} for item in financeiro_por_nivel],
            "por_campus": [{"label": item[0], "value": float(item[1])} for item in financeiro_por_campus],
            "por_edital": [{"label": item[0], "value": float(item[1])} for item in financeiro_por_edital]
        },
        "ocupacao": ocupacao_list
    }
    
    duration = time.time() - start_time
    if duration > 0.200:
        print(f"⚠️ [SLOW QUERY] Dashboard Data API levou {duration:.4f}s")
    
    return jsonify(real_payload)

@dashboard_bp.route('/data/financeiro')
@login_required
def dashboard_financeiro_api():
    """Retorna os dados financeiros consolidados (PI 33/2025)."""
    start_time = time.time()
    
    metrics = FinanceiroService.get_project_metrics()
    
    duration = time.time() - start_time
    if duration > 0.200:
        print(f"⚠️ [SLOW QUERY] Dashboard Financeiro levou {duration:.4f}s")
        
    return jsonify({
        "lote1": metrics['lote30'],
        "lote2": metrics['lote5du'],
        "total_folha": metrics['total_folha'],
        "saldo_convenio": metrics['saldo_convenio'],
        "burn_rate": int(metrics['saldo_convenio'] / metrics['total_folha']) if metrics['total_folha'] > 0 else 0,
        "vencimento_lote2": "5º DU"
    })

@dashboard_bp.route('/data/integridade')
@login_required
def dashboard_integridade_api():
    """
    Retorna contagem de pendências críticas via FinanceiroService.
    """
    report = FinanceiroService.get_scanner_report()
    
    return jsonify({
        "total_critico": report['total_critico'],
        "total_alertas": sum(report['detalhes'].values()) - report['total_critico'], # Simplificação
        "lista": [{"tipo": "CRÍTICO", "msg": report['msg'], "cor": "red"}] if report['total_critico'] > 0 else []
    })

@dashboard_bp.route('/sync')
@login_required
def sync_metrics():
    """
    Gatilho de Recálculo Manual com Memento Snapshot.
    """
    try:
        # 1. Salva Memento antes de qualquer operação
        memento_id = FinanceiroService.take_metrics_snapshot(user_id=current_user.id)
        
        # 2. Força recálculo (em um sistema com cache, aqui limparíamos o cache)
        # Como as queries são diretas, o recálculo acontece no próximo poll do front.
        
        return jsonify({
            "status": "success",
            "message": "Métricas atualizadas com sucesso!",
            "memento_id": memento_id
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Erro ao sincronizar: {str(e)}"
        }), 500

@dashboard_bp.route('/capes')
@login_required
def capes():
    where_clause = ""
    params = {}
    if current_user.role == 'coordenador_programa' and current_user.programa_id:
        where_clause = "AND p.id = :programa_id"
        params['programa_id'] = current_user.programa_id
    elif current_user.role == 'diretor_campus' and current_user.campus_id:
        where_clause = "AND p.campus_id = :campus_id"
        params['campus_id'] = current_user.campus_id
    
    sql = f"""
    SELECT p.id, p.nome_programa, p.codigo_programa, cp.sigla_campus, m.nivel, c.qtd_concedida,
           (SELECT COUNT(b.id) FROM bolsistas b 
            WHERE b.programa_id = p.id AND b.modalidade_id = m.id AND b.ativo = True AND b.edital_id = 14) as ocupadas
    FROM distribuicao_cotas c
    JOIN programa_academico p ON c.programa_id = p.id
    LEFT JOIN campus cp ON p.campus_id = cp.id
    JOIN modalidades m ON c.modalidade_id = m.id
    WHERE c.edital_id = 14 {where_clause}
    ORDER BY cp.sigla_campus, p.nome_programa
    """
    result = db.session.execute(text(sql), params)
    
    data_map = {}
    totais = {
        'mestrado_total': 0, 'mestrado_ocupado': 0, 'programas_mestrado': 0,
        'doutorado_total': 0, 'doutorado_ocupado': 0, 'programas_doutorado': 0,
        'ies_mestrado': 0, 'ies_doutorado': 0, 'ies_total_cotas': 0, 'ies_ocupadas': 0, 'ies_livres': 0, 'ies_programas_count': 0
    }

    for r in result:
        pid = r.id
        if pid not in data_map:
            data_map[pid] = {
                'pid': pid, 'nome': r.nome_programa, 'codigo': r.codigo_programa, 'campus': r.sigla_campus or '(IES)*',
                'mestrado': {'cota': 0, 'ocupado': 0}, 'doutorado': {'cota': 0, 'ocupado': 0}
            }
        
        is_mestrado = 'mestrado' in r.nivel.lower()
        key = 'mestrado' if is_mestrado else 'doutorado'
        
        data_map[pid][key]['cota'] += r.qtd_concedida
        data_map[pid][key]['ocupado'] += r.ocupadas
        
        # Agregação para o Dashboard Superior
        if is_mestrado:
            totais['mestrado_total'] += r.qtd_concedida
            totais['mestrado_ocupado'] += r.ocupadas
            if r.qtd_concedida > 0: totais['programas_mestrado'] += 1
        else:
            totais['doutorado_total'] += r.qtd_concedida
            totais['doutorado_ocupado'] += r.ocupadas
            if r.qtd_concedida > 0: totais['programas_doutorado'] += 1

    # Busca bolsas IES (Edital 13) se existirem para complementar o painel
    bolsistas_ies = Bolsista.query.filter_by(edital_id=13, ativo=True).all()
    
    return render_template('capes/dashboard.html', 
                           dados=sorted(data_map.values(), key=lambda x: x['nome']), 
                           totais=totais,
                           bolsistas_ies=bolsistas_ies)

@dashboard_bp.route('/api/capes/bolsistas/<int:programa_id>')
@login_required
def get_capes_bolsistas(programa_id):
    """
    API que retorna os bolsistas ativos de um programa para o modal CAPES.
    Filtra editais 13 (IES) e 14 (DS).
    """
    bolsistas = Bolsista.query.filter(
        Bolsista.programa_id == programa_id,
        Bolsista.ativo == True,
        Bolsista.edital_id.in_([13, 14])
    ).order_by(Bolsista.nome).all()
    
    data = []
    for b in bolsistas:
        # Mascarar CPF para segurança se necessário, aqui mantendo conforme JS espera
        data.append({
            'id': b.id,
            'nome': b.nome,
            'cpf': f"{b.cpf[:3]}.***.***-{b.cpf[-2:]}" if b.cpf and len(b.cpf) >= 11 else b.cpf,
            'sei': b.processo_sei or '-',
            'formulario': b.numero_formulario or '-',
            'status': 'Ativo' if b.ativo else 'Inativo'
        })
    
    return jsonify({
        'total': len(data),
        'bolsistas': data
    })

@dashboard_bp.route('/alertas')
@login_required
def alertas():
    from dateutil.relativedelta import relativedelta
    from blueprints.services.reconciliation import get_conflitos
    from utils.permissions import filter_editais_by_scope
    from sqlalchemy import extract
    
    hoje = date.today()
    marco_zero = hoje.replace(day=1)
    proximos_30_dias = hoje + relativedelta(days=30)
    
    # Parâmetros para o Controle Mensal Dinâmico (v17.0)
    mon_mes = request.args.get('mon_mes', type=int, default=hoje.month)
    mon_ano = request.args.get('mon_ano', type=int, default=hoje.year)
    
    # 1. Monitoramento Unificado (v17.0) - Unifica Ação Requerida e Monitoramento Temporal
    # --- 1. MONITORAMENTO MENSAL (Foco Exclusivo em Bolsistas) ---
    # Somente Bolsistas com encerramento previsto para o mês/ano selecionado
    query_bol_mon = Bolsista.query.filter(
        extract('month', Bolsista.data_fim_bolsa) == mon_mes,
        extract('year', Bolsista.data_fim_bolsa) == mon_ano,
        Bolsista.ativo == True
    )
    
    # 2. SCBA: Titulação Antecipada (Discentes ativos com defesa vencida)
    query_base = Bolsista.query.filter(Bolsista.ativo == True)
    
    # 3. Administrativo: Editais
    query_editais = Edital.query
    query_editais = filter_editais_by_scope(query_editais, current_user)
    
    # Filtros de Escopo para Monitoramento
    if current_user.role == 'coordenador_programa':
        query_base = query_base.filter_by(programa_id=current_user.programa_id)
        query_bol_mon = query_bol_mon.filter_by(programa_id=current_user.programa_id)
    elif current_user.role == 'diretor_campus':
        query_base = query_base.join(ProgramaAcademico).filter(ProgramaAcademico.campus_id == current_user.campus_id)
        query_bol_mon = query_bol_mon.join(ProgramaAcademico).filter(ProgramaAcademico.campus_id == current_user.campus_id)
        
    bolsistas_defesa_vencida = query_base.filter(
        Bolsista.previsao_defesa != None,
        Bolsista.previsao_defesa < hoje,
        Bolsista.data_fim_bolsa >= hoje
    ).all()
    
    expiring = query_editais.filter(Edital.data_fim >= hoje, Edital.data_fim <= proximos_30_dias).all()
    pending_editais = query_editais.filter(Edital.data_fim < hoje, Edital.prestacao_contas == False).all()
    
    # 5. Consolidar em uma lista única (Agora apenas Bolsistas por diretriz NAPI)
    consolidado_mon = []
    
    # Executar a query
    bolsistas_mon = query_bol_mon.all()
    
    for b in bolsistas_mon:
        consolidado_mon.append({
            'id': b.id,
            'nome': b.nome,
            'tipo': 'Bolsista',
            'edital': b.edital,
            'programa': b.programa_link.sigla_programa if b.programa_link else b.programa,
            'data_fim': b.data_fim_bolsa,
            'ativo': b.ativo,
            'route_edit': 'bolsistas.editar'
        })
        
    consolidado_mon.sort(key=lambda x: x['data_fim'])
    
    meses_nomes = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                   "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    anos_range = range(hoje.year - 1, hoje.year + 3)
    
    # 6. Governança de Dados: Conflitos de Identidade (Apenas para Admin/Gestor)
    grupos = []
    if current_user.role in ['admin', 'gestor']:
        grupos = get_conflitos()
    
    return render_template('alertas/index.html', 
                           monitoring_list=consolidado_mon,
                           mon_mes=mon_mes,
                           mon_ano=mon_ano,
                           meses_nomes=meses_nomes,
                           anos_range=anos_range,
                           bolsistas_defesa_vencida=bolsistas_defesa_vencida,
                           expiring=expiring,
                           pending=pending_editais,
                           grupos=grupos,
                           hoje=hoje)


@dashboard_bp.route('/alertas/exportar')
@login_required
def exportar_pendencias_excel():
    import pandas as pd
    from io import BytesIO
    from datetime import date
    
    hoje = date.today()
    marco_zero = hoje.replace(day=1)
    
    query = Bolsista.query.filter(Bolsista.ativo == True)
    if current_user.role == 'coordenador_programa':
        query = query.filter_by(programa_id=current_user.programa_id)
    elif current_user.role == 'diretor_campus':
        query = query.join(ProgramaAcademico).filter(ProgramaAcademico.campus_id == current_user.campus_id)
        
    pendencias = [b for b in query.all() if b.data_fim_bolsa and b.data_fim_bolsa < marco_zero]

    data = []
    for b in pendencias:
        # Formatação atômica para o Excel
        edital_nome = "Institucional"
        if b.edital:
            edital_nome = f"{b.edital.numero_edital or b.edital.numero}"
            if b.edital.ano_edital: edital_nome += f" / {b.edital.ano_edital}"

        data.append({
            'Campus': b.programa_link.campus.sigla_campus if b.programa_link and b.programa_link.campus else 'N/A',
            'Programa': b.programa_link.sigla_programa if b.programa_link else 'N/A',
            'Discente': b.nome,
            'CPF': b.cpf,
            'Edital': edital_nome,
            'Vencimento': b.data_fim_bolsa.strftime('%d/%m/%Y'),
            'Valor Mensal': b.modalidade.valor_mensal if b.modalidade else 0,
            'Atraso': (hoje - b.data_fim_bolsa).days
        })
    
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Pendencias')
    output.seek(0)
    
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 
                     as_attachment=True, download_name=f'pendencias_{hoje.strftime("%Y%m%d")}.xlsx')
