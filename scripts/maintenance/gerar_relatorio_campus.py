"""
Relatório Consolidado de Bolsas por Campus
Contabiliza TODAS as bolsas cadastradas no sistema (todos os editais)
Agrupa por Campus e separa Mestrado/Doutorado
"""

from app import app, db
from models import Bolsista, Campus
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter
from collections import defaultdict
from datetime import datetime
import io

def gerar_relatorio_campus_consolidado():
    """
    Gera relatório Excel consolidado:
    - Linhas: Campus (ordenados alfabeticamente)
    - Colunas: Mestrado | Doutorado | Total
    - Dados: TODAS as bolsas registradas (todos os editais)
    
    Retorna BytesIO para download direto via Flask
    """
    
    # Estrutura: {campus: {'M': count, 'D': count}}
    dados = defaultdict(lambda: {'M': 0, 'D': 0})
    
    # Buscar TODOS os bolsistas do sistema
    bolsistas = Bolsista.query.all()
    
    print(f"📊 Processando {len(bolsistas)} bolsistas...")
    
    for b in bolsistas:
        # Determinar campus
        if b.programa_link and b.programa_link.campus:
            campus_sigla = b.programa_link.campus.sigla_campus
        elif b.programa and '(' in b.programa:
            # Extrair campus do campo texto (ex: "PPGEM (CT)")
            campus_sigla = b.programa.split('(')[-1].strip(')')
        else:
            campus_sigla = 'NÃO INFORMADO'
        
        # Determinar nível
        if not b.modalidade:
            continue
        
        nivel_raw = b.modalidade.nivel.upper()
        if 'MESTRADO' in nivel_raw or 'MASTER' in nivel_raw or nivel_raw == 'M':
            nivel = 'M'
        elif 'DOUTORADO' in nivel_raw or 'DOCTOR' in nivel_raw or 'PHD' in nivel_raw or nivel_raw == 'D':
            nivel = 'D'
        else:
            continue  # Ignora outros níveis (IC, Pós-doc, etc)
        
        # Contabilizar
        dados[campus_sigla][nivel] += 1
    
    # Criar Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Bolsas por Campus"
    
    # Estilos
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=12)
    total_fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
    total_font = Font(bold=True, size=11)
    
    # Título
    ws.merge_cells('A1:D1')
    ws['A1'] = "Demonstrativo das Bolsas de Pós-graduação - UTFPR"
    ws['A1'].font = Font(bold=True, size=14)
    ws['A1'].alignment = Alignment(horizontal='center')
    
    # Subtítulo
    ws.merge_cells('A2:D2')
    ws['A2'] = f"Consolidado de todos os editais cadastrados no sistema"
    ws['A2'].font = Font(italic=True, size=10)
    ws['A2'].alignment = Alignment(horizontal='center')
    
    # Cabeçalho
    row = 4
    headers = ['Campus', 'Mestrado', 'Doutorado', 'TOTAL']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=row, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal='center')
    
    # Ordenar campus alfabeticamente
    campus_ordenados = sorted(dados.keys())
    
    # Dados por Campus
    row = 5
    total_mestrado = 0
    total_doutorado = 0
    
    for campus in campus_ordenados:
        mestrado = dados[campus]['M']
        doutorado = dados[campus]['D']
        total_campus = mestrado + doutorado
        
        ws.cell(row=row, column=1, value=campus)
        ws.cell(row=row, column=2, value=mestrado)
        ws.cell(row=row, column=3, value=doutorado)
        ws.cell(row=row, column=4, value=total_campus)
        
        # Centralizar números
        for col in [2, 3, 4]:
            ws.cell(row=row, column=col).alignment = Alignment(horizontal='center')
        
        total_mestrado += mestrado
        total_doutorado += doutorado
        row += 1
    
    # Linha de totais
    ws.cell(row=row, column=1, value='TOTAL')
    ws.cell(row=row, column=1).font = total_font
    
    ws.cell(row=row, column=2, value=total_mestrado)
    ws.cell(row=row, column=2).font = total_font
    ws.cell(row=row, column=2).fill = total_fill
    ws.cell(row=row, column=2).alignment = Alignment(horizontal='center')
    
    ws.cell(row=row, column=3, value=total_doutorado)
    ws.cell(row=row, column=3).font = total_font
    ws.cell(row=row, column=3).fill = total_fill
    ws.cell(row=row, column=3).alignment = Alignment(horizontal='center')
    
    total_geral = total_mestrado + total_doutorado
    ws.cell(row=row, column=4, value=total_geral)
    ws.cell(row=row, column=4).font = Font(bold=True, size=12, color="FFFFFF")
    ws.cell(row=row, column=4).fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    ws.cell(row=row, column=4).alignment = Alignment(horizontal='center')
    
    # Observações
    row += 2
    ws.merge_cells(f'A{row}:D{row}')
    ws.cell(row=row, column=1, value=f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}")
    ws.cell(row=row, column=1).font = Font(italic=True, size=9)
    
    row += 1
    ws.merge_cells(f'A{row}:D{row}')
    ws.cell(row=row, column=1, value="Fonte: Sistema de Gestão de Editais PROPPG")
    ws.cell(row=row, column=1).font = Font(italic=True, size=9)
    
    # Ajustar larguras
    ws.column_dimensions['A'].width = 20
    ws.column_dimensions['B'].width = 15
    ws.column_dimensions['C'].width = 15
    ws.column_dimensions['D'].width = 15
    
    # Salvar em BytesIO para download
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    print(f"✅ Relatório gerado: {len(campus_ordenados)} campus, {total_mestrado} M + {total_doutorado} D = {total_geral} total")
    
    return output


if __name__ == '__main__':
    with app.app_context():
        gerar_relatorio_campus_consolidado()
        # Salvar localmente para teste
        wb = Workbook()
        ws = wb.active
        ws.title = "Test"
        wb.save('teste_relatorio_campus.xlsx')
        print("Teste local salvo!")
