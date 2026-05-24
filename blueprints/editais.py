from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import re
from decimal import Decimal

# [REFATORACAO] Imports centralizados
from extensions import db
from models import Edital, Bolsista, Modalidade, ProapDistribuicao, Campus, ProgramaAcademico, EditalRegra, RodadaSelecao, EtapaCronograma, Candidatura
from utils import parse_flexible_date
from forms.edital_form import EditalForm
from services.edital_service import EditalService
from audit import log_action
from decorators import admin_required
from utils.permissions import apply_user_scope, filter_editais_by_scope  # [V22] Filtros de escopo hierárquico
from sqlalchemy import not_, func, and_

editais_bp = Blueprint('editais', __name__)

# --- HELPERS ---

def clean_currency(val):
    """
    Limpa e converte strings monetárias para Decimal (focada em R$).
    Aceita: "2.100,00", "2100,00", "R$ 2.100,00", "2100.00"
    """
    if val is None or val == '': return Decimal('0')
    if isinstance(val, Decimal): return val
    if isinstance(val, (int, float)): return Decimal(str(val))
    
    # Remove R$, espaços e outros caracteres não numéricos exceto ponto e vírgula
    cleaned = re.sub(r'[^\d,.]', '', str(val))
    
    if not cleaned: return Decimal('0')

    # Lógica Inteligente de Separador
    if ',' in cleaned and '.' in cleaned:
        # Se a vírgula vier depois do ponto, assume formato BR: 1.234,56
        if cleaned.rfind(',') > cleaned.rfind('.'):
            cleaned = cleaned.replace('.', '').replace(',', '.')
        else:
            # Formato US: 1,234.56
            cleaned = cleaned.replace(',', '')
    elif ',' in cleaned:
        # Apenas vírgula: 1234,56
        cleaned = cleaned.replace(',', '.')
    
    try:
        return Decimal(cleaned)
    except (ValueError, Exception):
        return Decimal('0')

# --- ROUTES: EDITAIS ---

@editais_bp.route('/editais')
def index():
    from flask_login import current_user
    
    # [V11.5] Monitoria Inteligente: Termômetro de Ocupação
    # Subquery para contar bolsistas ativos por edital
    contagem_ativos = db.session.query(
        Bolsista.edital_id,
        func.count(Bolsista.id).label('total_ativos')
    ).filter(Bolsista.ativo == True).group_by(Bolsista.edital_id).subquery()

    # Query principal unindo o Edital com o contador
    query = db.session.query(Edital, contagem_ativos.c.total_ativos).outerjoin(
        contagem_ativos, Edital.id == contagem_ativos.c.edital_id
    )
    
    # [V22] Filtro de Escopo Hierárquico
    query = filter_editais_by_scope(query, current_user)
    
    editais_data = query.order_by(Edital.data_fim.desc().nullsfirst()).all()
    
    return render_template('editais/index.html', editais=editais_data, hoje=date.today())

@editais_bp.route('/editais/novo', methods=['GET', 'POST'])
@admin_required
def novo():
    distribuicoes = ProapDistribuicao.query.filter(ProapDistribuicao.valor_distribuido > 0).all()
    form = EditalForm()
    
    # Preencher dropdown do PROAP
    form.proap_distribuicao_id.choices = [(0, '--- Nenhum ---')] + [(d.id, d.descricao) for d in distribuicoes]
    
    if form.validate_on_submit():
        success, result = EditalService.create_edital(form.data)
        if success:
            flash('Edital criado com sucesso!', 'success')
            return redirect(url_for('editais.index'))
        else:
            flash(f'Erro ao salvar edital: {result}', 'danger')
            
    return render_template('editais/form.html', form=form, edital=None, distribuicoes=distribuicoes)

