"""
Script para gerar relatórios de bolsas por programa e agência de fomento
Formato: Excel separado para Mestrado e Doutorado
Modelo baseado nos relatórios históricos da PROPPG
"""

from app import app, db
from models import Bolsista, ProgramaAcademico, Modalidade
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from collections import defaultdict

def gerar_relatorio_bolsas_por_programa():
    """
    Gera relatórios Excel de bolsas agrupadas por:
    - Programa
    - Agência de fomento (CAPES, CNPq, Outras)
    - Ano (2014-2025)
    
    Cria dois arquivos:
    - relatorio_mestrado_por_programa.xlsx
    - relatorio_doutorado_por_programa.xlsx
    """
    
    with app.app_context():
        # Buscar todos os bolsistas
        bolsistas = Bolsista.query.all()
        
        # Estrutura de dados: {nivel: {programa: {agencia: {ano: count}}}}
        dados = {
            'Mestrado': defaultdict(lambda: defaultdict(lambda: defaultdict(int))),
            'Doutorado': defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        }
        
        # Processar bolsistas
        for b in bolsistas:
            if not b.data_inicio_bolsa or not b.modalidade:
                continue
            
            # Determinar nível (Mestrado ou Doutorado)
            nivel_raw = b.modalidade.nivel.upper()
            if 'MESTRADO' in nivel_raw or 'MASTER' in nivel_raw:
                nivel = 'Mestrado'
            elif 'DOUTORADO' in nivel_raw or 'DOCTOR' in nivel_raw or 'PHD' in nivel_raw:
                nivel = 'Doutorado'
            else:
                continue  # Pula outros níveis
            
            # Determinar programa
            if b.programa_link:
                programa = b.programa_link.sigla_programa
            elif b.programa:
                # Extrair sigla do texto (ex: "PPGEM - Mecânica" -> "PPGEM")
                programa = b.programa.split(' - ')[0].split('(')[0].strip()
            else:
                programa = 'Não Informado'
            
            # Determinar agência
            agencia_raw = b.agencia_fomento if b.agencia_fomento else 'CAPES'
            agencia_raw = agencia_raw.upper()
            
            if 'CAPES' in agencia_raw:
                agencia = 'CAPES'
            elif 'CNPq' in agencia_raw or 'CNPQ' in agencia_raw:
                agencia = 'CNPq'
            else:
                agencia = 'Outras'
            
            # Ano de início
            ano = b.data_inicio_bolsa.year
            
            # Contar apenas anos relevantes (2014-2025)
            if 2014 <= ano <= 2025:
                dados[nivel][programa][agencia][ano] += 1
        
        # Gerar Excel para cada nível
        for nivel in ['Mestrado', 'Doutorado']:
            criar_excel_por_nivel(dados[nivel], nivel)
        
        print("✅ Relatórios gerados com sucesso!")
        print("📄 relatorio_mestrado_por_programa.xlsx")
        print("📄 relatorio_doutorado_por_programa.xlsx")



