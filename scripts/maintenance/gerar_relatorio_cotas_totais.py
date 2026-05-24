"""
Script para gerar relatório de COTAS totais da UTFPR (não bolsistas)
Mostra quantas vagas/cotas estão cadastradas, independente de estarem ocupadas
"""

from app import app, db
from models import DistribuicaoCotas, ProgramaAcademico, Campus
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from collections import defaultdict

def gerar_relatorio_cotas_totais():
    """
    Gera relatórios Excel de COTAS (vagas) cadastradas na UTFPR
    Separado por nível (Mestrado/Doutorado) e agência (CAPES DS, CAPES IES)
    
    IMPORTANTE: Este relatório mostra COTAS, não bolsistas ocupados!
    
    Dados extraídos:
    - CAPES DS (Edital 14): 414 cotas fixas por programa
    - CAPES IES (Edital 13): 23 cotas rotativas
    
    Total: 437 cotas CAPES
    """
    
    with app.app_context():
        print("=== GERANDO RELATÓRIO DE COTAS TOTAIS UTFPR ===\n")
        
        # Buscar todas as cotas (distribuição por programa)
        cotas_ds = DistribuicaoCotas.query.filter_by(edital_id=14).all()
        cotas_ies = DistribuicaoCotas.query.filter_by(edital_id=13).all()
        
        # Estrutura: {nivel: {programa: {tipo: quantidade}}}
        dados = {
            'Mestrado': defaultdict(lambda: {'CAPES DS': 0, 'CAPES IES': 0}),
            'Doutorado': defaultdict(lambda: {'CAPES DS': 0, 'CAPES IES': 0})
        }
        
        # Totais gerais
        totais = {
            'Mestrado': {'CAPES DS': 0, 'CAPES IES': 0},
            'Doutorado': {'CAPES DS': 0, 'CAPES IES': 0}
        }
        
        # Processar CAPES DS (414 cotas por programa)
        for cota in cotas_ds:
            if cota.programa:
                programa_nome = f"{cota.programa.sigla_programa} - {cota.programa.campus.sigla_campus}"
                nivel = 'Mestrado' if cota.nivel == 'M' else 'Doutorado'
                
                dados[nivel][programa_nome]['CAPES DS'] += cota.quantidade
                totais[nivel]['CAPES DS'] += cota.quantidade
        
        # Processar CAPES IES (23 cotas rotativas - NÃO vinculadas a programa)
        for cota in cotas_ies:
            nivel = 'Mestrado' if cota.nivel == 'M' else 'Doutorado'
            # IES são cotas livres/rotativas
            programa_nome = "COTAS ROTATIVAS (IES)"
            
            dados[nivel][programa_nome]['CAPES IES'] += cota.quantidade
            totais[nivel]['CAPES IES'] += cota.quantidade
        
        # Gerar Excel para cada nível
        for nivel in ['Mestrado', 'Doutorado']:
            criar_excel_cotas(dados[nivel], totais[nivel], nivel)
        
        print("\n✅ Relatórios de COTAS gerados com sucesso!")
        print("📄 relatorio_cotas_mestrado.xlsx")
        print("📄 relatorio_cotas_doutorado.xlsx")
        print(f"\n📊 Total Mestrado: {totais['Mestrado']['CAPES DS']} DS + {totais['Mestrado']['CAPES IES']} IES = {totais['Mestrado']['CAPES DS'] + totais['Mestrado']['CAPES IES']}")
        print(f"📊 Total Doutorado: {totais['Doutorado']['CAPES DS']} DS + {totais['Doutorado']['CAPES IES']} IES = {totais['Doutorado']['CAPES DS'] + totais['Doutorado']['CAPES IES']}")