@editais_bp.route('/editais/<int:id>/editar', methods=['GET', 'POST'])
@admin_required
def editar(id):
    edital = Edital.query.get_or_404(id)
    distribuicoes = ProapDistribuicao.query.filter(ProapDistribuicao.valor_distribuido > 0).all()
    
    # Preencher form com dados existentes para o GET
    form = EditalForm(obj=edital)
    form.proap_distribuicao_id.choices = [(0, '--- Nenhum ---')] + [(d.id, d.descricao) for d in distribuicoes]
    
    if form.validate_on_submit():
        success, result = EditalService.update_edital(id, form.data)
        if success:
            flash('Edital atualizado com sucesso!', 'success')
            return redirect(url_for('editais.index'))
        else:
            flash(f'Erro ao atualizar edital: {result}', 'danger')
            
    return render_template('editais/form.html', form=form, edital=edital, distribuicoes=distribuicoes)

@editais_bp.route('/editais/<int:id>/excluir', methods=['POST'])
@admin_required
def excluir(id):
    edital = Edital.query.get_or_404(id)
    num = edital.numero
    db.session.delete(edital)
    db.session.commit()
    log_action('DELETE_EDITAL', tabela='editais', registro_id=id, detalhes=f"Edital {num} deleted")
    flash('Edital excluído com sucesso!', 'success')
    return redirect(url_for('editais.index'))

@editais_bp.route('/editais/<int:id>/orcamento', methods=['POST'])
@admin_required
def orcamento(id):
    edital = Edital.query.get_or_404(id)
    try:
        val_str = request.form['orcamento']
        if val_str:
            clean = re.sub(r'[^\d,]', '', val_str).replace(',', '.')
            edital.orcamento_total = Decimal(clean)
        else:
            edital.orcamento_total = Decimal('0')
            
        db.session.commit()
        log_action('UPDATE_ORCAMENTO', tabela='editais', registro_id=edital.id, detalhes=f"New Total: {edital.orcamento_total}")
        flash('Orçamento atualizado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao atualizar orçamento: {e}', 'danger')
        
    return redirect(url_for('editais.modalidades_gerenciar', id=id))

# --- ROUTES: REGRAS DINAMICAS (AJAX) ---

@editais_bp.route('/api/editais/<int:id>/regras', methods=['POST'])
@login_required
def adicionar_regra(id):
    from flask import jsonify
    edital = Edital.query.get_or_404(id)
    try:
        data = request.get_json()
        if not data or not data.get('descricao'):
            return jsonify({'success': False, 'error': 'Descrição é obrigatória.'}), 400
            
        nova_regra = EditalRegra(
            edital_id=edital.id,
            descricao=data.get('descricao'),
            ordem=data.get('ordem', 0)
        )
        db.session.add(nova_regra)
        db.session.commit()
        return jsonify({'success': True, 'id': nova_regra.id, 'descricao': nova_regra.descricao, 'ordem': nova_regra.ordem})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@editais_bp.route('/api/editais/regras/<int:regra_id>', methods=['DELETE'])
@login_required
def excluir_regra(regra_id):
    from flask import jsonify
    regra = EditalRegra.query.get_or_404(regra_id)
    try:
        db.session.delete(regra)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# --- ROUTES: MODALIDADES ---