def populate_sheet(ws, dados, nivel, anos):
    """
    Helper function to populate a worksheet with scholarship data.
    """
    from openpyxl.styles import Font, Alignment, PatternFill
    from openpyxl.utils import get_column_letter
    from collections import defaultdict

    # Estilos
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    total_fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
    total_font = Font(bold=True, size=11)
    
    # Título
    ws.merge_cells('A1:P1')
    ws['A1'] = f"Número de bolsas nos programas de {nivel.lower()} da UTFPR"
    ws['A1'].font = Font(bold=True, size=14)
    ws['A1'].alignment = Alignment(horizontal='center')
    
    # Cabeçalho
    row = 3
    ws[f'A{row}'] = ''
    ws[f'B{row}'] = 'Programa'
    ws[f'C{row}'] = 'Agência'
    
    col = 4
    for ano in anos:
        ws.cell(row=row, column=col, value=ano)
        ws.cell(row=row, column=col).font = header_font
        ws.cell(row=row, column=col).fill = header_fill
        ws.cell(row=row, column=col).alignment = Alignment(horizontal='center')
        col += 1
    
    # Aplicar estilo no cabeçalho
    for c in ['A', 'B', 'C']:
        ws[f'{c}{row}'].font = header_font
        ws[f'{c}{row}'].fill = header_fill
        ws[f'{c}{row}'].alignment = Alignment(horizontal='center')
    
    # Ordenar programas
    programas_ordenados = sorted(dados.keys())
    
    # Dados por programa
    row = 4
    num_programa = 1
    totais_gerais = {'CAPES': defaultdict(int), 'CNPq': defaultdict(int), 'Outras': defaultdict(int)}
    
    for programa in programas_ordenados:
        agencias_programa = dados[programa]
        total_programa_por_ano = defaultdict(int)
        
        # CAPES
        ws.cell(row=row, column=1, value=num_programa)
        ws.cell(row=row, column=2, value=programa)
        ws.cell(row=row, column=3, value='CAPES')
        col = 4
        for ano in anos:
            valor = agencias_programa['CAPES'].get(ano, 0)
            if valor > 0:
                ws.cell(row=row, column=col, value=valor)
                total_programa_por_ano[ano] += valor
                totais_gerais['CAPES'][ano] += valor
            else:
                ws.cell(row=row, column=col, value='–')
            ws.cell(row=row, column=col).alignment = Alignment(horizontal='center')
            col += 1
        row += 1
        
        # CNPq
        ws.cell(row=row, column=3, value='CNPq')
        col = 4
        for ano in anos:
            valor = agencias_programa['CNPq'].get(ano, 0)
            if valor > 0:
                ws.cell(row=row, column=col, value=valor)
                total_programa_por_ano[ano] += valor
                totais_gerais['CNPq'][ano] += valor
            else:
                ws.cell(row=row, column=col, value='–')
            ws.cell(row=row, column=col).alignment = Alignment(horizontal='center')
            col += 1
        row += 1
        
        # Outras
        ws.cell(row=row, column=3, value='Outras')
        col = 4
        for ano in anos:
            valor = agencias_programa['Outras'].get(ano, 0)
            if valor > 0:
                ws.cell(row=row, column=col, value=valor)
                total_programa_por_ano[ano] += valor
                totais_gerais['Outras'][ano] += valor
            else:
                ws.cell(row=row, column=col, value='–')
            ws.cell(row=row, column=col).alignment = Alignment(horizontal='center')
            col += 1
        row += 1
        
        # Total do programa
        ws.cell(row=row, column=3, value='Total')
        ws.cell(row=row, column=3).font = Font(bold=True)
        col = 4
        for ano in anos:
            valor = total_programa_por_ano.get(ano, 0)
            ws.cell(row=row, column=col, value=valor if valor > 0 else '–')
            ws.cell(row=row, column=col).font = Font(bold=True)
            ws.cell(row=row, column=col).alignment = Alignment(horizontal='center')
            col += 1
        row += 1
        num_programa += 1
    
    # Totais gerais
    row += 1
    ws.cell(row=row, column=1, value='Total de bolsas')
    ws.cell(row=row, column=2, value=nivel.lower())
    ws.cell(row=row, column=1).font = total_font
    ws.cell(row=row, column=2).font = total_font
    
    # CAPES Total
    ws.cell(row=row, column=3, value='CAPES').font = total_font
    ws.cell(row=row, column=3).fill = total_fill
    col = 4
    for ano in anos:
        valor = totais_gerais['CAPES'].get(ano, 0)
        ws.cell(row=row, column=col, value=valor if valor > 0 else '–')
        ws.cell(row=row, column=col).font = total_font
        ws.cell(row=row, column=col).fill = total_fill
        ws.cell(row=row, column=col).alignment = Alignment(horizontal='center')
        col += 1
    row += 1
    
    # CNPq Total
    ws.cell(row=row, column=3, value='CNPq').font = total_font
    ws.cell(row=row, column=3).fill = total_fill
    col = 4
    for ano in anos:
        valor = totais_gerais['CNPq'].get(ano, 0)
        ws.cell(row=row, column=col, value=valor if valor > 0 else '–')
        ws.cell(row=row, column=col).font = total_font
        ws.cell(row=row, column=col).fill = total_fill
        ws.cell(row=row, column=col).alignment = Alignment(horizontal='center')
        col += 1
    row += 1
    
    # Outras Total
    ws.cell(row=row, column=3, value='Outras').font = total_font
    ws.cell(row=row, column=3).fill = total_fill
    col = 4
    for ano in anos:
        valor = totais_gerais['Outras'].get(ano, 0)
        ws.cell(row=row, column=col, value=valor if valor > 0 else '–')
        ws.cell(row=row, column=col).font = total_font
        ws.cell(row=row, column=col).fill = total_fill
        ws.cell(row=row, column=col).alignment = Alignment(horizontal='center')
        col += 1
    row += 1
    
    # Total Geral
    ws.cell(row=row, column=3, value='Total').font = Font(bold=True, size=12)
    ws.cell(row=row, column=3).fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    col = 4
    for ano in anos:
        total_ano = sum(totais_gerais[ag].get(ano, 0) for ag in ['CAPES', 'CNPq', 'Outras'])
        ws.cell(row=row, column=col, value=total_ano if total_ano > 0 else '–')
        ws.cell(row=row, column=col).font = Font(bold=True, size=12)
        ws.cell(row=row, column=col).fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        ws.cell(row=row, column=col).alignment = Alignment(horizontal='center')
        col += 1
    
    # Fonte
    row += 2
    ws.cell(row=row, column=1, value='Fonte: DIRPPG, PROPPG, CNPq e CAPES')
    ws.cell(row=row, column=1).font = Font(italic=True, size=9)
    
    # Ajustar larguras
    ws.column_dimensions['A'].width = 5
    ws.column_dimensions['B'].width = 25
    ws.column_dimensions['C'].width = 12
    for i in range(4, 4 + len(anos)):
        ws.column_dimensions[get_column_letter(i)].width = 8

