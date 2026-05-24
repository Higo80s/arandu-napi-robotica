from flask import Blueprint, render_template, request
from models import MobilidadeInternacional, Bolsista, db, ProgramaAcademico, Campus, AcordoInternacional
from .services.inter_logic import MapVisualizationStrategy
from collections import Counter
from datetime import date, datetime

inter_bp = Blueprint('inter', __name__)

@inter_bp.route('/internacionalizacao/print')
def print_view():
    # Same logic as index, reusing for print
    return index_logic(print_mode=True)

@inter_bp.route('/internacionalizacao')
def index():
    return index_logic(print_mode=False)

# Helper to avoid code duplication
def index_logic(print_mode=False):
    from flask_login import current_user
    
    # [V22] Filtro de Escopo Hierárquico
    query = MobilidadeInternacional.query.options(
        db.joinedload(MobilidadeInternacional.bolsista).joinedload(Bolsista.programa_link).joinedload(ProgramaAcademico.campus)
    )
    
    # Filtrar mobilidades por escopo (via bolsista vinculado)
    if current_user.role == 'coordenador_programa' and current_user.programa_id:
        query = query.join(Bolsista).filter(Bolsista.programa_id == current_user.programa_id)
    elif current_user.role == 'diretor_campus' and current_user.campus_id:
        query = query.join(Bolsista).join(ProgramaAcademico).filter(
            ProgramaAcademico.campus_id == current_user.campus_id
        )
    
    mobilidades = query.all()
    
    today = date.today()
    
    stats = {
        'total_ativos': 0,
        'saida_ativos': 0,
        'entrada_ativos': 0,
        
        # New Historical Stats
        'total_historico': 0,
        'saida_historico': 0,
        'entrada_historico': 0,
        
        'total_paises': 0,
        'total_inst': 0
    }
    
    # Data Buckets
    paises_saida = []
    paises_entrada = []
    all_paises = []
    all_instituicoes = []
    cursos_entrada = []
    campus_entrada = []
    
    for m in mobilidades:
        fluxo = getattr(m, 'tipo_fluxo', 'saida') or 'saida'
        
        # Historical Counts
        stats['total_historico'] += 1
        if fluxo == 'entrada':
            stats['entrada_historico'] += 1
        else:
            stats['saida_historico'] += 1

        # Active Status
        m.ativo_hoje = (m.data_inicio <= today <= m.data_fim)
        
        if m.ativo_hoje:
            stats['total_ativos'] += 1
            if fluxo == 'entrada':
                stats['entrada_ativos'] += 1
            else:
                stats['saida_ativos'] += 1
        
        all_paises.append(m.pais_destino)
        all_instituicoes.append(m.instituicao_destino)
        
        if fluxo == 'saida':
            paises_saida.append(m.pais_destino)
        else:
            paises_entrada.append(m.pais_destino)
            if m.bolsista:
                if m.bolsista.programa_link:
                    prog = m.bolsista.programa_link.nome_programa
                    camp = m.bolsista.programa_link.campus.nome if m.bolsista.programa_link.campus else None
                else:
                    prog = m.bolsista.programa
                    camp = m.bolsista.campus
                
                if prog: cursos_entrada.append(prog)
                if camp: campus_entrada.append(camp)
    
    # Helper for Chart Data
    def prepare_chart_data(counter_data, total_count, color_palette):
        data = []
        for i, (label, count) in enumerate(counter_data):
            pct = (count / total_count * 100) if total_count > 0 else 0
            color = color_palette[i % len(color_palette)]
            data.append({
                'label': label,
                'count': count,
                'pct': pct,
                'color': color
            })
        return data

    colors = ['#8b5cf6', '#ec4899', '#06b6d4', '#f59e0b', '#10b981', '#ef4444', '#3b82f6', '#6366f1']
    
    # Use Historical Totals for "Top Visited" context
    top_destinos_raw = Counter(paises_saida).most_common(10)
    top_origens_raw = Counter(paises_entrada).most_common(10)
    
    top_destinos_data = prepare_chart_data(top_destinos_raw, len(paises_saida), colors)
    top_origens_data = prepare_chart_data(top_origens_raw, len(paises_entrada), colors)

    top_cursos = Counter(cursos_entrada).most_common(10)
    top_campus = Counter(campus_entrada).most_common(10)
    
    lista_paises = sorted(list(set(all_paises)))
    stats['total_paises'] = len(set(all_paises))
    stats['total_inst'] = len(set(all_instituicoes))
    
    # Lógica de Acordos e Mapa
    acordos = AcordoInternacional.query.filter_by(ativo=True).all()
    paises_com_acordo = {a.pais for a in acordos}
    
    strategy = MapVisualizationStrategy()
    count_mobilidade = Counter(all_paises)
    todos_os_paises = set(count_mobilidade.keys()) | paises_com_acordo
    
    map_data = [["Country", "Indicador"]]
    for p in todos_os_paises:
        val = strategy.calculate_value(
            num_alunos=count_mobilidade.get(p, 0),
            tem_acordo=(p in paises_com_acordo)
        )
        map_data.append([p, val])
    
    template = 'internacionalizacao/print.html' if print_mode else 'internacionalizacao/dashboard.html'
    return render_template(template, 
                           mobilidades=mobilidades, 
                           stats=stats, 
                           map_data=map_data,
                           top_destinos=top_destinos_data,
                           top_origens=top_origens_data,
                           top_cursos=top_cursos,
                           top_campus=top_campus,
                           lista_paises=lista_paises,
                           acordos=acordos)

