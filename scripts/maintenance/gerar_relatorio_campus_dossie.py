from reportlab.lib.pagesizes import A4
from reportlab.lead.units import cm
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
import io
from datetime import datetime
import matplotlib.pyplot as plt

def gerar_dossie_campus_pdf(campus_sigla):
    """
    Gera um dossiê PDF completo para um Campus específico.
    Inclui:
    1. Capa com Cabeçalho e Mapa (Estático/Simbólico)
    2. KPIs (Bolsistas, Financeiro)
    3. Gráficos de Distribuição
    4. Lista de Programas
    """
    from models import Campus, Bolsista, ProgramaAcademico, Modalidade
    from app import app, db # Usar contexto para query
    
    with app.app_context():
        # Dados
        campus = Campus.query.filter_by(sigla_campus=campus_sigla).first()
        if not campus:
            return None
            
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, 
                                rightMargin=2*cm, leftMargin=2*cm, 
                                topMargin=2*cm, bottomMargin=2*cm)
        
        elements = []
        styles = getSampleStyleSheet()
        
        # --- Estilos Personalizados ---
        style_title = ParagraphStyle('TitleCustom', parent=styles['Heading1'], alignment=TA_CENTER, fontSize=24, spaceAfter=20, textColor=colors.HexColor("#002c66"))
        style_subtitle = ParagraphStyle('SubtitleCustom', parent=styles['Heading2'], alignment=TA_CENTER, fontSize=16, spaceAfter=20, textColor=colors.HexColor("#666666"))
        style_kpi = ParagraphStyle('KPICustom', parent=styles['Normal'], alignment=TA_CENTER, fontSize=14, spaceAfter=10)
        
        # --- 1. Cabeçalho e Título ---
        # (Idealmente teria logotipo aqui)
        elements.append(Paragraph("UNIVERSIDADE TECNOLÓGICA FEDERAL DO PARANÁ", style_subtitle))
        elements.append(Paragraph(f"DOSSIÊ ESTRATÉGICO: CAMPUS {campus.nome.upper()}", style_title))
        elements.append(Spacer(1, 1*cm))
        
        elements.append(Spacer(1, 0.5*cm))

        # --- Mapa Estático ---
        try:
            from gerar_mapa_png import gerar_mapa_png
            map_buffer = gerar_mapa_png()
            img_map = Image(map_buffer, width=12*cm, height=9.6*cm) # Aspect ratio 10:8
            elements.append(img_map)
        except Exception as e:
            print(f"Erro ao gerar mapa: {e}")
            elements.append(Paragraph("[Mapa Indisponível]", styles['Normal']))

        elements.append(Spacer(1, 1*cm))
        
        # --- 2. KPIs em Tabela ---
        bolsistas_ativos = db.session.query(Bolsista).join(Bolsista.programa_link).filter(
            ProgramaAcademico.campus_id == campus.id,
            Bolsista.ativo == True
        ).all()
        
        total_bolsistas = len(bolsistas_ativos)
        
        total_investimento = 0
        for b in bolsistas_ativos:
            if b.modalidade:
                total_investimento += b.modalidade.valor_mensal
                
        investimento_anual_proj = total_investimento * 12
        
        data_kpis = [
            ['BOLSISTAS ATIVOS', 'INVESTIMENTO MENSAL', 'PREVISÃO ANUAL'],
            [str(total_bolsistas), f"R$ {total_investimento:,.2f}", f"R$ {investimento_anual_proj:,.2f}"]
        ]
        
        tbl_kpis = Table(data_kpis, colWidths=[5*cm, 6*cm, 6*cm])
        tbl_kpis.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f8f9fa")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#64748b")),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('FONTSIZE', (0,1), (-1,1), 16),
            ('FONTNAME', (0,1), (-1,1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0,1), (-1,1), colors.HexColor("#002c66")),
            ('BOTTOMPADDING', (0,0), (-1,-1), 12),
            ('TOPPADDING', (0,0), (-1,-1), 12),
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#e2e8f0"))
        ]))
        elements.append(tbl_kpis)
        elements.append(Spacer(1, 1*cm))
        
        # --- 3. Lista de Programas ---
        elements.append(Paragraph("Programas de Pós-Graduação Ofertados", styles['Heading2']))
        
        programas = ProgramaAcademico.query.filter_by(campus_id=campus.id).order_by(ProgramaAcademico.nome_programa).all()
        data_progs = [['Sigla', 'Nome do Programa', 'Nível']]
        
        for p in programas:
            data_progs.append([p.sigla_programa, p.nome_programa, p.niveis])
            
        tbl_progs = Table(data_progs, colWidths=[3*cm, 10*cm, 4*cm])
        tbl_progs.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#002c66")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#f1f5f9"), colors.white]),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey)
        ]))
        elements.append(tbl_progs)
        elements.append(Spacer(1, 1*cm))
        
        # --- 4. Gráfico de Barras (Modalidades) ---
        # Gerar gráfico em memória
        fig, ax = plt.subplots(figsize=(6, 3))
        
        # Contar modalidades
        from collections import Counter
        mods = [b.modalidade.nome for b in bolsistas_ativos if b.modalidade]
        counts = Counter(mods)
        
        if counts:
            ax.barh(list(counts.keys()), list(counts.values()), color='#002c66')
            ax.set_title("Distribuição por Modalidade")
            plt.tight_layout()
            
            img_buf = io.BytesIO()
            plt.savefig(img_buf, format='png', dpi=100)
            img_buf.seek(0)
            
            img = Image(img_buf, width=16*cm, height=8*cm)
            elements.append(img)
            plt.close()
        else:
             elements.append(Paragraph("Sem dados de modalidades para exibir.", styles['Normal']))

        # --- Footer ---
        elements.append(Spacer(1, 1*cm))
        elements.append(Paragraph(f"Relatório gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 
                                  ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey)))


        doc.build(elements)
        buffer.seek(0)
        return buffer