def get_data_for_level(bolsistas, nivel_target):
    """
    Filters bolsistas and aggregates data for a specific level.
    """
    from collections import defaultdict
    dados = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    
    for b in bolsistas:
        if not b.data_inicio_bolsa or not b.modalidade:
            continue
        
        nivel_raw = b.modalidade.nivel.upper()
        if nivel_target == 'Mestrado':
            if not ('MESTRADO' in nivel_raw or 'MASTER' in nivel_raw):
                continue
        elif nivel_target == 'Doutorado':
            if not ('DOUTORADO' in nivel_raw or 'DOCTOR' in nivel_raw or 'PHD' in nivel_raw):
                continue
        else:
            continue
        
        if b.programa_link:
            programa = b.programa_link.sigla_programa
        elif b.programa:
            programa = b.programa.split(' - ')[0].split('(')[0].strip()
        else:
            programa = 'Não Informado'
        
        agencia_raw = b.agencia_fomento if b.agencia_fomento else 'CAPES'
        agencia_raw = agencia_raw.upper()
        
        if 'CAPES' in agencia_raw:
            agencia = 'CAPES'
        elif 'CNPq' in agencia_raw or 'CNPQ' in agencia_raw:
            agencia = 'CNPq'
        else:
            agencia = 'Outras'
        
        ano = b.data_inicio_bolsa.year
        if 2014 <= ano <= 2025:
            dados[programa][agencia][ano] += 1
            
    return dados

def gerar_relatorio_especifico(nivel):
    """
    Gera relatório Excel para um nível específico (Mestrado ou Doutorado)
    e retorna como BytesIO para download direto via Flask.
    """
    from openpyxl import Workbook
    import io
    
    bolsistas = Bolsista.query.all()
    dados = get_data_for_level(bolsistas, nivel)
    
    wb = Workbook()
    ws = wb.active
    ws.title = f"Bolsas {nivel}"
    
    anos = list(range(2014, 2026))
    populate_sheet(ws, dados, nivel, anos)
    
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output

def gerar_relatorio_unificado():
    """
    Gera um único arquivo Excel contendo duas abas: Mestrado e Doutorado.
    """
    from openpyxl import Workbook
    import io
    
    bolsistas = Bolsista.query.all()
    
    wb = Workbook()
    # Remover sheet padrão
    wb.remove(wb.active)
    
    anos = list(range(2014, 2026))
    
    # Processar Mestrado
    ws_mestrado = wb.create_sheet("Mestrado")
    dados_mestrado = get_data_for_level(bolsistas, 'Mestrado')
    populate_sheet(ws_mestrado, dados_mestrado, 'Mestrado', anos)
    
    # Processar Doutorado
    ws_doutorado = wb.create_sheet("Doutorado")
    dados_doutorado = get_data_for_level(bolsistas, 'Doutorado')
    populate_sheet(ws_doutorado, dados_doutorado, 'Doutorado', anos)
    
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output

if __name__ == '__main__':
    gerar_relatorio_bolsas_por_programa()
