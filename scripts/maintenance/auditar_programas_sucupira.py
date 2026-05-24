"""
Auditoria: Programas no Banco vs Plataforma Sucupira
Gera relatório PDF com discrepâncias e propostas de ajuste
"""

from app import app, db
from models import ProgramaAcademico, Campus
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime

# Dados da Plataforma Sucupira (fornecidos pelo usuário)
SUCUPIRA_DATA = [
    {"codigo": "40006018179P5", "nome": "Engenharia Química", "sigla": "PPGEQ", "campus": "AP", "niveis": "M", "nota": "3", "ano": 2019},
    {"codigo": "40006018183P2", "nome": "Textil e Moda", "sigla": "PPGTM", "campus": "AP", "niveis": "M", "nota": "A", "ano": 2023},
    {"codigo": "40006018182P6", "nome": "Ciência da Computação", "sigla": "PPGCC", "campus": "CM", "niveis": "M", "nota": "A", "ano": 2021},
    {"codigo": "33283010001P5", "nome": "Ensino de Física - PROFIS (Polo)", "sigla": "PROFIS", "campus": "CM", "niveis": "MP", "nota": "5", "ano": 2014},
    {"codigo": "40006018170P8", "nome": "INOVAÇÕES TECNOLÓGICAS", "sigla": "PPGIT", "campus": "CM", "niveis": "MP", "nota": "3", "ano": 2016},
    {"codigo": "33004013069P2", "nome": "Regulamentação de Recursos Hídricos (Polo)", "sigla": "PROFÁGUA", "campus": "CM", "niveis": "MP", "nota": "4", "ano": 2018},
    {"codigo": "40006018037P6", "nome": "BIOINFORMÁTICA", "sigla": "PPGBIOINFO", "campus": "CP", "niveis": "M", "nota": "4", "ano": 2015},
    {"codigo": "40001016175P8", "nome": "Bioinformática (Associação com UFPR)", "sigla": "PPGAB", "campus": "CP", "niveis": "D", "nota": "4", "ano": 2020},
    {"codigo": "40006018012P3", "nome": "Engenharia Elétrica", "sigla": "PPGEE", "campus": "CP", "niveis": "M", "nota": "4", "ano": 2010},
    {"codigo": "40002012171P9", "nome": "ENGENHARIA ELETRICA (Associação com UEL)", "sigla": "PPGAEE", "campus": "CP", "niveis": "D", "nota": "4", "ano": 2016},
    {"codigo": "40006018025P8", "nome": "Informática", "sigla": "PPGI", "campus": "CP", "niveis": "MP", "nota": "4", "ano": 2013},
    {"codigo": "31075010001P2", "nome": "Matemática em Rede Nacional (Polo)", "sigla": "PROFMAT", "campus": "CP", "niveis": "MP", "nota": "5", "ano": 2014},
    {"codigo": "40006018024P1", "nome": "Engenharia Mecânica", "sigla": "PPGEM", "campus": "CP/PG", "niveis": "M", "nota": "3", "ano": 2012},
    {"codigo": "40006018044P2", "nome": "ADMINISTRAÇÃO", "sigla": "PPGA", "campus": "CT", "niveis": "M", "nota": "3", "ano": 2016},
    {"codigo": "53045009001P3", "nome": "ADMINISTRAÇÃO PÚBLICA EM REDE NACIONAL (Polo)", "sigla": "PROFIAP", "campus": "CT", "niveis": "MP", "nota": "3", "ano": 2016},
    {"codigo": "40006018013P0", "nome": "CIÊNCIA E TECNOLOGIA AMBIENTAL", "sigla": "PPGCTA", "campus": "CT", "niveis": "M,D", "nota": "4", "ano": 2012},
    {"codigo": "40006018011P7", "nome": "Computação Aplicada", "sigla": "PPGCA", "campus": "CT", "niveis": "MP", "nota": "3", "ano": 2010},
    {"codigo": "40006018173P7", "nome": "Educação Física", "sigla": "PPGEF", "campus": "CT", "niveis": "M", "nota": "3", "ano": 2017},
    {"codigo": "40006018018P1", "nome": "Engenharia Biomédica", "sigla": "PPGEB", "campus": "CT", "niveis": "MP", "nota": "4", "ano": 2011},
    {"codigo": "40006018008P6", "nome": "ENGENHARIA CIVIL", "sigla": "PPGEC", "campus": "CT", "niveis": "M,D", "nota": "5", "ano": 2009},
    {"codigo": "40006018001P1", "nome": "ENGENHARIA ELÉTRICA E INFORMÁTICA INDUSTRIAL", "sigla": "CPGEI", "campus": "CT", "niveis": "M,D", "nota": "6", "ano": 1988},
    {"codigo": "40006018003P4", "nome": "ENGENHARIA MECÂNICA E DE MATERIAIS", "sigla": "PPGEM", "campus": "CT", "niveis": "M,D", "nota": "4", "ano": 2000},
    {"codigo": "40006018035P3", "nome": "ESTUDOS DE LINGUAGENS", "sigla": "PPGEL", "campus": "CT", "niveis": "M", "nota": "4", "ano": 2015},
    {"codigo": "40006018172P0", "nome": "FÍSICA E ASTRONOMIA", "sigla": "PPGFA", "campus": "CT", "niveis": "M", "nota": "3", "ano": 2016},
    {"codigo": "40006018019P8", "nome": "Formação Científica, Educacional e Tecnológica", "sigla": "PPGFCET", "campus": "CT", "niveis": "MP,DP", "nota": "4", "ano": 2011},
    {"codigo": "31075010001P2", "nome": "Matemática em Rede Nacional (Polo)", "sigla": "PROFMAT", "campus": "CT", "niveis": "MP", "nota": "5", "ano": 2011},
    {"codigo": "40006018017P5", "nome": "Planejamento e Governança Pública", "sigla": "PPGPGP", "campus": "CT", "niveis": "MP,DP", "nota": "4", "ano": 2011},
    {"codigo": "40006018032P4", "nome": "Química", "sigla": "PPGQ", "campus": "CT", "niveis": "M", "nota": "3", "ano": 2014},
    {"codigo": "40006018038P2", "nome": "SISTEMAS DE ENERGIA", "sigla": "PPGSE", "campus": "CT", "niveis": "MP", "nota": "4", "ano": 2015},
    {"codigo": "40006018181P0", "nome": "Sustentabilidade Ambiental Urbana", "sigla": "PPGSAU", "campus": "CT", "niveis": "D", "nota": "4", "ano": 2019},
    {"codigo": "40006018002P8", "nome": "TECNOLOGIA E SOCIEDADE", "sigla": "PPGTE", "campus": "CT", "niveis": "M,D", "nota": "5", "ano": 1995},
    {"codigo": "40006018043P6", "nome": "AGROECOSSISTEMAS", "sigla": "PPGSIS", "campus": "DV", "niveis": "M", "nota": "3", "ano": 2015},
    {"codigo": "40015017009P8", "nome": "Zootecnia (Associação Unioeste)", "sigla": "PPGZO", "campus": "DV", "niveis": "M,D", "nota": "4", "ano": 2011},
    {"codigo": "40006018174P3", "nome": "Engenharia Ambiental: Análise e Tecnologia Ambiental", "sigla": "PPGEA", "campus": "FB", "niveis": "M", "nota": "3", "ano": 2017},
    {"codigo": "40006018175P0", "nome": "CIÊNCIA E ENGENHARIA DE MATERIAIS", "sigla": "PPGCEM", "campus": "LD/AP", "niveis": "M", "nota": "4", "ano": 2016},
    {"codigo": "40006018023P5", "nome": "Engenharia Ambiental", "sigla": "PPGEA", "campus": "LD/AP", "niveis": "M", "nota": "4", "ano": 2012},
    {"codigo": "40006018027P0", "nome": "Ensino de Ciências Humanas, Sociais e da Natureza", "sigla": "PPGEN", "campus": "LD/CP", "niveis": "MP", "ano": 2013, "nota": "4"},
    {"codigo": "40006018041P3", "nome": "ENSINO DE MATEMÁTICA", "sigla": "PPGMAT", "campus": "LD/CP", "niveis": "MP", "nota": "4", "ano": 2015},
    {"codigo": "40006018015P2", "nome": "Tecnologia de Alimentos", "sigla": "PPGTAL", "campus": "LD/FB", "niveis": "MP", "nota": "4", "ano": 2011},
    {"codigo": "33283010001P5", "nome": "Ensino de Física - PROFIS (Polo)", "sigla": "PROFIS", "campus": "MD", "niveis": "MP", "nota": "5", "ano": 2015},
    {"codigo": "31102000001P6", "nome": "PROPRIEDADE INTELECTUAL E TRANSFERÊNCIA DE TECNOLOGIA PARA INOVAÇÃO", "sigla": "PROFNIT", "campus": "MD", "niveis": "MP", "nota": "4", "ano": 2023},
    {"codigo": "31001017169P2", "nome": "Química em Rede Nacional (Polo)", "sigla": "PROFQUI", "campus": "MD", "niveis": "MP", "nota": "4", "ano": 2016},
    {"codigo": "40006018026P4", "nome": "Tecnologias Ambientais", "sigla": "PPGTAMB", "campus": "MD", "niveis": "M", "nota": "4", "ano": 2013},
    {"codigo": "40006018034P7", "nome": "TECNOLOGIAS COMPUTACIONAIS PARA O AGRONEGÓCIO", "sigla": "PPGTCA", "campus": "MD", "niveis": "MP", "nota": "4", "ano": 2015},
    {"codigo": "40006018016P9", "nome": "Tecnologia de Alimentos", "sigla": "PPGTA", "campus": "MD/CM", "niveis": "M,D", "nota": "4", "ano": 2011},
    {"codigo": "40006018005P7", "nome": "AGRONOMIA", "sigla": "PPGAG", "campus": "PB", "niveis": "M,D", "nota": "4", "ano": 2007},
    {"codigo": "40006018010P0", "nome": "Desenvolvimento Regional", "sigla": "PPGDR", "campus": "PB", "niveis": "M,D", "nota": "5", "ano": 2010},
    {"codigo": "40006018030P1", "nome": "Engenharia Civil", "sigla": "PPGEC", "campus": "PB", "niveis": "M", "nota": "3", "ano": 2014},
    {"codigo": "40006018031P8", "nome": "Engenharia de Produção e Sistemas", "sigla": "PPGEPS", "campus": "PB", "niveis": "M", "nota": "3", "ano": 2014},
    {"codigo": "40006018009P2", "nome": "ENGENHARIA ELÉTRICA", "sigla": "PPGEE", "campus": "PB", "niveis": "M", "nota": "3", "ano": 2009},
    {"codigo": "40006018036P0", "nome": "LETRAS", "sigla": "PPGL", "campus": "PB", "niveis": "M", "nota": "4", "ano": 2015},
    {"codigo": "31075010001P2", "nome": "Matemática em Rede Nacional (Polo)", "sigla": "PROFMAT", "campus": "PB", "niveis": "MP", "nota": "5", "ano": 2012},
    {"codigo": "40006018020P6", "nome": "Tecnologia de Processos Químicos e Bioquímicos", "sigla": "PPGTP", "campus": "PB", "niveis": "M", "nota": "3", "ano": 2011},
    {"codigo": "40006018171P4", "nome": "CIÊNCIA DA COMPUTAÇÃO", "sigla": "PPGCC", "campus": "PG", "niveis": "M", "nota": "3", "ano": 2016},
    {"codigo": "40006018004P0", "nome": "ENGENHARIA DE PRODUÇÃO", "sigla": "PPGEP", "campus": "PG", "niveis": "M,D", "nota": "5", "ano": 2004},
    {"codigo": "40006018022P9", "nome": "Engenharia Elétrica", "sigla": "PPGEE", "campus": "PG", "niveis": "M", "nota": "4", "ano": 2012},
    {"codigo": "40006018177P2", "nome": "ENGENHARIA QUÍMICA", "sigla": "PPGEQ", "campus": "PG", "niveis": "M", "nota": "3", "ano": 2017},
    {"codigo": "40006018006P3", "nome": "ENSINO DE CIÊNCIA E TECNOLOGIA", "sigla": "PPGECT", "campus": "PG", "niveis": "MP,D", "nota": "5", "ano": 2008},
    {"codigo": "40006018176P6", "nome": "BIOTECNOLOGIA", "sigla": "PPGBIOTEC", "campus": "PG/DV", "niveis": "M,D", "nota": "4", "ano": 2017},
    {"codigo": "40006018178P9", "nome": "Recursos Naturais e Sustentabilidade", "sigla": "PPGRNS", "campus": "SH", "niveis": "M", "nota": "3", "ano": 2019},
    {"codigo": "31075010001P2", "nome": "Matemática em Rede Nacional (Polo)", "sigla": "PROFMAT", "campus": "TD", "niveis": "MP", "nota": "5", "ano": 2018},
    {"codigo": "40006018033P0", "nome": "PROCESSOS QUÍMICOS E BIOTECNOLÓGICOS", "sigla": "PPGQB", "campus": "TD", "niveis": "M", "nota": "3", "ano": 2015},
    {"codigo": "40006018180P3", "nome": "Tecnologia Biociências", "sigla": "PPGBIO", "campus": "TD", "niveis": "MP", "nota": "3", "ano": 2019},
]

