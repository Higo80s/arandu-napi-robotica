from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from models import db, Bolsista, Edital, Modalidade
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/advanced')
@login_required
def advanced():
    """Renderiza a página do dashboard avançado."""
    return render_template('dashboard/advanced.html')

@dashboard_bp.route('/api/stats')
@login_required
def get_stats():
    """
    API segura que retorna dados estatísticos agregados.
    Nenhum dado pessoal (PII) é exposto aqui.
    """
    # 1. Totais Gerais
    total_ativos = Bolsista.query.filter_by(ativo=True).count()
    total_inativos = Bolsista.query.filter_by(ativo=False).count()
    total_editais = Edital.query.count()
    
    # 2. Distribuição por Modalidade (Apenas Ativos)
    # Ex: Mestrado: 10, Doutorado: 5
    modalidades_query = db.session.query(
        Modalidade.nivel, func.count(Bolsista.id)
    ).join(Bolsista).filter(Bolsista.ativo == True).group_by(Modalidade.nivel).all()
    
    modalidades_dict = {m[0]: m[1] for m in modalidades_query if m[0]}

    # 3. Evolução Temporal (Inícios de Bolsa por Mês)
    # Processamento em Python para garantir compatibilidade SQLite/Postgres
    dates = db.session.query(Bolsista.data_inicio_bolsa).filter(Bolsista.ativo == True).all()
    
    from collections import Counter
    evolution_counts = Counter()
    
    for d in dates:
        if d[0]: # d é uma tupla (date,)
            # Formato AAAA-MM
            key = d[0].strftime('%Y-%m')
            evolution_counts[key] += 1
            
    # Ordenar cronologicamente
    evolution_sorted = dict(sorted(evolution_counts.items()))

    return jsonify({
        'summary': {
            'active_scholars': total_ativos,
            'inactive_scholars': total_inativos,
            'total_edicts': total_editais
        },
        'by_modality': modalidades_dict,
        'evolution': evolution_sorted
    })
