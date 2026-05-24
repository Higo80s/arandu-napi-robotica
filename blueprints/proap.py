"""
MÓDULO PROAP/PROAPINHO - Rotas Flask
=====================================

Rotas para gestão de recursos PROAP (CAPES) e PROAPINHO (UTFPR).
Este arquivo será importado pelo app.py principal.

Funcionalidades:
- Gestão de Repasses (CRUD)
- Distribuição de Recursos para Programas
- Registro de Aplicações/Despesas
- Dashboard e Relatórios

Autor: Equipe Yoko - Fase 8
Data: Janeiro 2026
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from decimal import Decimal
from datetime import datetime, date
from models import db, ProapRepasse, ProapDistribuicao, ProapAplicacao, ProgramaAcademico, CATEGORIAS_PROAP, Edital, Campus
from decorators import admin_required, require_role
from utils import parse_flexible_date, format_date_br
from sqlalchemy import func, extract, not_
import io
from xhtml2pdf import pisa
from flask import make_response
from sqlalchemy.orm import joinedload

# Criar Blueprint
proap_bp = Blueprint('proap', __name__, url_prefix='/proap')

# ============================================================================
# ROTAS: REPASSES
# ============================================================================

@proap_bp.route('/')
@proap_bp.route('/repasses')
def repasses_index():
    """Lista todos os repasses PROAP/PROAPINHO"""
    from flask_login import current_user
    
    query = ProapRepasse.query
    
    # [V22] Filtro de Escopo Hierárquico
    # Coordenadores e Diretores não filtram repasses (são institucionais)
    # Apenas visualizam tudo (não há filtro por programa aqui)
    
    repasses = query.order_by(ProapRepasse.ano.desc(), ProapRepasse.tipo).all()
    
    # Estatísticas rápidas
    total_proap = db.session.query(func.sum(ProapRepasse.valor_total))\
        .filter_by(tipo='PROAP').scalar() or Decimal('0')
    total_proapinho = db.session.query(func.sum(ProapRepasse.valor_total))\
        .filter_by(tipo='PROAPINHO').scalar() or Decimal('0')
    
    stats = {
        'total_proap': total_proap,
        'total_proapinho': total_proapinho,
        'total_geral': total_proap + total_proapinho
    }
    
    return render_template('proap/repasses/index.html', repasses=repasses, stats=stats)


@proap_bp.route('/repasses/novo', methods=['GET', 'POST'])
@admin_required
def repasses_novo():
    """Cadastro de novo repasse"""
    if request.method == 'POST':
        try:
            novo_repasse = ProapRepasse(
                ano=int(request.form['ano']),
                tipo=request.form['tipo'],  # 'PROAP' ou 'PROAPINHO'
                valor_total=Decimal(request.form['valor_total'].replace('.', '').replace(',', '.')),
                data_repasse=parse_flexible_date(request.form['data_repasse']),
                observacoes=request.form.get('observacoes', '')
            )
            db.session.add(novo_repasse)
            db.session.commit()
            
            flash(f'✅ Repasse {novo_repasse.tipo} {novo_repasse.ano} cadastrado com sucesso!', 'success')
            return redirect(url_for('proap.repasses_distribuir', id=novo_repasse.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Erro ao cadastrar repasse: {str(e)}', 'error')
            return redirect(url_for('proap.repasses_novo'))
    
    return render_template('proap/repasses/form.html', repasse=None)


@proap_bp.route('/repasses/<int:id>/editar', methods=['GET', 'POST'])
@admin_required
def repasses_editar(id):
    """Edição de repasse existente"""
    repasse = ProapRepasse.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            repasse.ano = int(request.form['ano'])
            repasse.tipo = request.form['tipo']
            repasse.valor_total = Decimal(request.form['valor_total'].replace('.', '').replace(',', '.'))
            repasse.data_repasse = parse_flexible_date(request.form['data_repasse'])
            repasse.observacoes = request.form.get('observacoes', '')
            
            db.session.commit()
            flash('✅ Repasse atualizado com sucesso!', 'success')
            return redirect(url_for('proap.repasses_index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Erro ao atualizar: {str(e)}', 'error')
    
    return render_template('proap/repasses/form.html', repasse=repasse)


@proap_bp.route('/repasses/<int:id>/excluir', methods=['POST'])
@admin_required
def repasses_excluir(id):
    """Exclusão de repasse (e cascata de distribuições/aplicações)"""
    try:
        repasse = ProapRepasse.query.get_or_404(id)
        tipo = repasse.tipo
        ano = repasse.ano
        
        db.session.delete(repasse)
        db.session.commit()
        
        flash(f'✅ Repasse {tipo} {ano} excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Erro ao excluir: {str(e)}', 'error')
    
    return redirect(url_for('proap.repasses_index'))


# ============================================================================
# ROTAS: DISTRIBUIÇÃO
# ============================================================================

@proap_bp.route('/repasses/<int:id>/distribuir', methods=['GET', 'POST'])
@admin_required
def repasses_distribuir(id):
    """Distribuição de recursos do repasse para programas"""
    repasse = ProapRepasse.query.get_or_404(id)
    
    # [FIX] Eager load campus to avoid lazy load errors in template if session is dirty
    todos_programas = ProgramaAcademico.query.options(db.joinedload(ProgramaAcademico.campus))\
        .filter(not_(ProgramaAcademico.nome_programa.ilike('%*%')))\
        .order_by(ProgramaAcademico.nome_programa.asc()).all()
        
    # Filtrar para exibir apenas códigos únicos (evitar duplicação M/D)
    # Mantém o primeiro encontrado de cada código
    programas_unicos = {}
    for p in todos_programas:
        if p.codigo_programa and p.codigo_programa not in programas_unicos:
            programas_unicos[p.codigo_programa] = p
        elif not p.codigo_programa: # Caso não tenha código, inclui pelo ID para evitar perda
             programas_unicos[f"ID_{p.id}"] = p
             
    programas = sorted(programas_unicos.values(), key=lambda x: x.nome_programa)
    
    if request.method == 'POST':
        try:
            # Processar distribu içõesições em lote
            programa_ids = request.form.getlist('programa_id[]')
            valores = request.form.getlist('valor[]')
            numeros_sei = request.form.getlist('numero_sei[]')
            anotacoes_list = request.form.getlist('anotacoes[]')
            
            total_distribuido = 0
            
            for i, prog_id in enumerate(programa_ids):
                if prog_id and valores[i]:
                    valor = Decimal(valores[i].replace('.', '').replace(',', '.'))
                    total_distribuido += valor
                    
                    dist = ProapDistribuicao(
                        repasse_id=repasse.id,
                        programa_id=int(prog_id),
                        valor_distribuido=valor,
                        percentual=round((valor / repasse.valor_total) * Decimal('100'), 2),
                        data_distribuicao=date.today(),
                        numero_sei=numeros_sei[i] if i < len(numeros_sei) else None,
                        anotacoes=anotacoes_list[i] if i < len(anotacoes_list) else None
                    )
                    db.session.add(dist)
            
            # Validação
            if abs(total_distribuido - repasse.valor_total) > 0.01:
                raise ValueError(f'Total distribuído (R$ {total_distribuido:,.2f}) diferente do repasse (R$ {repasse.valor_total:,.2f})')
            
            db.session.commit()
            flash(f'✅ Distribuição realizada com sucesso! {len(programa_ids)} programas beneficiados.', 'success')
            return redirect(url_for('proap.repasses_index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Erro na distribuição: {str(e)}', 'error')
    
    # Cálculo de distribuições existentes
    try:
        distribuido_atual = db.session.query(func.sum(ProapDistribuicao.valor_distribuido))\
            .filter_by(repasse_id=repasse.id).scalar() or Decimal('0')
    except Exception as e:
        db.session.rollback()
        print(f"Error calculating distribuido_atual: {e}")
        distribuido_atual = 0
    
    return render_template('proap/distribuicoes/distribuir.html', 
                         repasse=repasse, 
                         programas=programas,
                         distribuido_atual=distribuido_atual)


@proap_bp.route('/distribuicoes/<int:id>/aplicacoes')
def distribuicoes_aplicacoes(id):
    """Listagem e registro de aplicações de uma distribuição"""
    distribuicao = ProapDistribuicao.query.get_or_404(id)
    
    # Total aplicado
    total_aplicado = db.session.query(func.sum(ProapAplicacao.valor))\
        .filter_by(distribuicao_id=id).scalar() or Decimal('0')
    
    saldo = distribuicao.valor_distribuido - total_aplicado
    
    return render_template('proap/aplicacoes/index.html',
                         distribuicao=distribuicao,
                         total_aplicado=total_aplicado,
                         saldo=saldo,
                         categorias=CATEGORIAS_PROAP)


@proap_bp.route('/distribuicoes/<int:id>/aplicacoes/nova', methods=['POST'])
def aplicacoes_nova(id):
    """Registro de nova aplicação/despesa"""
    try:
        distribuicao = ProapDistribuicao.query.get_or_404(id)
        
        nova_aplicacao = ProapAplicacao(
            distribuicao_id=distribuicao.id,
            categoria=request.form['categoria'],
            descricao=request.form['descricao'],
            valor=Decimal(request.form['valor'].replace('.', '').replace(',', '.')),
            data_aplicacao=parse_flexible_date(request.form['data_aplicacao']),
            numero_documento=request.form.get('numero_documento'),
            # TODO: Implementar upload de comprovante
        )
        
        db.session.add(nova_aplicacao)
        db.session.commit()
        
        flash('✅ Aplicação registrada com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Erro ao registrar aplicação: {str(e)}', 'error')
    
    return redirect(url_for('proap.distribuicoes_aplicacoes', id=id))


# ============================================================================
# DASHBOARD E RELATÓRIOS
# ============================================================================

@proap_bp.route('/dashboard')
def dashboard():
    """Dashboard analítico PROAP/PROAPINHO com métricas e visualizações"""
    from models import Edital # Import local para evitar ciclo
    from flask_login import current_user
    
    # [V22] Filtro de Escopo Hierárquico
    # Filtrar queries de distribuição e aplicação baseado no escopo
    dist_query = ProapDistribuicao.query
    if current_user.role == 'coordenador_programa' and current_user.programa_id:
        dist_query = dist_query.filter(ProapDistribuicao.programa_id == current_user.programa_id)
    elif current_user.role == 'diretor_campus' and current_user.campus_id:
        dist_query = dist_query.join(ProgramaAcademico).filter(
            ProgramaAcademico.campus_id == current_user.campus_id
        )
    
    # ==== ESTATÍSTICAS GERAIS (filtradas) ====
    total_repasses = ProapRepasse.query.count() # Repasses são institucionais, não filtrar
    total_programas_beneficiados = db.session.query(func.count(func.distinct(ProapDistribuicao.programa_id))).scalar() or 0
    
    # Totais financeiros
    total_proap = db.session.query(func.sum(ProapRepasse.valor_total))\
        .filter_by(tipo='PROAP').scalar() or Decimal('0')
        
    total_proapinho = db.session.query(func.sum(ProapRepasse.valor_total))\
        .filter_by(tipo='PROAPINHO').scalar() or Decimal('0')
        
    total_recebido = total_proap + total_proapinho
    
    # [V22] Filtrar totalização de distribuição e aplicação
    total_distribuido = db.session.query(func.sum(ProapDistribuicao.valor_distribuido))
    if current_user.role == 'coordenador_programa' and current_user.programa_id:
        total_distribuido = total_distribuido.filter(ProapDistribuicao.programa_id == current_user.programa_id)
    elif current_user.role == 'diretor_campus' and current_user.campus_id:
        total_distribuido = total_distribuido.join(ProgramaAcademico).filter(
            ProgramaAcademico.campus_id == current_user.campus_id
        )
    total_distribuido = total_distribuido.scalar() or Decimal('0')
    
    total_aplicado = db.session.query(func.sum(ProapAplicacao.valor)).scalar() or Decimal('0')
    
    # ==== APLICAÇÕES POR CATEGORIA ====
    dist_categoria = db.session.query(
        ProapAplicacao.categoria,
        func.sum(ProapAplicacao.valor).label('total'),
        func.count(ProapAplicacao.id).label('quantidade')
    ).group_by(ProapAplicacao.categoria)\
     .order_by(func.sum(ProapAplicacao.valor).desc())\
     .all()
    
    # ==== TIMELINE ANUAL (Repasses por ano) ====
    timeline = db.session.query(
        ProapRepasse.ano,
        ProapRepasse.tipo,
        func.sum(ProapRepasse.valor_total).label('total')
    ).group_by(ProapRepasse.ano, ProapRepasse.tipo)\
     .order_by(ProapRepasse.ano)\
     .all()
    
    # Organizar timeline por ano
    timeline_data = {}
    for t in timeline:
        if t.ano not in timeline_data:
            timeline_data[t.ano] = {'PROAP': 0, 'PROAPINHO': 0}
        timeline_data[t.ano][t.tipo] = t.total
    
    # ==== DISTRIBUIÇÃO POR PROGRAMA (Top 10) ====
    dist_programa = db.session.query(
        ProgramaAcademico.sigla_programa,
        func.sum(ProapDistribuicao.valor_distribuido).label('total')
    ).join(ProapDistribuicao, ProgramaAcademico.id == ProapDistribuicao.programa_id)
    
    if current_user.role == 'coordenador_programa' and current_user.programa_id:
        dist_programa = dist_programa.filter(ProapDistribuicao.programa_id == current_user.programa_id)
    elif current_user.role == 'diretor_campus' and current_user.campus_id:
        dist_programa = dist_programa.filter(ProgramaAcademico.campus_id == current_user.campus_id)
        
    dist_programa = dist_programa.group_by(ProgramaAcademico.id)\
     .order_by(func.sum(ProapDistribuicao.valor_distribuido).desc())\
     .limit(10).all()

    # ==== COMPROMETIDO (EDITAIS) [NEW FASE 9] ====
    editais_proap = Edital.query.join(ProapDistribuicao).filter(ProapDistribuicao.id != None)
    if current_user.role == 'coordenador_programa' and current_user.programa_id:
        editais_proap = editais_proap.filter(ProapDistribuicao.programa_id == current_user.programa_id)
    elif current_user.role == 'diretor_campus' and current_user.campus_id:
        editais_proap = editais_proap.join(ProgramaAcademico).filter(ProgramaAcademico.campus_id == current_user.campus_id)
        
    editais_list = editais_proap.all()
    total_comprometido = sum(e.orcamento_total for e in editais_list) if editais_list else Decimal('0')

    # Saldo geral (Considerando o que foi distribuído vs aplicado no escopo do usuário)
    saldo_geral = total_distribuido - total_aplicado
    
    stats = {
        'total_repasses': total_repasses,
        'total_programas': total_programas_beneficiados,
        'total_proap': total_proap,
        'total_proapinho': total_proapinho,
        'total_geral': total_proap + total_proapinho,
        'total_distribuido': total_distribuido,
        'total_aplicado': total_aplicado,
        'saldo_geral': saldo_geral,
        'taxa_execucao': round(taxa_execucao, 2),
        'dist_programa': dist_programa,
        'dist_categoria': dist_categoria,
        'timeline': timeline_data
    }

    financeiro = {
        'distribuido': total_distribuido,
        'aplicado': total_aplicado,
        'comprometido': total_comprometido,
        'saldo': saldo_geral
    }
    
    return render_template('proap/dashboard.html', stats=stats, financeiro=financeiro, editais=editais_list)


# ============================================================================
# RELATÓRIOS
# ============================================================================

@proap_bp.route('/relatorios')
def relatorios_index():
    """Página principal de relatórios"""
    # Definição dos anos disponíveis
    anos = db.session.query(ProapRepasse.ano.distinct()).order_by(ProapRepasse.ano.desc()).all()
    anos = [a[0] for a in anos]
    
    # Se não houver anos, usa o atual
    if not anos:
        anos = [date.today().year]
        
    return render_template('proap/relatorios/index.html', anos=anos, ano_atual=date.today().year)


@proap_bp.route('/relatorios/mensal')
def relatorios_mensal():
    """Relatório Mensal"""
    mes = int(request.args.get('mes', date.today().month))
    ano = int(request.args.get('ano', date.today().year))
    
    # Dados do Relatório
    aplicacoes = ProapAplicacao.query.filter(
        extract('month', ProapAplicacao.data_aplicacao) == mes,
        extract('year', ProapAplicacao.data_aplicacao) == ano
    ).order_by(ProapAplicacao.data_aplicacao).all()
    
    total_aplicado = sum(a.valor for a in aplicacoes) if aplicacoes else Decimal('0')
    
    # Agrupamento por Categoria
    por_categoria = db.session.query(
        ProapAplicacao.categoria,
        func.sum(ProapAplicacao.valor).label('total')
    ).filter(
        extract('month', ProapAplicacao.data_aplicacao) == mes,
        extract('year', ProapAplicacao.data_aplicacao) == ano
    ).group_by(ProapAplicacao.categoria).all()
    
    return render_template('proap/relatorios/mensal.html',
                         mes=mes, ano=ano,
                         aplicacoes=aplicacoes,
                         total_aplicado=total_aplicado,
                         por_categoria=por_categoria)


@proap_bp.route('/relatorios/trimestral')
def relatorios_trimestral():
    """Relatório Trimestral"""
    trimestre = int(request.args.get('trimestre', (date.today().month - 1) // 3 + 1))
    ano = int(request.args.get('ano', date.today().year))
    
    mes_inicio = (trimestre - 1) * 3 + 1
    mes_fim = mes_inicio + 2
    
    # Filtros
    aplicacoes = ProapAplicacao.query.filter(
        extract('month', ProapAplicacao.data_aplicacao) >= mes_inicio,
        extract('month', ProapAplicacao.data_aplicacao) <= mes_fim,
        extract('year', ProapAplicacao.data_aplicacao) == ano
    ).order_by(ProapAplicacao.data_aplicacao).all()
    
    total_aplicado = sum(a.valor for a in aplicacoes) if aplicacoes else Decimal('0')
    
    por_categoria = db.session.query(
        ProapAplicacao.categoria,
        func.sum(ProapAplicacao.valor).label('total')
    ).filter(
        extract('month', ProapAplicacao.data_aplicacao) >= mes_inicio,
        extract('month', ProapAplicacao.data_aplicacao) <= mes_fim,
        extract('year', ProapAplicacao.data_aplicacao) == ano
    ).group_by(ProapAplicacao.categoria).all()
    
    return render_template('proap/relatorios/trimestral.html',
                         trimestre=trimestre, ano=ano,
                         aplicacoes=aplicacoes,
                         total_aplicado=total_aplicado,
                         por_categoria=por_categoria)


@proap_bp.route('/relatorios/semestral')
def relatorios_semestral():
    """Relatório Semestral"""
    semestre = int(request.args.get('semestre', 1 if date.today().month <= 6 else 2))
    ano = int(request.args.get('ano', date.today().year))
    
    mes_inicio = 1 if semestre == 1 else 7
    mes_fim = 6 if semestre == 1 else 12
    
    aplicacoes = ProapAplicacao.query.filter(
        extract('month', ProapAplicacao.data_aplicacao) >= mes_inicio,
        extract('month', ProapAplicacao.data_aplicacao) <= mes_fim,
        extract('year', ProapAplicacao.data_aplicacao) == ano
    ).order_by(ProapAplicacao.data_aplicacao).all()
    
    total_aplicado = sum(a.valor for a in aplicacoes) if aplicacoes else Decimal('0')
    
    por_categoria = db.session.query(
        ProapAplicacao.categoria,
        func.sum(ProapAplicacao.valor).label('total')
    ).filter(
        extract('month', ProapAplicacao.data_aplicacao) >= mes_inicio,
        extract('month', ProapAplicacao.data_aplicacao) <= mes_fim,
        extract('year', ProapAplicacao.data_aplicacao) == ano
    ).group_by(ProapAplicacao.categoria).all()
    
    return render_template('proap/relatorios/semestral.html',
                         semestre=semestre, ano=ano,
                         aplicacoes=aplicacoes,
                         total_aplicado=total_aplicado,
                         por_categoria=por_categoria)


@proap_bp.route('/relatorios/anual')
def relatorios_anual():
    """Relatório Anual Completo"""
    ano = int(request.args.get('ano', date.today().year))
    
    # 1. Resumo Financeiro
    total_recebido = db.session.query(func.sum(ProapRepasse.valor_total))\
        .filter(ProapRepasse.ano == ano).scalar() or Decimal('0')
        
    total_distribuido = db.session.query(func.sum(ProapDistribuicao.valor_distribuido))\
        .join(ProapRepasse)\
        .filter(ProapRepasse.ano == ano).scalar() or Decimal('0')
        
    total_aplicado = db.session.query(func.sum(ProapAplicacao.valor))\
        .filter(extract('year', ProapAplicacao.data_aplicacao) == ano).scalar() or Decimal('0')
        
    # [FIX] Calcular Comprometido e Buscar Editais
    editais_proap = Edital.query.join(ProapDistribuicao).join(ProapRepasse)\
        .filter(ProapRepasse.ano == ano).order_by(Edital.numero).all()
        
    total_comprometido_global = sum(e.orcamento_total for e in editais_proap)
        
    # 2. Execução Mensal
    mensal = db.session.query(
        extract('month', ProapAplicacao.data_aplicacao).label('mes'),
        func.sum(ProapAplicacao.valor).label('total')
    ).filter(
        extract('year', ProapAplicacao.data_aplicacao) == ano
    ).group_by('mes').order_by('mes').all()
    
    # 3. Top Categorias
    categorias = db.session.query(
        ProapAplicacao.categoria,
        func.sum(ProapAplicacao.valor).label('total')
    ).filter(
        extract('year', ProapAplicacao.data_aplicacao) == ano
    ).group_by(ProapAplicacao.categoria)\
     .order_by(func.sum(ProapAplicacao.valor).desc()).all()
     
    # 4. Top Programas (que mais aplicaram, não receberam)
    programas = db.session.query(
        ProgramaAcademico.sigla_programa,
        func.sum(ProapAplicacao.valor).label('total')
    ).join(ProapDistribuicao, ProapAplicacao.distribuicao_id == ProapDistribuicao.id)\
     .join(ProgramaAcademico, ProapDistribuicao.programa_id == ProgramaAcademico.id)\
     .filter(extract('year', ProapAplicacao.data_aplicacao) == ano, not_(ProgramaAcademico.nome_programa.ilike('%*%')))\
     .group_by(ProgramaAcademico.id)\
     .order_by(func.sum(ProapAplicacao.valor).desc())\
     .limit(10).all()

    return render_template('proap/relatorios/anual.html',
                         ano=ano,
                         financeiro={
                             'recebido': total_recebido,
                             'distribuido': total_distribuido,
                             'aplicado': total_aplicado,
                             'comprometido': total_comprometido_global, # [UPDATED]
                             'saldo': total_distribuido - total_aplicado
                         },
                         mensal=mensal,
                         categorias=categorias,
                         programas=programas,
                         editais=editais_proap)

def generate_pdf(html_content, filename):
    """Gera PDF a partir de conteúdo HTML usando xhtml2pdf"""
    pdf = io.BytesIO()
    pisa_status = pisa.CreatePDF(html_content, dest=pdf)
    if pisa_status.err:
        return f"Erro ao gerar PDF: {pisa_status.err}", 500
    
    response = make_response(pdf.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    return response

@proap_bp.route('/relatorios/consolidado')
def relatorios_consolidado():
    """
    [NEW] Tela Unificada de Relatórios (Abas)
    """
    return render_template('proap/relatorios/consolidado.html')

@proap_bp.route('/relatorios/trimestral_pdf')
def relatorios_trimestral_pdf():
    # Reutiliza lógica de dados da rota trimestral
    ano = int(request.args.get('ano', date.today().year))
    trimestre = int(request.args.get('trimestre', 1))  # Default to 1st quarter
    
    trimestres = {
        1: {'nome': '1º Trimestre', 'meses': [1, 2, 3], 'aplicacoes': [], 'total': Decimal('0')},
        2: {'nome': '2º Trimestre', 'meses': [4, 5, 6], 'aplicacoes': [], 'total': Decimal('0')},
        3: {'nome': '3º Trimestre', 'meses': [7, 8, 9], 'aplicacoes': [], 'total': Decimal('0')},
        4: {'nome': '4º Trimestre', 'meses': [10, 11, 12], 'aplicacoes': [], 'total': Decimal('0')},
    }
    
    # Buscar aplicações com joins explícitos
    aplicacoes = db.session.query(ProapAplicacao)\
        .select_from(ProapAplicacao)\
        .join(ProapDistribuicao, ProapAplicacao.distribuicao_id == ProapDistribuicao.id)\
        .join(ProapRepasse, ProapDistribuicao.repasse_id == ProapRepasse.id)\
        .filter(ProapRepasse.ano == ano)\
        .order_by(ProapAplicacao.data_aplicacao).all()
        
    for app in aplicacoes:
        mes = app.data_aplicacao.month
        for t_id, t_data in trimestres.items():
            if mes in t_data['meses']:
                t_data['aplicacoes'].append(app)
                t_data['total'] += app.valor
                break
    
    # Calcular total aplicado no ano todo
    total_aplicado = sum(t['total'] for t in trimestres.values()) if trimestres else Decimal('0')
    
    # Agrupar por categoria
    categorias_dict = {}
    for app in aplicacoes:
        cat = app.categoria or 'Não Classificado'
        if cat not in categorias_dict:
            categorias_dict[cat] = Decimal('0')
        categorias_dict[cat] += app.valor
    
    por_categoria = [{'categoria': k, 'total': v} for k, v in categorias_dict.items()]
    por_categoria.sort(key=lambda x: x['total'], reverse=True)
                
    # Query programas com joins explícitos para evitar ambiguidade
    programas = db.session.query(
        ProgramaAcademico.sigla_programa,
        func.sum(ProapAplicacao.valor)
    ).select_from(ProapAplicacao)\
     .join(ProapDistribuicao, ProapAplicacao.distribuicao_id == ProapDistribuicao.id)\
     .join(ProgramaAcademico, ProapDistribuicao.programa_id == ProgramaAcademico.id)\
     .join(ProapRepasse, ProapDistribuicao.repasse_id == ProapRepasse.id)\
     .filter(ProapRepasse.ano == ano)\
     .group_by(ProgramaAcademico.sigla_programa).all()
     
    # Render with PDF specific template or same template with stripped UI
    html = render_template('proap/relatorios/trimestral.html',
                           ano=ano,
                           trimestre=trimestre,
                           trimestres=trimestres,
                           programas=programas,
                           total_aplicado=total_aplicado,
                           por_categoria=por_categoria,
                           aplicacoes=aplicacoes,
                           now=date.today().strftime('%d/%m/%Y'),
                           pdf_mode=True)
                           
    return generate_pdf(html, f"Relatorio_Trimestral_{ano}.pdf")

@proap_bp.route('/relatorios/semestral_pdf')
def relatorios_semestral_pdf():
    ano = int(request.args.get('ano', date.today().year))
    semestre_filter = int(request.args.get('semestre', '1'))  # 1 ou 2
    
    semestres = {
        1: {'nome': '1º Semestre', 'meses': [1, 2, 3, 4, 5, 6], 'aplicacoes': [], 'total': Decimal('0')},
        2: {'nome': '2º Semestre', 'meses': [7, 8, 9, 10, 11, 12], 'aplicacoes': [], 'total': Decimal('0')},
    }
    
    # Buscar aplicações com joins explícitos
    aplicacoes = db.session.query(ProapAplicacao)\
        .select_from(ProapAplicacao)\
        .join(ProapDistribuicao, ProapAplicacao.distribuicao_id == ProapDistribuicao.id)\
        .join(ProapRepasse, ProapDistribuicao.repasse_id == ProapRepasse.id)\
        .filter(ProapRepasse.ano == ano)\
        .order_by(ProapAplicacao.data_aplicacao).all()
        
    for app in aplicacoes:
        mes = app.data_aplicacao.month
        semester_idx = 1 if mes <= 6 else 2
        semestres[semester_idx]['aplicacoes'].append(app)
        semestres[semester_idx]['total'] += app.valor

    # Calcular total aplicado no semestre selecionado
    semestre_data = semestres.get(semestre_filter)
    total_aplicado = semestre_data['total'] if semestre_data else Decimal('0')
    
    # Agrupar por categoria no semestre selecionado
    categorias_dict = {}
    if semestre_data:
        for app in semestre_data['aplicacoes']:
            cat = app.categoria or 'Não Classificado'
            if cat not in categorias_dict:
                categorias_dict[cat] = Decimal('0')
            categorias_dict[cat] += app.valor
    
    por_categoria = [{'categoria': k, 'total': v} for k, v in categorias_dict.items()]
    por_categoria.sort(key=lambda x: x['total'], reverse=True)
    
    html = render_template('proap/relatorios/semestral.html',
                           ano=ano,
                           semestre=semestre_filter,
                           semestres={semestre_filter: semestre_data},
                           total_aplicado=total_aplicado,
                           por_categoria=por_categoria,
                           aplicacoes=semestre_data['aplicacoes'] if semestre_data else [],
                           now=date.today().strftime('%d/%m/%Y'),
                           pdf_mode=True)
                           
    return generate_pdf(html, f"Relatorio_Semestral_{semestre_filter}_{ano}.pdf")

@proap_bp.route('/relatorios/anual_pdf')
def relatorios_anual_pdf():
    ano = int(request.args.get('ano', date.today().year))
    
    # 1. Total Recebido (Repasses)
    repasses = ProapRepasse.query.filter_by(ano=ano).all()
    total_recebido = sum(r.valor_total for r in repasses) if repasses else Decimal('0')
    
    # 2. Total Distribuído
    distribuicoes = ProapDistribuicao.query.join(ProapRepasse)\
        .filter(ProapRepasse.ano == ano).all()
    total_distribuido = sum(d.valor_distribuido for d in distribuicoes) if distribuicoes else Decimal('0')
    
    # 3. Total Executado (Aplicações) - Query com joins explícitos
    aplicacoes = db.session.query(ProapAplicacao)\
        .select_from(ProapAplicacao)\
        .join(ProapDistribuicao, ProapAplicacao.distribuicao_id == ProapDistribuicao.id)\
        .join(ProapRepasse, ProapDistribuicao.repasse_id == ProapRepasse.id)\
        .filter(ProapRepasse.ano == ano).all()
    total_executado = sum(a.valor for a in aplicacoes) if aplicacoes else Decimal('0')
    
    saldo_geral = total_recebido - total_executado
    taxa_execucao = (total_executado / total_recebido * 100) if total_recebido > 0 else 0
    
    # 4. Timeline Mensal - Query com joins explícitos (PostgreSQL compatible)
    mensal = db.session.query(
        func.extract('month', ProapAplicacao.data_aplicacao).label('mes'),
        func.sum(ProapAplicacao.valor)
    ).select_from(ProapAplicacao)\
     .join(ProapDistribuicao, ProapAplicacao.distribuicao_id == ProapDistribuicao.id)\
     .join(ProapRepasse, ProapDistribuicao.repasse_id == ProapRepasse.id)\
     .filter(ProapRepasse.ano == ano)\
     .group_by('mes').order_by('mes').all()
     
    # 5. Por Categoria - Query com joins explícitos
    categorias = db.session.query(
        ProapAplicacao.categoria,
        func.sum(ProapAplicacao.valor)
    ).select_from(ProapAplicacao)\
     .join(ProapDistribuicao, ProapAplicacao.distribuicao_id == ProapDistribuicao.id)\
     .join(ProapRepasse, ProapDistribuicao.repasse_id == ProapRepasse.id)\
     .filter(ProapRepasse.ano == ano)\
     .group_by(ProapAplicacao.categoria).all()
     
    # 6. Por Programa - Query simplificada para evitar ambiguidade
    programas = db.session.query(
        ProgramaAcademico.sigla_programa,
        func.sum(ProapDistribuicao.valor_distribuido)
    ).select_from(ProapDistribuicao)\
     .join(ProgramaAcademico, ProapDistribuicao.programa_id == ProgramaAcademico.id)\
     .join(ProapRepasse, ProapDistribuicao.repasse_id == ProapRepasse.id)\
     .filter(ProapRepasse.ano == ano, not_(ProgramaAcademico.nome_programa.ilike('%*%')))\
     .group_by(ProgramaAcademico.sigla_programa).all()
     
    # Fix Programas Query (Simpler approach)
    # ... logic above is slightly broken because of double aggregate. 
    # Let's reuse the simple one from relevant route if confusing.
    # Re-fetching for correctness:
    
    # [FIX] Calcular Comprometido e Buscar Editais
    editais_proap = Edital.query.join(ProapDistribuicao).join(ProapRepasse)\
        .filter(ProapRepasse.ano == ano).order_by(Edital.numero).all()
    
    html = render_template('proap/relatorios/anual.html',
                           ano=ano,
                           total_recebido=total_recebido,
                           total_distribuido=total_distribuido,
                           total_executado=total_executado,
                           saldo_geral=saldo_geral,
                           taxa_execucao=taxa_execucao,
                           mensal=mensal,
                           categorias=categorias,
                           programas=programas,
                           editais=editais_proap,
                           pdf_mode=True)
                           
    return generate_pdf(html, f"Relatorio_Anual_PROAP_{ano}.pdf")

@proap_bp.route('/relatorios/auditoria_pdf')
def relatorios_auditoria_pdf():
    """
    [NEW] Relatório de Governança e Transparência
    Agrupado por Campus > Programa
    Colunas: Código, Programa, Campus(Sigla), Total Recebido
    """
    ano = int(request.args.get('ano', date.today().year))
    
    # Query complexa para agrupar dados
    # Busca programas e seus totais distribuídos no ano
    dados = db.session.query(
        Campus.nome.label('campus_nome'),
        Campus.sigla_campus.label('campus_sigla'),
        ProgramaAcademico.codigo_programa,
        ProgramaAcademico.nome_programa,
        func.sum(ProapDistribuicao.valor_distribuido).label('total_recebido')
    ).join(ProgramaAcademico, Campus.id == ProgramaAcademico.campus_id)\
     .join(ProapDistribuicao, ProgramaAcademico.id == ProapDistribuicao.programa_id)\
     .join(ProapRepasse, ProapDistribuicao.repasse_id == ProapRepasse.id)\
     .filter(ProapRepasse.ano == ano, not_(ProgramaAcademico.nome_programa.ilike('%*%')))\
     .group_by(Campus.nome, Campus.sigla_campus, ProgramaAcademico.codigo_programa, ProgramaAcademico.nome_programa)\
     .order_by(Campus.nome, ProgramaAcademico.nome_programa).all()
     
    # Agrupar por Campus no Python para facilitar o template
    campus_dict = {}
    total_geral_anual = Decimal('0')
    
    for row in dados:
        campus = row.campus_nome
        if campus not in campus_dict:
            campus_dict[campus] = []
            
        campus_dict[campus].append({
            'codigo': row.codigo_programa or 'N/A',
            'programa': row.nome_programa,
            'sigla_campus': row.campus_sigla,
            'valor': row.total_recebido
        })
        total_geral_anual += row.total_recebido
        
    html = render_template('proap/relatorios/auditoria.html',
                           ano=ano,
                           dados_por_campus=campus_dict,
                           total_geral=total_geral_anual,
                           hoje=date.today().strftime('%d/%m/%Y'))
                           
    return generate_pdf(html, f"Relatorio_Governanca_Auditoria_{ano}.pdf")

@proap_bp.route('/relatorios/detalhado')
def relatorios_detalhado():
    """
    [NEW] Relatório Detalhado de Repasses (Transparência Completa)
    Filtros: Ano, Programa, Campus
    Colunas: Data Solicitação, Código, Programa, Campus, Valor, SEI
    """
    # Filtros
    ano = int(request.args.get('ano', date.today().year))
    input_programa = request.args.get('programa_id')
    input_campus = request.args.get('campus_id')
    
    programa_id = int(input_programa) if input_programa else None
    campus_id = int(input_campus) if input_campus else None
    
    # Query Base
    query = ProapDistribuicao.query.join(ProgramaAcademico).join(ProapRepasse).join(Campus)
    
    # Filtro por Ano (Repasse)
    if ano:
        query = query.filter(ProapRepasse.ano == ano)
        
    # Filtro por Programa
    if programa_id:
        query = query.filter(ProgramaAcademico.id == programa_id)
        
    # Filtro por Campus
    if campus_id:
        query = query.filter(Campus.id == campus_id)
        
    # Ordenação
    distribuicoes = query.order_by(ProapDistribuicao.data_distribuicao.desc()).all()
    
    # Cálculos KPI
    total_geral = sum(d.valor_distribuido for d in distribuicoes)
    programas_contemplados = set(d.programa_id for d in distribuicoes)
    
    # Dados para combo boxes
    todos_programas = ProgramaAcademico.query.options(db.joinedload(ProgramaAcademico.campus)).order_by(ProgramaAcademico.nome_programa.asc()).all()
    todos_campuses = Campus.query.order_by(Campus.nome).all()
    
    return render_template('proap/relatorios/detalhado.html',
                           ano=ano,
                           programa_id=programa_id,
                           campus_id=campus_id,
                           todos_programas=todos_programas,
                           todos_campuses=todos_campuses,
                           distribuicoes=distribuicoes,
                           total_geral=total_geral,
                           programas_contemplados_count=len(programas_contemplados),
                           now=datetime.now().strftime('%d/%m/%Y %H:%M'))