@editais_bp.route('/editais/<int:id>/modalidades', methods=['GET', 'POST'])
@admin_required
def modalidades_gerenciar(id):
    edital = Edital.query.get_or_404(id)
    if request.method == 'POST':
        try:
            nova_mod = Modalidade(
                edital_id=edital.id,
                nivel=request.form['nivel'],
                vagas=int(request.form['vagas']),
                valor_mensal=clean_currency(request.form['valor_mensal']),
                max_meses=int(request.form['max_meses']) if request.form.get('max_meses') else None
            )
            db.session.add(nova_mod)
            db.session.commit()
            flash('Modalidade adicionada!', 'success')
            return redirect(url_for('editais.modalidades_gerenciar', id=id))
        except Exception as e:
            # app.logger not available directly on blueprint, use print/logging or current_app
            print(f"Erro ao adicionar modalidade: {e}")
            flash(f'Erro ao adicionar modalidade: {e}', 'danger')
            return redirect(url_for('editais.modalidades_gerenciar', id=id))
    
    # Dashboard Logic
    today = date.today()
    
    stats = {
        'total_vagas': 0,
        'total_ocupado': 0,
        'custo_mensal': Decimal('0'),
        'total_comprometido': Decimal('0'),
        'by_level': {}
    }
    
    for mod in edital.modalidades:
        occupied = 0
        
        # 1. Bolsistas
        for b in mod.bolsistas:
            if b.check_status_validity() == 'ATIVO':
                occupied += 1
                stats['custo_mensal'] += mod.valor_mensal
                
                if b.data_fim_bolsa and b.data_fim_bolsa > today:
                    diff = relativedelta(b.data_fim_bolsa, today)
                    meses_restantes = diff.years * 12 + diff.months
                    if b.data_fim_bolsa.day >= today.day:
                        meses_restantes += 1
                    stats['total_comprometido'] += (meses_restantes * mod.valor_mensal)

        # 2. Residentes
        for r in mod.residentes:
            if r.check_status_validity() == 'ATIVO' and r.recebe_bolsa:
                 stats['custo_mensal'] += mod.valor_mensal
                 if r.data_fim and r.data_fim > today:
                    diff = relativedelta(r.data_fim, today)
                    meses = diff.years * 12 + diff.months
                    stats['total_comprometido'] += (meses * mod.valor_mensal)
                
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

    # [NEW V10.8] Sincronização com o Modo Seleção (Vagas Globais)
    v_stats = EditalService.get_vacancy_stats(id)
    stats['total_ocupado_global'] = v_stats['total_ocupado']
    stats['saldo_global'] = v_stats['saldo']
    stats['selecionados_pendentes'] = v_stats['selecionados']

    return render_template('editais/modalidades.html', edital=edital, stats=stats)

@editais_bp.route('/modalidades/<int:id>/editar', methods=['GET', 'POST'])
@admin_required
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
        return redirect(url_for('editais.modalidades_gerenciar', id=edital_id))
    
    edital = Edital.query.get_or_404(edital_id)
    return render_template('editais/modalidades.html', edital=edital, modalidade_edit=mod)

@editais_bp.route('/modalidades/<int:id>/excluir', methods=['POST'])
@admin_required
def modalidades_excluir(id):
    mod = Modalidade.query.get_or_404(id)
    edital_id = mod.edital_id
    db.session.delete(mod)
    db.session.commit()
    flash('Modalidade removida!', 'success')
    return redirect(url_for('editais.modalidades_gerenciar', id=edital_id))

# --- GESTÃO V10: SELEÇÃO E CRONOGRAMAS ---

@editais_bp.route('/editais/<int:id>/selecao', methods=['GET'])
@login_required
def painel_selecao(id):
    """
    Painel Principal de Gestão de Processos Seletivos.
    Visualiza as Rodadas (Chamadas) e seus Cronogramas.
    """
    edital = Edital.query.get_or_404(id)
    
    rodada_ativa_id = request.args.get('rodada_id', type=int)
    rodada_focada = None
    
    if rodada_ativa_id:
        rodada_focada = RodadaSelecao.query.get(rodada_ativa_id)
    elif edital.rodadas:
        rodada_focada = next((r for r in edital.rodadas if r.ativa), edital.rodadas[0])
        
    # Stats [REPLACED V10.8 with Global Logic]
    v_stats = EditalService.get_vacancy_stats(id)
    
    stats_rodada = {'inscritos': 0, 'selecionados': 0, 'excedentes': 0, 'efetivados': 0}
    if rodada_focada:
        stats_rodada['inscritos'] = len(rodada_focada.candidaturas)
        stats_rodada['selecionados'] = len([c for c in rodada_focada.candidaturas if c.status == 'SELECIONADO'])
        stats_rodada['excedentes'] = len([c for c in rodada_focada.candidaturas if c.status == 'EXCEDENTE'])
        stats_rodada['efetivados'] = len([c for c in rodada_focada.candidaturas if c.status == 'EFETIVADO'])
        
    # [NEW V10.9] Registro de CPFs efetivados para trava de idempotência
    from utils.idempotency import get_cpfs_efetivados_set
    cpfs_efetivados = get_cpfs_efetivados_set()
        
    return render_template('editais/selecao_painel.html', 
                           edital=edital, 
                           rodada_focada=rodada_focada,
                           campuses=Campus.query.all(),
                           programas=ProgramaAcademico.query.options(db.joinedload(ProgramaAcademico.campus)).filter(not_(ProgramaAcademico.nome_programa.ilike('%*%'))).order_by(ProgramaAcademico.nome_programa.asc()).all(),
                           dashboard_stats={
                               'total_vagas': v_stats['total_vagas'],
                               'bolsas_ativas': v_stats['bolsistas_ativos'],
                               'selecionados_pendentes': v_stats['selecionados'],
                               'total_ocupado': v_stats['total_ocupado'],
                               'saldo': v_stats['saldo']
                           },
                           funnel=stats_rodada,
                           cpfs_efetivados=cpfs_efetivados)