def gerar_relatorio_auditoria():
    with app.app_context():
        # Buscar programas do banco
        programas_db = ProgramaAcademico.query.all()
        campus_db = {c.sigla_campus: c for c in Campus.query.all()}
        
        # Criar dicionários para comparação
        db_dict = {p.codigo_programa: p for p in programas_db if p.codigo_programa}
        sucupira_dict = {s['codigo']: s for s in SUCUPIRA_DATA}
        
        # Análises
        faltantes = []  # No Sucupira mas não no BD
        excedentes = []  # No BD mas não no Sucupira
        divergencias = []  # Dados diferentes
        
        # 1. Verificar faltantes (Sucupira → BD)
        for codigo, suc in sucupira_dict.items():
            if codigo not in db_dict:
                faltantes.append(suc)
        
        # 2. Verificar excedentes (BD → Sucupira)
        for codigo, prog in db_dict.items():
            if codigo not in sucupira_dict:
                excedentes.append(prog)
        
        # 3. Verificar divergências
        for codigo in set(db_dict.keys()) & set(sucupira_dict.keys()):
            prog = db_dict[codigo]
            suc = sucupira_dict[codigo]
            
            diffs = []
            
            # Comparar nome
            if prog.nome_programa.upper().strip() != suc['nome'].upper().strip():
                diffs.append(f"Nome: '{prog.nome_programa}' vs '{suc['nome']}'")
            
            # Comparar sigla
            if prog.sigla_programa.upper() != suc['sigla'].upper():
                diffs.append(f"Sigla: '{prog.sigla_programa}' vs '{suc['sigla']}'")
            
            # Comparar campus
            campus_db_sigla = prog.campus.sigla_campus if prog.campus else "N/I"
            if campus_db_sigla != suc['campus']:
                diffs.append(f"Campus: '{campus_db_sigla}' vs '{suc['campus']}'")
            
            # Comparar níveis
            prog_niveis = prog.niveis or "N/I"
            if prog_niveis != suc['niveis']:
                diffs.append(f"Níveis: '{prog_niveis}' vs '{suc['niveis']}'")
            
            # Comparar nota
            prog_nota = str(prog.nota_capes) if prog.nota_capes else "N/I"
            suc_nota = str(suc['nota'])
            if prog_nota != suc_nota:
                diffs.append(f"Nota: '{prog_nota}' vs '{suc_nota}'")
            
            if diffs:
                divergencias.append({
                    'codigo': codigo,
                    'programa': prog,
                    'sucupira': suc,
                    'diferencas': diffs
                })
        
        # GERAR PDF
        filename = f"auditoria_programas_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        doc = SimpleDocTemplate(filename, pagesize=A4, leftMargin=1.5*cm, rightMargin=1.5*cm)
        
        story = []
        styles = getSampleStyleSheet()
        
        # Título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#003366'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        story.append(Paragraph("RELATÓRIO DE AUDITORIA DE PROGRAMAS", title_style))
        story.append(Paragraph(f"Banco de Dados vs Plataforma Sucupira - {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        story.append(Spacer(1, 0.5*cm))
        
        # Resumo
        summary_data = [
            ['INDICADOR', 'QUANTIDADE'],
            ['Programas na Sucupira', len(SUCUPIRA_DATA)],
            ['Programas no Banco', len([p for p in programas_db if p.codigo_programa])],
            ['Faltantes no BD', len(faltantes)],
            ['Excedentes no BD', len(excedentes)],
            ['Com Divergências', len(divergencias)],
        ]
        
        summary_table = Table(summary_data, colWidths=[12*cm, 4*cm])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(PageBreak())
        
        # 1. FALTANTES
        if faltantes:
            story.append(Paragraph(f"1. PROGRAMAS FALTANTES NO BANCO ({len(faltantes)})", styles['Heading2']))
            story.append(Paragraph("Estão na Sucupira mas não foram encontrados no banco de dados:", styles['Normal']))
            story.append(Spacer(1, 0.3*cm))
            
            for prog in faltantes:
                story.append(Paragraph(f"<b>• Código:</b> {prog['codigo']}", styles['Normal']))
                story.append(Paragraph(f"  Nome: {prog['nome']}", styles['Normal']))
                story.append(Paragraph(f"  Sigla: {prog['sigla']} | Campus: {prog['campus']} | Níveis: {prog['niveis']}", styles['Normal']))
                story.append(Spacer(1, 0.2*cm))
            
            story.append(PageBreak())
        
        # 2. EXCEDENTES
        if excedentes:
            story.append(Paragraph(f"2. PROGRAMAS EXCEDENTES NO BANCO ({len(excedentes)})", styles['Heading2']))
            story.append(Paragraph("Estão no banco mas não foram encontrados na Sucupira (podem ser desatualizados):", styles['Normal']))
            story.append(Spacer(1, 0.3*cm))
            
            for prog in excedentes:
                story.append(Paragraph(f"<b>• Código:</b> {prog.codigo_programa}", styles['Normal']))
                story.append(Paragraph(f"  Nome: {prog.nome_programa}", styles['Normal']))
                story.append(Paragraph(f"  Sigla: {prog.sigla_programa} | Campus: {prog.campus.sigla_campus if prog.campus else 'N/I'}", styles['Normal']))
                story.append(Spacer(1, 0.2*cm))
            
            story.append(PageBreak())
        
        # 3. DIVERGÊNCIAS
        if divergencias:
            story.append(Paragraph(f"3. PROGRAMAS COM DIVERGÊNCIAS ({len(divergencias)})", styles['Heading2']))
            story.append(Paragraph("Programas encontrados em ambos mas com dados diferentes:", styles['Normal']))
            story.append(Spacer(1, 0.3*cm))
            
            for div in divergencias:
                story.append(Paragraph(f"<b>• Código:</b> {div['codigo']} - {div['sucupira']['sigla']}", styles['Heading3']))
                for diff in div['diferencas']:
                    story.append(Paragraph(f"  ⚠ {diff}", styles['Normal']))
                story.append(Spacer(1, 0.3*cm))
        
        # PROPOSTAS
        story.append(PageBreak())
        story.append(Paragraph("4. PROPOSTAS DE AJUSTE", styles['Heading2']))
        
        if faltantes:
            story.append(Paragraph(f"<b>4.1 Adicionar {len(faltantes)} programas faltantes</b>", styles['Heading3']))
            story.append(Paragraph("Script SQL para inserção dos programas na tabela programa_academico.", styles['Normal']))
        
        if divergencias:
            story.append(Paragraph(f"<b>4.2 Atualizar {len(divergencias)} programas com divergências</b>", styles['Heading3']))
            story.append(Paragraph("Corrigir nomes, siglas, campus e níveis conforme Sucupira.", styles['Normal']))
        
        if excedentes:
            story.append(Paragraph(f"<b>4.3 Revisar {len(excedentes)} programas excedentes</b>", styles['Heading3']))
            story.append(Paragraph("Verificar se são programas descontinuados ou erros de cadastro.", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        
        print(f"\n✅ Relatório gerado: {filename}")
        print(f"\nRESUMO:")
        print(f"  Sucupira: {len(SUCUPIRA_DATA)} programas")
        print(f"  Banco:    {len([p for p in programas_db if p.codigo_programa])} programas")
        print(f"  Faltantes: {len(faltantes)}")
        print(f"  Excedentes: {len(excedentes)}")
        print(f"  Divergências: {len(divergencias)}")
        
        return filename

if __name__ == "__main__":
    gerar_relatorio_auditoria()
