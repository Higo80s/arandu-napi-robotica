# Função auxiliar para estatísticas consolidadas
def get_consolidated_stats():
    """Calcula estatísticas consolidadas do sistema."""
    from sqlalchemy import func, distinct
    from models import ProgramaAcademico, Campus, Bolsista
    
    # 1. Contagem de cursos por nível
    programas = ProgramaAcademico.query.all()
    
    mestrado = [p for p in programas if 'MESTRADO' in p.nome_programa.upper()]
    doutorado = [p for p in programas if 'DOUTORADO' in p.nome_programa.upper()]
    
    # 2. Distribuição por campus
    por_campus = db.session.query(
        Campus.nome,
        Campus.sigla_campus,
        func.count(distinct(ProgramaAcademico.id))
    ).join(
        ProgramaAcademico, 
        Campus.id == ProgramaAcademico.campus_id
    ).group_by(Campus.id, Campus.nome, Campus.sigla_campus).all()
    
    # 3. Programas multicampi (mesmo código em vários campus)
    multicampi_query = db.session.query(
        ProgramaAcademico.codigo_programa,
        func.count(distinct(Campus.id))
    ).join(
        Campus,
        Campus.id == ProgramaAcademico.campus_id
    ).group_by(
        ProgramaAcademico.codigo_programa
    ).having(func.count(distinct(Campus.id)) > 1).all()
    
    # 4. Taxa de discentes ativos
    total_discentes = Bolsista.query.count()
    ativos = Bolsista.query.filter_by(ativo=True).count()
    taxa_ativacao = (ativos / total_discentes * 100) if total_discentes > 0 else 0
    
    return {
        'total_mestrado': len(mestrado),
        'total_doutorado': len(doutorado),
        'total_geral': len(mestrado) + len(doutorado),
        'distribuicao_campus': por_campus,
        'programas_multicampi': multicampi_query,
        'total_discentes': total_discentes,
        'discentes_ativos': ativos,
        'taxa_ativacao': round(taxa_ativacao, 1)
    }

# Rota para painel consolidado
@app.route('/admin/consolidado')
def admin_consolidado():
    """Dashboard consolidado com estatísticas acadêmicas."""
    stats = get_consolidated_stats()
    return render_template('admin/consolidado.html', **stats)