@editais_bp.route('/editais/<int:id>/rodadas/nova', methods=['GET', 'POST'])
@login_required
def rodadas_nova(id):
    edital = Edital.query.get_or_404(id)
    if request.method == 'GET':
        return render_template('editais/rodada_form.html', edital=edital)

    try:
        nova_rodada = RodadaSelecao(
            edital_id=edital.id,
            nome=request.form['nome'],
            data_inicio=parse_flexible_date(request.form['data_inicio']),
            data_fim=parse_flexible_date(request.form['data_fim']),
            descricao=request.form.get('descricao', ''),
            ativa=True
        )
        db.session.add(nova_rodada)
        db.session.flush()

        # [NEW V10] Criação de Cronograma em Lote
        fases_nomes = request.form.getlist('fase_nome[]')
        fases_inicio = request.form.getlist('fase_inicio[]')
        fases_fim = request.form.getlist('fase_fim[]')

        for i, nome in enumerate(fases_nomes):
            if nome.strip():
                d_inicio = fases_inicio[i] if i < len(fases_inicio) else None
                d_fim = fases_fim[i] if i < len(fases_fim) else None
                
                etapa = EtapaCronograma(
                    rodada_id=nova_rodada.id,
                    nome=nome,
                    data_inicio=parse_flexible_date(d_inicio) if d_inicio else None,
                    data_limite=parse_flexible_date(d_fim) if d_fim else None,
                    ordem=i
                )
                db.session.add(etapa)

        db.session.commit()
        flash('Nova Rodada de Seleção criada com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao criar rodada: {str(e)}', 'error')
    return redirect(url_for('editais.painel_selecao', id=id, rodada_id=nova_rodada.id))

@editais_bp.route('/rodadas/<int:id>/etapa/nova', methods=['POST'])
@login_required
def etapas_nova(id):
    rodada = RodadaSelecao.query.get_or_404(id)
    try:
        nova_etapa = EtapaCronograma(
            rodada_id=rodada.id,
            nome=request.form['nome'],
            link_publicacao=request.form.get('link_publicacao', ''),
            ordem=int(request.form.get('ordem', 0))
        )
        if request.form.get('data_inicio'):
             nova_etapa.data_inicio = parse_flexible_date(request.form['data_inicio'])
        if request.form.get('data_limite'):
             nova_etapa.data_limite = parse_flexible_date(request.form['data_limite'])

        db.session.add(nova_etapa)
        db.session.commit()
        flash('Etapa adicionada ao cronograma!', 'success')
    except Exception as e:
        flash(f'Erro ao adicionar etapa: {str(e)}', 'error')
    return redirect(url_for('editais.painel_selecao', id=rodada.edital_id, rodada_id=rodada.id))

