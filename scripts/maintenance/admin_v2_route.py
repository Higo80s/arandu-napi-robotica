
# --- Rota de Teste para Fase 5.1 (Admin Programas V2) ---

@app.route('/admin/programas_v2')
def admin_programas_v2():
    """
    Lista estendida de programas para validação (Novas colunas + Contagem de Ativos).
    """
    from models import ProgramaAcademico, Bolsista, Campus
    from sqlalchemy import func, case
    
    # Query complexa para trazer contagem de ativos por programa
    # Precisamos fazer um join left com Bolsistas (ativos) e agrupar
    
    # Subquery para contar ativos
    subquery_ativos = db.session.query(
        Bolsista.programa_id,
        func.count(Bolsista.id).label('ativos_count')
    ).filter(
        Bolsista.ativo == True
    ).group_by(Bolsista.programa_id).subquery()
    
    # Query principal
    # Se quiser multicampi agrupado, a lógica complica. Por enquanto vamos listar linha a linha,
    # mas o usuário pediu "Campus/campi". Se for multicampi, deve aparecer todos?
    # O modelo atual (ProgramaAcademico) tem 1 campus_id por linha.
    # Programas multicampi são linhas diferentes com mesmo 'codigo_programa'.
    
    # Vamos agrupar por codigo_programa para tratar multicampi?
    # Se agruparmos, como mostrar o ID para edição?
    # O usuário pediu "Campus/Campi". 
    # Vou fazer uma query que, para cada linha (programa_academico), traz os dados normais.
    # E vamos tentar detectar se ele faz parte de um grupo multicampi na hora de exibir (via python ou group concat).
    
    results = db.session.query(
        ProgramaAcademico,
        Campus.sigla_campus,
        func.coalesce(subquery_ativos.c.ativos_count, 0).label('ativos_count')
    ).join(
        Campus, ProgramaAcademico.campus_id == Campus.id
    ).outerjoin(
        subquery_ativos, ProgramaAcademico.id == subquery_ativos.c.programa_id
    ).order_by(ProgramaAcademico.nome_programa).all()
    
    # Pós-processamento para identificar multicampi (opcional, ou podemos deixar simples por enquanto)
    # Lista de dicionários para facilitar o template
    programas_data = []
    
    # Dicionário auxiliar para contar campi por código (para saber se é multicampi)
    campi_por_codigo = {}
    for r in results:
        prog = r[0]
        code = prog.codigo_programa
        if code:
             campi_por_codigo[code] = campi_por_codigo.get(code, 0) + 1
             
    for r in results:
        prog = r[0]
        sigla_campus = r[1]
        ativos = r[2]
        
        is_multicampi = False
        if prog.codigo_programa and campi_por_codigo.get(prog.codigo_programa, 0) > 1:
            is_multicampi = True
            
        programas_data.append({
            'id': prog.id,
            'codigo_programa': prog.codigo_programa,
            'nome_programa': prog.nome_programa,
            'sigla_programa': prog.sigla_programa,
            'campus_sigla': sigla_campus,
            'campus_count': campi_por_codigo.get(prog.codigo_programa, 1) if prog.codigo_programa else 1,
            'niveis': prog.niveis,
            'area_avaliacao': prog.area_avaliacao,
            'area_basica': prog.area_basica,
            'ano_inicio': prog.ano_inicio,
            'nota_capes': prog.nota_capes,
            'ativos_count': ativos
        })

    return render_template('admin/programas_v2.html', programas=programas_data)