def criar_excel_cotas(dados, totais, nivel):
    """
    Cria arquivo Excel para cotas de um nível específico
    """
    wb = Workbook()
    ws = wb.active
    ws.title = f"Cotas {nivel}"
    
    # Estilos
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    total_fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
    total_font = Font(bold=True, size=11)
    
    # Título
    ws.merge_cells('A1:D1')
    ws['A1'] = f"COTAS CADASTRADAS - {nivel.upper()} - UTFPR"
    ws['A1'].font = Font(bold=True, size=14)
    ws['A1'].alignment = Alignment(horizontal='center')
    
    # Subtítulo
    ws.merge_cells('A2:D2')
    ws['A2'] = "Total de vagas disponíveis (independente de ocupação)"
    ws['A2'].font = Font(italic=True, size=10)
    ws['A2'].alignment = Alignment(horizontal='center')
    
    # Cabeçalho
    row = 4
    headers = ['#', 'Programa/Campus', 'CAPES DS', 'CAPES IES', 'Total']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=row, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal='center')
    
    # Ordenar programas
    programas_ordenados = sorted(dados.keys())
    
    # Dados por programa
    row = 5
    num = 1
    
    for programa in programas_ordenados:
        ws.cell(row=row, column=1, value=num)
        ws.cell(row=row, column=2, value=programa)
        
        capes_ds = dados[programa]['CAPES DS']
        capes_ies = dados[programa]['CAPES IES']
        total_prog = capes_ds + capes_ies
        
        ws.cell(row=row, column=3, value=capes_ds if capes_ds > 0 else '–')
        ws.cell(row=row, column=4, value=capes_ies if capes_ies > 0 else '–')
        ws.cell(row=row, column=5, value=total_prog)
        
        # Centralizar
        for col in [1, 3, 4, 5]:
            ws.cell(row=row, column=col).alignment = Alignment(horizontal='center')
        
        row += 1
        num += 1
    
    # Linha de totais
    row += 1
    ws.cell(row=row, column=2, value=f'TOTAL {nivel.upper()}')
    ws.cell(row=row, column=2).font = total_font
    
    ws.cell(row=row, column=3, value=totais['CAPES DS'])
    ws.cell(row=row, column=3).font = total_font
    ws.cell(row=row, column=3).fill = total_fill
    ws.cell(row=row, column=3).alignment = Alignment(horizontal='center')
    
    ws.cell(row=row, column=4, value=totais['CAPES IES'])
    ws.cell(row=row, column=4).font = total_font
    ws.cell(row=row, column=4).fill = total_fill
    ws.cell(row=row, column=4).alignment = Alignment(horizontal='center')
    
    total_geral = totais['CAPES DS'] + totais['CAPES IES']
    ws.cell(row=row, column=5, value=total_geral)
    ws.cell(row=row, column=5).font = Font(bold=True, size=12)
    ws.cell(row=row, column=5).fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    ws.cell(row=row, column=5).alignment = Alignment(horizontal='center')
    
    # Observações
    row += 2
    ws.cell(row=row, column=1, value="Observações:")
    ws.cell(row=row, column=1).font = Font(bold=True, size=10)
    
    row += 1
    ws.merge_cells(f'A{row}:E{row}')
    ws.cell(row=row, column=1, value="• CAPES DS: Cotas fixas da Demanda Social (Edital 14), atribuídas permanentemente aos programas")
    ws.cell(row=row, column=1).font = Font(italic=True, size=9)
    
    row += 1
    ws.merge_cells(f'A{row}:E{row}')
    ws.cell(row=row, column=1, value="• CAPES IES: Cotas rotativas da IES PROPPG (Edital 13), redistribuídas conforme demanda")
    ws.cell(row=row, column=1).font = Font(italic=True, size=9)
    
    row += 1
    ws.merge_cells(f'A{row}:E{row}')
    ws.cell(row=row, column=1, value=f"• Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}")
    ws.cell(row=row, column=1).font = Font(italic=True, size=9)
    
    # Ajustar larguras
    ws.column_dimensions['A'].width = 5
    ws.column_dimensions['B'].width = 40
    ws.column_dimensions['C'].width = 12
    ws.column_dimensions['D'].width = 12
    ws.column_dimensions['E'].width = 10
    
    # Salvar
    filename = f'relatorio_cotas_{nivel.lower()}.xlsx'
    wb.save(filename)
    print(f"✅ {filename} criado!")


if __name__ == '__main__':
    gerar_relatorio_cotas_totais()