@editais_bp.route('/rodadas/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def rodadas_editar(id):
    rodada = RodadaSelecao.query.get_or_404(id)
    if request.method == 'GET':
         edital = Edital.query.get(rodada.edital_id)
         return render_template('editais/rodada_editar.html', rodada=rodada, edital=edital)

    try:
        rodada.nome = request.form['nome']
        rodada.data_inicio = parse_flexible_date(request.form['data_inicio'])
        rodada.data_fim = parse_flexible_date(request.form['data_fim'])
        rodada.descricao = request.form.get('descricao', '')
        db.session.commit()
        flash('Rodada atualizada com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao atualizar: {str(e)}', 'error')
    return redirect(url_for('editais.painel_selecao', id=rodada.edital_id, rodada_id=rodada.id))

@editais_bp.route('/rodadas/<int:id>/excluir', methods=['POST'])
@login_required
def rodadas_excluir(id):
    rodada = RodadaSelecao.query.get_or_404(id)
    edital_id = rodada.edital_id
    try:
        EtapaCronograma.query.filter_by(rodada_id=id).delete()
        Candidatura.query.filter_by(rodada_id=id).delete()
        db.session.delete(rodada)
        db.session.commit()
        flash('Rodada excluída permanentemente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir rodada: {str(e)}', 'error')
    return redirect(url_for('editais.painel_selecao', id=edital_id))

@editais_bp.route('/etapa/<int:id>/editar', methods=['POST'])
@login_required
def etapa_editar(id):
    etapa = EtapaCronograma.query.get_or_404(id)
    try:
        etapa.nome = request.form['nome']
        if request.form.get('data_inicio'):
            etapa.data_inicio = parse_flexible_date(request.form['data_inicio'])
        else:
            etapa.data_inicio = None
        if request.form.get('data_limite'):
            etapa.data_limite = parse_flexible_date(request.form['data_limite'])
        else:
            etapa.data_limite = None
        etapa.link_publicacao = request.form.get('link_publicacao', '')
        etapa.ordem = int(request.form.get('ordem', 0))
        db.session.commit()
        flash('Etapa atualizada!', 'success')
    except Exception as e:
        flash(f'Erro ao editar: {str(e)}', 'error')
    return redirect(url_for('editais.painel_selecao', id=etapa.rodada.edital_id, rodada_id=etapa.rodada_id))

@editais_bp.route('/etapa/<int:id>/excluir', methods=['POST'])
@login_required
def etapa_excluir(id):
    etapa = EtapaCronograma.query.get_or_404(id)
    rodada_id = etapa.rodada_id
    edital_id = etapa.rodada.edital_id
    try:
        db.session.delete(etapa)
        db.session.commit()
        flash('Etapa removida.', 'success')
    except Exception as e:
        flash(f'Erro ao remover: {str(e)}', 'error')
    return redirect(url_for('editais.painel_selecao', id=edital_id, rodada_id=rodada_id))

@editais_bp.route('/api/etapas/reordenar', methods=['POST'])
@login_required
def api_etapas_reordenar():
    from flask import jsonify
    try:
        data = request.get_json()
        etapas = data.get('etapas', [])
        
        for item in etapas:
            etapa = EtapaCronograma.query.get(int(item['id']))
            if etapa:
                etapa.ordem = int(item['ordem'])
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Ordem atualizada com sucesso!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@editais_bp.route('/rodadas/<int:id>/candidatura/nova', methods=['GET', 'POST'])
@login_required
def candidatura_nova(id):
    rodada = RodadaSelecao.query.get_or_404(id)
    if request.method == 'GET':
        from sqlalchemy import not_
        from models import Campus
        edital = Edital.query.get(rodada.edital_id)
        campuses = Campus.query.order_by(Campus.nome.asc()).all()
        programas = ProgramaAcademico.query.options(db.joinedload(ProgramaAcademico.campus)).filter(not_(ProgramaAcademico.nome_programa.ilike('%*%'))).order_by(ProgramaAcademico.nome_programa.asc()).all()
        return render_template('editais/candidatura_form.html', rodada=rodada, edital=edital, programas=programas, campuses=campuses)

    try:
        nova_cand = Candidatura(
            rodada_id=rodada.id,
            nome=request.form['nome'],
            cpf=request.form['cpf'],
            email=request.form['email'],
            campus_id=int(request.form.get('campus_id')) if request.form.get('campus_id') else None,
            programa_id=int(request.form.get('programa_id')) if request.form.get('programa_id') else None,
            numero_sei=request.form.get('numero_sei'),
            numero_formulario=request.form.get('numero_formulario'),
            orientador=request.form.get('orientador'),
            email_orientador=request.form.get('email_orientador'),
            projeto_pesquisa=request.form.get('projeto_pesquisa'),
            cidade=request.form.get('cidade'),
            instituicao=request.form.get('instituicao'),
            anotacoes=request.form.get('anotacoes'),
            status='INSCRITO',
            data_submissao=datetime.now()
        )
        db.session.add(nova_cand)
        db.session.commit()
        flash('Candidato inscrito com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao inscrever: {str(e)}', 'error')
    return redirect(url_for('editais.painel_selecao', id=rodada.edital_id, rodada_id=rodada.id))

@editais_bp.route('/candidatura/<int:id>/status', methods=['POST'])
@login_required
def candidatura_status(id):
    cand = Candidatura.query.get_or_404(id)
    novo_status = request.form['status']
    if novo_status in ['INSCRITO', 'SELECIONADO', 'EXCEDENTE', 'REJEITADO', 'EFETIVADO']:
        old_status = cand.status
        # [NEW V10.8] Validação de Vagas Globais: Impede selecionar se não houver saldo
        if novo_status == 'SELECIONADO' and old_status != 'SELECIONADO':
            v_stats = EditalService.get_vacancy_stats(cand.rodada.edital_id)
            if v_stats['saldo'] <= 0:
                flash(f"Erro: Limite de Vagas Esgotado ({v_stats['total_vagas']} vagas). Não é possível selecionar mais candidatos.", 'danger')
                return redirect(url_for('editais.painel_selecao', id=cand.rodada.edital_id, rodada_id=cand.rodada_id))

        cand.status = novo_status
        db.session.commit()
        flash(f'Status atualizado para {novo_status}.', 'success')
    return redirect(url_for('editais.painel_selecao', id=cand.rodada.edital_id, rodada_id=cand.rodada_id))

@editais_bp.route('/candidatura/<int:id>/promover', methods=['POST'])
@login_required
def candidatura_promover(id):
    cand = Candidatura.query.get_or_404(id)
    if cand.status != 'SELECIONADO':
        flash('Apenas candidatos com status SELECIONADO podem ser promovidos.', 'warning')
        return redirect(url_for('editais.painel_selecao', id=cand.rodada.edital_id, rodada_id=cand.rodada_id))
        
    is_posdoc = False
    if cand.programa:
        niveis = (cand.programa.niveis or "").upper()
        if any(x in niveis for x in ['PÓS', 'POS', 'RESID']):
            is_posdoc = True
    
    if is_posdoc:
        return redirect(url_for('posdoc.novo', candidatura_id=cand.id))
    return redirect(url_for('bolsistas.novo', candidatura_id=cand.id))

@editais_bp.route('/rodadas/<int:id>/imprimir', methods=['GET'])
@login_required
def rodadas_imprimir_lista(id):
    rodada = RodadaSelecao.query.get_or_404(id)
    priority_map = {'EFETIVADO': 0, 'SELECIONADO': 1, 'EXCEDENTE': 2, 'INSCRITO': 3, 'DESCLASSIFICADO': 4}
    candidatos = sorted(rodada.candidaturas, key=lambda c: (priority_map.get(c.status, 9), c.nome))
    return render_template('editais/print_lista.html', rodada=rodada, candidatos=candidatos, agora=datetime.now())

# === MODALIDADES API ===
@editais_bp.route('/api/modalidades/<int:edital_id>')
@login_required
def api_modalidades(edital_id):
    modalidades = Modalidade.query.filter_by(edital_id=edital_id).all()
    return jsonify([{
        'id': m.id, 
        'nivel': m.nivel, 
        'valor': m.valor_mensal, 
        'vagas': m.vagas,
        'max_meses': m.max_meses
    } for m in modalidades])
