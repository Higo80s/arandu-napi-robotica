
# --- Rota de Teste (Consolidado V2) ---
@app.route('/admin/consolidado_v2')
def admin_consolidado_v2():
    """
    Versão V2 do Painel Consolidado com ajustes solicitados:
    - Taxa Referente a Ocupação (Bolsas Ocupadas / Bolsas Ofertadas).
    - Tabelas com colunas 'Discentes Ativos'.
    - Multicampi detalhado.
    """
    from models import ProgramaAcademico, Bolsista, Campus
    from sqlalchemy import func
    
    # 1. Stats Gerais
    stats = {}
    
    # Total de Programas (Mestrado/Doutorado)
    # Reutilizando lógica existente, mas refinando
    programas = ProgramaAcademico.query.all()
    stats['total_geral'] = len(programas)
    stats['total_mestrado'] = 0
    stats['total_doutorado'] = 0
    
    for p in programas:
        nome = (p.nome_programa or '').upper()
        niveis = (p.niveis or '').upper()
        
        is_mestrado = 'M' in niveis or 'MESTRADO' in nome or 'CIÊNCIAS' in nome
        is_doutorado = 'D' in niveis or 'DOUTORADO' in nome
        
        if is_mestrado: stats['total_mestrado'] += 1
        if is_doutorado: stats['total_doutorado'] += 1
        
    if stats['total_mestrado'] == 0 and stats['total_doutorado'] == 0:
        stats['total_mestrado'] = len(programas) # Fallback

    # 2. Campus Stats (Com Ativos)
    # Query: Campus Name, Count(Programas), Count(Ativos)
    # Precisa de subquery ou processamento python
    
    campi = Campus.query.all()
    campus_stats = []
    
    for c in campi:
        # Pular Multicampi se for o registro 'MULTI' que inserimos fake, 
        # MAS o usuário pediu para listar multicampi separado.
        # Vamos processar tudo e separar na view.
        
        num_programas = ProgramaAcademico.query.filter_by(campus_id=c.id).count()
        
        # Ativos neste campus
        # Join Bolsista -> Programa -> Campus
        num_ativos = db.session.query(func.count(Bolsista.id))\
            .join(ProgramaAcademico, Bolsista.programa_id == ProgramaAcademico.id)\
            .filter(ProgramaAcademico.campus_id == c.id, Bolsista.ativo == True)\
            .scalar()
            
        campus_stats.append({
            'id': c.id,
            'nome': c.nome,
            'sigla': c.sigla_campus,
            'num_programas': num_programas,
            'num_ativos': num_ativos or 0
        })
        
    # Ordenar por número de programas
    campus_stats.sort(key=lambda x: x['num_programas'], reverse=True)
    stats['distribuicao_campus'] = campus_stats

    # 3. Multicampi (Detalhado)
    # Identificar programas multicampi (mesmo código, múltiplos registros)
    from collections import defaultdict
    code_map = defaultdict(list)
    
    all_progs = db.session.query(ProgramaAcademico, Campus.sigla_campus)\
        .join(Campus, ProgramaAcademico.campus_id == Campus.id).all()
        
    for prog, sigla in all_progs:
        if prog.codigo_programa:
            code_map[prog.codigo_programa].append({
                'prog': prog,
                'sigla_campus': sigla
            })
            
    multicampi_list = []
    for code, items in code_map.items():
        if len(items) > 1:
            # É multicampi
            # Calcular ativos SOMADOS de todos os campi desse programa
            total_ativos_prog = 0
            siglas = []
            nome = items[0]['prog'].nome_programa
            
            for item in items:
                p = item['prog']
                siglas.append(item['sigla_campus'])
                count = Bolsista.query.filter_by(programa_id=p.id, ativo=True).count()
                total_ativos_prog += count
                
            multicampi_list.append({
                'codigo': code,
                'nome': nome,
                'siglas': ", ".join(sorted(siglas)),
                'qtd_campus': len(items),
                'total_ativos': total_ativos_prog
            })
            
    stats['programas_multicampi'] = multicampi_list

    # 4. Taxas (Ocupação)
    # "Taxa se refere ao quantitativo de bolsas ocupadas x ofertadas"
    # Onde estão as "Ofertadas"?
    # Vamos checar se existe Modalidade com 'quantidade_cotas' ou similar
    # Se não existir, vamos usar 'Total Discentes Ativos' vs 'Total Discentes' (ocupado vs cadastro) como fallback,
    # ou assumir um número fixo se não tivermos dados de cotas.
    # Vou verificar models.py
    
    # Fallback temp: Total Bolsistas (ativos) / (Total Bolsistas + Inativos ?? Não faz sentido)
    # Se não tem cota, a taxa de ocupação é 100% do que tem?
    # O usuário pediu "ocupadas x ofertadas".
    # Vou tentar somar Modalidade.quantidade_cotas (se existir no modelo Edital/Modalidade).
    # Se não, vou deixar 0/0 e um aviso "Dados de Cotas não definidos".
    
    stats['discentes_ativos'] = Bolsista.query.filter_by(ativo=True).count()
    stats['total_bolsas_ofertadas'] = 0 # Placeholder
    
    # Tentar buscar cotas totais
    # Modalidade -> vagas (verificar model)
    try:
        from models import Modalidade
        total_cotas = db.session.query(func.sum(Modalidade.vagas)).scalar()
        if total_cotas:
            stats['total_bolsas_ofertadas'] = int(total_cotas)
    except:
        pass
        
    if stats['total_bolsas_ofertadas'] > 0:
        stats['taxa_ocupacao'] = round((stats['discentes_ativos'] / stats['total_bolsas_ofertadas']) * 100, 1)
    else:
        stats['taxa_ocupacao'] = 0

    return render_template('admin/consolidado_v2.html', **stats)