@inter_bp.route('/api/internacionalizacao/acordos', methods=['POST'])
def add_acordo():
    from flask_login import current_user
    if not current_user.is_authenticated:
         return {"success": False, "error": "Não autenticado"}, 401

    data = request.get_json()
    if not data or not data.get('pais') or not data.get('instituicao'):
        return {"success": False, "error": "Campos Pais e Instituição são obrigatórios"}, 400
    
    try:
        data_ass = None
        data_venc = None
        if data.get('data_assinatura'):
             data_ass = datetime.strptime(data['data_assinatura'], '%Y-%m-%d').date()
        if data.get('data_vencimento'):
             data_venc = datetime.strptime(data['data_vencimento'], '%Y-%m-%d').date()
             
        from utils.formatters import normalizar_edital
        
        is_gcub = data.get('is_gcub', False)
        raw_edital = data.get('numero_edital', '').strip() if data.get('numero_edital') else None
        numero_edital = normalizar_edital(raw_edital) if raw_edital else None

        if is_gcub and not numero_edital:
            return {"success": False, "error": "Número do Edital é obrigatório para acordos GCUB"}, 400

        novo_acordo = AcordoInternacional(
            pais=data.get('pais'),
            instituicao=data.get('instituicao'),
            processo_sei=data.get('processo_sei'),
            tipo_acordo=data.get('tipo_acordo'),
            data_assinatura=data_ass,
            data_vencimento=data_venc,
            vagas_anuais=data.get('vagas_anuais', 0),
            idioma_instrucao=data.get('idioma_instrucao'),
            areas_conhecimento=data.get('areas_conhecimento'),
            ativo=data.get('ativo', True),
            is_gcub=is_gcub,
            numero_edital=numero_edital
        )
        db.session.add(novo_acordo)
        db.session.commit()

        # [YOKO] Auditoria para Acordos GCUB
        if novo_acordo.is_gcub:
            from models import LogAutomacao
            log = LogAutomacao(
                nome_tarefa="Cadastro de Acordo GCUB",
                status="SUCESSO",
                mensagem=f"Acordo GCUB registrado: {novo_acordo.instituicao} ({novo_acordo.pais}) - Edital: {novo_acordo.numero_edital} por {current_user.nome}"
            )
            db.session.add(log)
            db.session.commit()
        return {"success": True, "acordo": novo_acordo.to_dict()}
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e)}, 500

@inter_bp.route('/api/internacionalizacao/acordos/<int:acordo_id>', methods=['PUT'])
def update_acordo(acordo_id):
    from flask_login import current_user
    if not current_user.is_authenticated:
         return {"success": False, "error": "Não autenticado"}, 401
         
    data = request.get_json()
    try:
        acordo = AcordoInternacional.query.get(acordo_id)
        if not acordo:
            return {"success": False, "error": "Acordo não encontrado"}, 404
        
        # Atualização de Campos
        acordo.pais = data.get('pais', acordo.pais)
        acordo.instituicao = data.get('instituicao', acordo.instituicao)
        acordo.processo_sei = data.get('processo_sei', acordo.processo_sei)
        acordo.tipo_acordo = data.get('tipo_acordo', acordo.tipo_acordo)
        
        if data.get('data_assinatura'):
            acordo.data_assinatura = datetime.strptime(data['data_assinatura'], '%Y-%m-%d').date()
        if data.get('data_vencimento'):
            acordo.data_vencimento = datetime.strptime(data['data_vencimento'], '%Y-%m-%d').date()
            
        acordo.is_gcub = data.get('is_gcub', acordo.is_gcub)
        
        from utils.formatters import normalizar_edital
        raw_edital = data.get('numero_edital', '').strip() if data.get('numero_edital') else None
        if raw_edital:
            acordo.numero_edital = normalizar_edital(raw_edital)
            
        acordo.ativo = data.get('ativo', acordo.ativo)
        
        db.session.commit()

        # Auditoria para Edição GCUB
        if acordo.is_gcub:
            from models import LogAutomacao
            log = LogAutomacao(
                nome_tarefa="Edição de Acordo GCUB",
                status="SUCESSO",
                mensagem=f"Acordo GCUB atualizado: {acordo.instituicao} ({acordo.pais}) por {current_user.nome}"
            )
            db.session.add(log)
            db.session.commit()

        return {"success": True, "acordo": acordo.to_dict()}
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e)}, 500

@inter_bp.route('/api/internacionalizacao/acordos/<int:acordo_id>', methods=['DELETE'])
def delete_acordo(acordo_id):
    from flask_login import current_user
    if not current_user.is_authenticated:
         return {"success": False, "error": "Não autenticado"}, 401
         
    try:
        acordo = AcordoInternacional.query.get(acordo_id)
        if not acordo:
            return {"success": False, "error": "Acordo não encontrado"}, 404
        
        db.session.delete(acordo)
        db.session.commit()
        return {"success": True}
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e)}, 500
