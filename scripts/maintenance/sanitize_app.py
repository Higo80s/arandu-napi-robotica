# Script de Saneamento Total do app.py

safe_end_point = "def alertas_index():"
code_block_consolidado = """

# --- Fase 4: Painel Consolidado e Relatórios --- (Adicionado/Restaurado)

def get_consolidated_stats():
    # Função robusta para calcular estatísticas
    from sqlalchemy import func, distinct
    from models import ProgramaAcademico, Campus, Bolsista
    
    programas = ProgramaAcademico.query.all()
    mestrado = 0
    doutorado = 0
    
    for p in programas:
        niveis = (p.niveis or "").upper()
        nome = p.nome_programa.upper()
        is_mestrado = 'M' in niveis or 'MESTRADO' in nome or 'CIÊNCIAS' in nome
        is_doutorado = 'D' in niveis or 'DOUTORADO' in nome
        
        if is_doutorado: doutorado += 1
        if is_mestrado: mestrado += 1
            
    if mestrado == 0 and doutorado == 0:
        mestrado = len(programas)
    
    por_campus = db.session.query(Campus.nome, Campus.sigla_campus, func.count(distinct(ProgramaAcademico.id))).join(ProgramaAcademico, Campus.id == ProgramaAcademico.campus_id).group_by(Campus.id, Campus.nome, Campus.sigla_campus).all()
    
    multicampi_query = db.session.query(ProgramaAcademico.codigo_programa, func.count(distinct(Campus.id))).join(Campus, Campus.id == ProgramaAcademico.campus_id).group_by(ProgramaAcademico.codigo_programa).having(func.count(distinct(Campus.id)) > 1).all()
    
    total_discentes = Bolsista.query.count()
    ativos = Bolsista.query.filter_by(ativo=True).count()
    taxa_ativacao = (ativos / total_discentes * 100) if total_discentes > 0 else 0
    
    return {
        'total_mestrado': mestrado,
        'total_doutorado': doutorado,
        'total_geral': len(programas),
        'distribuicao_campus': por_campus,
        'programas_multicampi': multicampi_query,
        'total_discentes': total_discentes,
        'discentes_ativos': ativos,
        'taxa_ativacao': round(taxa_ativacao, 1)
    }

@app.route('/admin/consolidado')
def admin_consolidado():
    stats = get_consolidated_stats()
    return render_template('admin/consolidado.html', **stats)

@app.route('/relatorios/consolidado/download')
def download_consolidado():
    import pandas as pd
    from io import BytesIO
    from flask import send_file
    from datetime import datetime
    
    stats = get_consolidated_stats()
    
    df_campus = pd.DataFrame(stats['distribuicao_campus'], columns=['Campus', 'Sigla', 'Programas'])
    df_multicampi = pd.DataFrame(stats['programas_multicampi'], columns=['Código Programa', 'Qtd Campus'])
    df_resumo = pd.DataFrame([
        {'Métrica': 'Total Mestrado', 'Valor': stats['total_mestrado']},
        {'Métrica': 'Total Doutorado', 'Valor': stats['total_doutorado']},
        {'Métrica': 'Total Geral Programas', 'Valor': stats['total_geral']},
        {'Métrica': 'Total Discentes', 'Valor': stats['total_discentes']},
        {'Métrica': 'Discentes Ativos', 'Valor': stats['discentes_ativos']},
        {'Métrica': 'Taxa Ativação (%)', 'Valor': stats['taxa_ativacao']}
    ])
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_resumo.to_excel(writer, sheet_name='Resumo', index=False)
        df_campus.to_excel(writer, sheet_name='Por Campus', index=False)
        if not df_multicampi.empty:
            df_multicampi.to_excel(writer, sheet_name='Multicampi', index=False)
            
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name=f'Relatorio_Consolidado_UTFPR_{datetime.now().strftime("%Y%m%d")}.xlsx')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5003)
"""

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

cut_index = -1
for i, line in enumerate(lines):
    if "def alertas_index():" in line:
        # Encontrei o início de alertas. Preciso achar o final dela.
        # Aproximadamente 35 linhas depois...
        cut_index = i + 40 # Chute seguro para depois do return render_template
        break

# Ajuste fino: encontrar onde alertas_index termina (return render_template ou o próximo def ou if name)
real_cut_index = -1
if cut_index != -1:
    for i in range(cut_index, len(lines)):
        if "return render_template('alertas/index.html'" in lines[i]:
             # + 5 linhas para garantir o fechamento do parenteses
             real_cut_index = i + 5
             break

if real_cut_index != -1:
    # Manter tudo até o fim de alertas_index
    clean_content = "".join(lines[:real_cut_index])
    # Adicionar o novo bloco limpo
    final_content = clean_content + code_block_consolidado
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(final_content)
    print("✅ Arquivo saneado e reconstruído com sucesso!")
else:
    print("⚠️ Não foi possível encontrar ponto de corte seguro.")
