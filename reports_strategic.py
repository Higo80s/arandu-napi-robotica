
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from datetime import datetime
from decimal import Decimal
import matplotlib
matplotlib.use('Agg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

# --- HELPER: CHART GENERATION (ENHANCED) ---
def generate_chart_img(type, data, labels, title, color_palette=None):
    fig = Figure(figsize=(7, 4))
    ax = fig.add_subplot(111)
    
    # Advanced Palette (Rainbow/Modern)
    if not color_palette:
        # Purple to Blue to Green gradient-ish
        color_palette = ['#8b5cf6', '#6366f1', '#3b82f6', '#0ea5e9', '#10b981', '#f59e0b', '#ef4444']
    
    # Cycle colors
    colors_cycle = color_palette * (len(data) // len(color_palette) + 1)
    
    if type == 'donut':
        wedges, texts, autotexts = ax.pie(data, labels=labels, autopct='%1.1f%%', startangle=90, pctdistance=0.85, colors=colors_cycle)
        centre_circle = matplotlib.patches.Circle((0,0),0.70,fc='white')
        ax.add_artist(centre_circle)
        for t in texts: t.set_fontsize(8)
        for t in autotexts: t.set_fontsize(8); t.set_color('white'); t.set_weight('bold')
        
    elif type == 'barh':
        # Horizontal Bars for readability
        y_pos = range(len(labels))
        bars = ax.barh(y_pos, data, color=colors_cycle[:len(data)])
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels)
        ax.invert_yaxis()
        
        # Clean look
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.xaxis.grid(True, linestyle='--', alpha=0.5)
        
        # Annotate
        for bar in bars:
            width = bar.get_width()
            ax.annotate(f'{int(width)}', 
                       xy=(width, bar.get_y() + bar.get_height() / 2),
                       xytext=(5, 0), textcoords="offset points",
                       ha='left', va='center', fontsize=9, fontweight='bold', color='#4b5563')
                       
    elif type == 'line':
        ax.plot(labels, data, marker='o', color='#8b5cf6', linewidth=2, markersize=6)
        ax.fill_between(labels, data, color='#8b5cf6', alpha=0.1)
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        for i, v in enumerate(data):
            ax.annotate(str(v), xy=(i, v), xytext=(0, 5), textcoords='offset points', ha='center')

    ax.set_title(title, fontsize=12, pad=30, fontweight='bold', color='#1f2937')
    fig.tight_layout()
    
    img_buffer = io.BytesIO()
    FigureCanvas(fig).print_png(img_buffer)
    img_buffer.seek(0)
    return img_buffer

# --- HEADER FUNCTION ---
def add_header_footer(canvas, doc):
    canvas.saveState()
    # Logo / Title Area
    canvas.setFillColor(colors.HexColor("#1e293b"))
    canvas.rect(0, 800, 595, 42, fill=1, stroke=0) # Top Bar
    
    canvas.setFillColor(colors.white)
    canvas.setFont('Helvetica-Bold', 14)
    canvas.drawString(30, 815, "Relatório de Gestão - NAPI-Robótica")
    canvas.setFont('Helvetica', 9)
    # [UPDATED] System Name: Arandú Napi-Robótica
    canvas.drawString(30, 805, "Sistema Arandú Napi-Robótica")
    
    canvas.drawRightString(565, 815, "NAPI-Robótica / FUNTEF")
    
    # Footer
    canvas.setFillColor(colors.black)
    canvas.setStrokeColor(colors.lightgrey)
    canvas.line(30, 40, 565, 40)
    canvas.setFont('Helvetica', 8)
    # [UPDATED] Date/Time + Responsible
    canvas.drawString(30, 25, f"Emissão: {datetime.now().strftime('%d/%m/%Y às %H:%M')} | Responsável: Administrador")
    canvas.drawRightString(565, 25, f"Página {doc.page}")
    
    canvas.restoreState()

# --- EXCEL REPORT ---
def gerar_excel_residentes(residentes):
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Lista Geral Residentes"

    headers = [
        "Nome", "CPF", "Campus", "Programa", 
        "Projeto de Pesquisa", "Supervisor", 
        "Início Vigência", "Fim Vigência", "Duração (Meses)", 
        "Bolsista?", "Agência", "Valor Adicional", "Qtd Adicional"
    ]
    ws.append(headers)
    
    for r in residentes:
        campus = "N/A"
        programa = "N/A"
        if r.programa_link:
            programa = r.programa_link.nome_programa
            if r.programa_link.campus:
                campus = r.programa_link.campus.sigla_campus


        row = [
            r.nome,
            r.cpf,
            campus,
            programa,
            r.projeto_pesquisa or "-",
            r.supervisor or "-",
            r.data_inicio.strftime('%d/%m/%Y') if r.data_inicio else "-",
            r.data_fim.strftime('%d/%m/%Y') if r.data_fim else "-",
            r.meses_duracao,
            "SIM" if r.recebe_bolsa else "NÃO",
            r.agencia_fomento or "N/A",
            f"R$ {r.valor_adicional:.2f}" if getattr(r, 'tem_adicional', False) else "-",
            r.qtd_adicional if getattr(r, 'tem_adicional', False) else "-"
        ]
        ws.append(row)

    # Auto-adjust column width
    for column_cells in ws.columns:
        # Check if cell.value is not None before converting to string
        length = max((len(str(cell.value)) if cell.value is not None else 0) for cell in column_cells)
        ws.column_dimensions[column_cells[0].column_letter].width = min(length + 2, 50) # Cap width


    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output

# --- PDF STRATEGIC REPORT ---
def gerar_pdf_estrategico(residentes):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=60, bottomMargin=50) # Adjusted margins for header
    
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    
    style_section = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#8b5cf6'), # Purple Theme
        spaceBefore=20,
        spaceAfter=10,
        borderPadding=5,
        borderColor=colors.HexColor('#e5e7eb'),
        borderWidth=0,
        borderBottomWidth=1
    )
    
    style_kpi = ParagraphStyle(
        'KPI',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#374151'),
        alignment=TA_CENTER,
        leading=14
    )
    
    style_insight = ParagraphStyle(
        'Insight',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#047857'), # Green
        backColor=colors.HexColor('#ecfdf5'),
        borderColor=colors.HexColor('#10b981'),
        borderWidth=1,
        borderPadding=10,
        borderRadius=5,
        spaceBefore=10,
        spaceAfter=15,
        alignment=TA_JUSTIFY
    )
    
    style_warning = ParagraphStyle(
        'Warning',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#b91c1c'), # Red
        backColor=colors.HexColor('#fef2f2'),
        borderColor=colors.HexColor('#f87171'),
        borderWidth=1,
        borderPadding=8,
        borderRadius=5,
        spaceBefore=5,
        spaceAfter=10,
        alignment=TA_JUSTIFY
    )
    
    # --- DATA PROCESSING ---
    total = len(residentes)
    
    if total == 0:
        elements.append(Paragraph("Nenhum residente cadastrado para análise.", styles['Normal']))
        doc.build(elements, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
        buffer.seek(0)
        return buffer

    # Metrics
    bolsistas_count = sum(1 for r in residentes if r.recebe_bolsa)
    voluntarios_count = total - bolsistas_count
    
    campus_dist = {}
    prog_dist = {}
    year_dist = {}
    invest_total_mensal = Decimal('0')
    
    undefined_campus_count = 0
    undefined_prog_count = 0
    
    for r in residentes:
        # Campus
        c_name = "Indefinido"
        if r.programa_link and r.programa_link.campus:
            c_name = r.programa_link.campus.sigla_campus
        
        # [UPDATED] Logic to separate Undefined
        if c_name == "Indefinido":
            undefined_campus_count += 1
        else:
            campus_dist[c_name] = campus_dist.get(c_name, 0) + 1
        
        # Program
        p_name = r.programa_link.nome_programa if r.programa_link else "N/I"
        
        if p_name == "N/I":
            undefined_prog_count += 1
        else:
            prog_dist[p_name] = prog_dist.get(p_name, 0) + 1
        
        # Year
        if r.data_inicio:
            y = r.data_inicio.year
            if y > 2010: # Reasonable filter
                year_dist[y] = year_dist.get(y, 0) + 1
                
        # Investment (Est.)
        if r.recebe_bolsa:
            if r.valor_bolsa:
                 invest_total_mensal += r.valor_bolsa
            elif r.modalidade:
                 invest_total_mensal += r.modalidade.valor_mensal
                 
    # Sorts
    sorted_campus = sorted(campus_dist.items(), key=lambda x: x[1], reverse=True)
    sorted_prog = sorted(prog_dist.items(), key=lambda x: x[1], reverse=True)
    sorted_year = sorted(year_dist.items())

    # --- DOCUMENT STRUCTURE ---
    
    # 1. Executive Summary
    elements.append(Paragraph("Resumo Executivo", style_section))
    
    summary_text = f"""
    O presente relatório analisa a distribuição e impacto dos <b>{total}</b> residentes pós-doutorais ativos. 
    Observa-se que <b>{(bolsistas_count/total)*100:.1f}%</b> ({bolsistas_count}) recebem fomento financeiro, 
    representando um investimento mensal estimado de <b>R$ {invest_total_mensal:,.2f}</b>.
    """
    elements.append(Paragraph(summary_text.replace('\n', ' '), styles['Normal']))
    
    # Data Quality Warning (Action Item)
    if undefined_campus_count > 0 or undefined_prog_count > 0:
        warning_text = f"""
        <b>Atenção - Qualidade de Dados (Ação Necessária):</b> Identificamos <b>{undefined_campus_count}</b> registro(s) sem campus definido 
        e <b>{undefined_prog_count}</b> registro(s) sem vínculo com programa de pós-graduação. 
        Recomenda-se a revisão manual destes cadastros."
        """
        elements.append(Paragraph(warning_text, style_warning))

    # Insight Automático
    top_campus = sorted_campus[0] if sorted_campus else ("N/A", 0)
    top_prog = sorted_prog[0] if sorted_prog else ("N/A", 0)
    
    # Calc valid stats base
    valid_base = total - undefined_campus_count if (total - undefined_campus_count) > 0 else 1
    
    insight_text = f"""
    <b>Insight de Distribuição (Considerando dados válidos):</b> O campus <b>{top_campus[0]}</b> lidera a concentração de pesquisadores, 
    abrigando {top_campus[1]} residentes ({(top_campus[1]/valid_base)*100:.0f}% dos válidos). 
    No âmbito acadêmico, o programa <b>{top_prog[0]}</b> destaca-se como o principal polo de atração.
    """
    elements.append(Paragraph(insight_text, style_insight))
    
    # 2. Charts Row 1 (Profile & Trend)
    elements.append(Spacer(1, 10))
    
    # Generate Images
    img_profile = generate_chart_img('donut', [bolsistas_count, voluntarios_count], ['Bolsistas', 'Voluntários'], "Perfil de Financiamento")
    
    years = [str(k) for k,v in sorted_year]
    y_vals = [v for k,v in sorted_year]
    img_trend = generate_chart_img('line', y_vals, years, "Evolução de Ingressos (Anual)")
    
    # Table for Layout (Side by Side)
    data_table = [[Image(img_profile, width=250, height=150), Image(img_trend, width=250, height=150)]]
    t = Table(data_table, colWidths=[260, 260])
    t.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'TOP')]))
    elements.append(t)
    
    elements.append(Spacer(1, 20))
    
    # 3. Geographic Distribution
    elements.append(Paragraph("Distribuição Geográfica (Campus)", style_section))
    
    c_labels = [x[0] for x in sorted_campus]
    c_values = [x[1] for x in sorted_campus]
    
    if len(c_labels) > 8: # If too many, show top 8
        c_labels = c_labels[:8]
        c_values = c_values[:8]
        
    if c_labels:
        img_campus = generate_chart_img('barh', c_values, c_labels, "Residentes por Campus (Válidos)")
        elements.append(Image(img_campus, width=500, height=280))
    else:
        elements.append(Paragraph("Sem dados de campus válidos para exibição.", styles['Normal']))
    
    elements.append(Spacer(1, 10))
    elements.append(PageBreak())
    
    # 4. Program Analysis
    elements.append(Paragraph("Análise por Programa de Pós-Graduação", style_section))
    
    p_labels = [x[0][:40]+"..." if len(x[0])>40 else x[0] for x in sorted_prog[:10]] # Top 10, truncate names
    p_values = [x[1] for x in sorted_prog[:10]]
    
    if p_labels:
        img_prog = generate_chart_img('barh', p_values, p_labels, "Top 10 Programas (Válidos)")
        elements.append(Image(img_prog, width=500, height=350))
    else:
        elements.append(Paragraph("Sem dados de programas válidos para exibição.", styles['Normal']))
    
    # 5. Detailed List (Table) - Optional, simplified for strategic report
    elements.append(Paragraph("Destaques Recentes", style_section))
    elements.append(Paragraph("Últimos 5 residentes cadastrados:", styles['Normal']))
    elements.append(Spacer(1, 5))
    
    # Recent Residents Table
    # Sort by ID desc or Date Start desc
    recent = sorted(residentes, key=lambda x: x.data_inicio or datetime.min.date(), reverse=True)[:5]
    
    table_data = [['Nome', 'Programa', 'Início', 'Bolsa', 'Valor', 'Parc.']]
    for r in recent:
        p_name = r.programa_link.sigla_programa if r.programa_link else "-"
        inicio = r.data_inicio.strftime("%m/%Y") if r.data_inicio else "-"
        bolsa = "Sim" if r.recebe_bolsa else "Não"
        
        # [NEW] Optional Fields
        valor = f"R$ {r.valor_bolsa:,.2f}" if r.valor_bolsa else "-"
        # Try to find duration/parcels. 'meses_duracao' is usually total months.
        parc = f"{r.meses_duracao}x" if r.meses_duracao else "-"
        
        table_data.append([r.nome[:30], p_name, inicio, bolsa, valor, parc])
        
    t_recent = Table(table_data, colWidths=[160, 80, 60, 40, 60, 40])

    t_recent.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e2e8f0')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#1f2937')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#d1d5db')),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('ALIGN', (2,1), (-1,-1), 'CENTER'),
    ]))
    elements.append(t_recent)
    
    # Footer Note
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Relatório gerado automaticamente pelo Sistema Arandú Napi-Robótica.", styles['Italic']))

    doc.build(elements, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
    buffer.seek(0)
    return buffer
