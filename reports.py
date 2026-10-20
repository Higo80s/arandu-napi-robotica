import io
import csv
from flask import send_file
from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from models import Bolsista, Modalidade, Edital
from utils import calcular_parcelas
from services.financeiro_service import VencimentoFactory
from datetime import datetime
from decimal import Decimal

def gerar_relatorio_excel(mes_referencia_str):
    # mes_referencia_str format: YYYY-MM — mesma linha do log individual (PagamentoBolsistaService)
    from services.pagamento_bolsista_service import PagamentoBolsistaService, PAGAMENTO_HEADERS

    wb = Workbook()
    ws = wb.active
    ws.title = "Pagamento Bolsas"
    ws.append(PAGAMENTO_HEADERS)

    bolsistas = Bolsista.query.filter_by(ativo=True).all()
    bolsistas.sort(key=lambda b: (
        (Edital.query.get(b.edital_id).numero if b.edital_id else ""),
        b.nome or ""
    ))

    for b in bolsistas:
        row = PagamentoBolsistaService.build_row(b, mes_referencia_str)
        if not row:
            continue
        ws.append([
            row['edital'], row['sei'], row['cpf'], row['nome'], row['email'],
            row['orientador'], row['instituicao'], row['banco'], row['agencia'],
            row['conta'], row['tipo'], row['nivel'], row['valor'], row['inicio_bolsa'],
            row['referencia'], row['vencimento'], row['parcela_atual'], row['total_parcelas'],
        ])

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output


def gerar_relatorio_pdf(mes_referencia_str):
    buffer = io.BytesIO()
    # Use A4 Landscape (Standard in Brazil) - Width ~842 pts
    from reportlab.lib.pagesizes import landscape, A4
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=30, leftMargin=30, topMargin=40, bottomMargin=30)
    elements = []
    
    styles = getSampleStyleSheet()
    from reportlab.lib.styles import ParagraphStyle
    title_style = styles['Title']
    title_style.fontSize = 16
    title_style.textColor = colors.HexColor("#0056b3") # UTFPR Blue
    
    cell_style = ParagraphStyle(
        'CellNormal',
        parent=styles['Normal'],
        fontSize=8,
        leading=10
    )
    
    elements.append(Paragraph(f"Relatório de Pagamento de Bolsas - {mes_referencia_str}", title_style))
    elements.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 20))

    # Headers and Data
    # Columns: Edital, Nome, Nível, CPF, Instituição, Banco, Agência, Conta, Valor, Parcela
    headers = ["Edital", "Nome", "Nível", "CPF", "Instituição", "Banco", "Agência", "Conta", "Valor", "Parcela"]
    
    data = [headers]
    
    ref_date = datetime.strptime(mes_referencia_str + '-01', '%Y-%m-%d').date()
    # [UPDATED] User requested ALL bolsistas, not just active/paying ones
    bolsistas = Bolsista.query.all()
    
    total_valor = Decimal('0')
    rows_to_sort = []

    for b in bolsistas:
        mod = Modalidade.query.get(b.modalidade_id)
        edital = Edital.query.get(b.edital_id)
        
        if not mod or not edital: continue

        parcela = calcular_parcelas(b.data_inicio_bolsa, ref_date)
        
        val_base = mod.valor_mensal
        val_final = Decimal('0')
        parcela_str = "-"
        
        is_paying = False
        
        if b.ativo:
            if 0 < parcela <= b.meses_duracao:
                is_paying = True
                val_final = val_base
                if getattr(b, 'tem_adicional', False):
                     val_final += b.valor_adicional
                parcela_str = f"{parcela}/{b.meses_duracao}"
            elif parcela <= 0:
                parcela_str = "A Iniciar"
            else:
                parcela_str = "Vigência Encerrada"
        else:
            parcela_str = "Inativo"

        if is_paying:
            total_valor += val_final
            
        if is_paying:
            val_str = f"R$ {val_final:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        else:
            val_str = "-"

        nome_display = b.nome
        if not b.ativo:
            nome_display += " (INATIVO)"
            
        banco_display = b.banco or "-"
        edital_num_str = str(edital.numero)
        nivel_str = mod.nivel if mod else "-"
        
        rows_to_sort.append({
            'edital': edital_num_str,
            'nome': b.nome or "",
            'nivel': nivel_str,
            'row': [
                Paragraph(edital_num_str, cell_style),
                Paragraph(nome_display, cell_style),
                Paragraph(nivel_str, cell_style),
                Paragraph(b.cpf or "-", cell_style),
                Paragraph(b.instituicao or b.sigla_campus_display or "-", cell_style),
                Paragraph(banco_display, cell_style),
                b.agencia or "-",
                b.conta or "-",
                val_str,
                parcela_str
            ]
        })

    # [NEW] Include Residents
    from models import Residente
    residentes = Residente.query.all()
    
    for r in residentes:
        val_res = Decimal('0')
        if r.valor_bolsa:
            val_res = r.valor_bolsa
        elif r.recebe_bolsa and r.modalidade:
            val_res = r.modalidade.valor_mensal
            if getattr(r, 'tem_adicional', False):
                val_res += r.valor_adicional
        
        if val_res <= 0: continue
        if not r.ativo: continue 
        if not r.data_inicio: continue
        
        start = r.data_inicio
        diff = (ref_date.year - start.year) * 12 + (ref_date.month - start.month) + 1
        parcela_r = diff
        
        if 0 < parcela_r <= r.meses_duracao:
             val_str_r = f"R$ {val_res:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
             parcela_str_r = f"{parcela_r}/{r.meses_duracao}"
             ed_num = r.edital.numero if r.edital else "N/I"
             
             total_valor += val_res
             edital_disp = f"{ed_num} (Res)"
             nivel_res_str = r.modalidade.nivel if r.modalidade else "Pós-Doc"
             
             nome_display_r = r.nome
             banco_display_r = r.banco or "-"
             
             rows_to_sort.append({
                 'edital': edital_disp,
                 'nome': r.nome or "",
                 'nivel': nivel_res_str,
                 'row': [
                     Paragraph(edital_disp, cell_style),
                     Paragraph(nome_display_r, cell_style),
                     Paragraph(nivel_res_str, cell_style),
                     Paragraph(r.cpf or "-", cell_style),
                     Paragraph(r.instituicao or (r.programa_link.campus.sigla_campus if r.programa_link else "-"), cell_style),
                     Paragraph(banco_display_r, cell_style),
                     r.agencia or "-",
                     r.conta or "-",
                     val_str_r,
                     parcela_str_r
                 ]
             })

    # Organize/Sort the rows: first by Level (alphabetical), then by Name (alphabetical), and finally by Edital (alphabetical)
    rows_to_sort.sort(key=lambda x: (x['nivel'].lower(), x['nome'].lower(), x['edital'].lower()))

    # Build the final data table
    for item in rows_to_sort:
        data.append(item['row'])

    # Column Widths (Total ~780pts)
    col_widths = [70, 130, 70, 80, 80, 65, 45, 55, 95, 90]

    t = Table(data, colWidths=col_widths, repeatRows=1)
    
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0056b3")), 
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (1, 1), (-1, -1), [colors.white, colors.HexColor("#f1f5f9")]),
        ('FONTSIZE', (0, 1), (-1, -1), 8), # Reduced font size for better fit
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    elements.append(t)
    
    # Signature fields for NAPI
    elements.append(Spacer(1, 40))
    sig_data = [
        ["_________________________________", "_________________________________"],
        ["Coordenação NAPI-Robótica", "Visto Financeiro FUNTEF"]
    ]
    sig_table = Table(sig_data, colWidths=[390, 390])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))
    elements.append(sig_table)

    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"<b>Total Geral da Folha: R$ {total_valor:,.2f}</b>".replace(",", "X").replace(".", ",").replace("X", "."), styles['Normal']))

    doc.build(elements)
    buffer.seek(0)
    return buffer

import matplotlib
matplotlib.use('Agg') # Non-interactive backend
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plt
from reportlab.platypus import Image, Spacer

# --- Chart Generation Helper (Enhanced) ---
def generate_chart_img(type, data, labels, title, color_palette=None, value_fmt="{:.0f}"):
    # Adjust figure size for better aspect ratio in reports
    fig = Figure(figsize=(7, 4)) 
    ax = fig.add_subplot(111)
    
    # Default Palette
    if not color_palette:
        color_palette = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
    
    # ensure consistent color cycle
    colors = color_palette * (len(data) // len(color_palette) + 1)

    if type == 'pie':
        wedges, texts, autotexts = ax.pie(data, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
        plt.setp(texts, size=8)
        plt.setp(autotexts, size=8, weight="bold", color="white")
        
    elif type == 'donut':
        wedges, texts, autotexts = ax.pie(data, labels=labels, autopct='%1.1f%%', startangle=90, pctdistance=0.85, colors=colors)
        centre_circle = matplotlib.patches.Circle((0,0),0.70,fc='white')
        ax.add_artist(centre_circle)
        plt.setp(texts, size=8)
        plt.setp(autotexts, size=8, weight="bold", color="white")
        
    elif type == 'bar':
        bars = ax.bar(labels, data, color=colors[:len(data)])
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.yaxis.grid(True, linestyle='--', alpha=0.7, color='#e5e7eb')
        ax.set_axisbelow(True)
        
        fig.autofmt_xdate(rotation=45, ha='right')
        
        for bar in bars:
            height = bar.get_height()
            ax.annotate(value_fmt.format(height),
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3), 
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=8, color='#374151')

    elif type == 'barh':
        # Horizontal Bar Chart (Rainbow Request)
        y_pos = range(len(labels))
        bars = ax.barh(y_pos, data, color=colors[:len(data)])
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels)
        ax.invert_yaxis()  # Labels read top-to-bottom
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.xaxis.grid(True, linestyle='--', alpha=0.7, color='#e5e7eb')
        ax.set_axisbelow(True)
        
        # Annotate right of bar
        for bar in bars:
            width = bar.get_width()
            ax.annotate(value_fmt.format(width),
                        xy=(width, bar.get_y() + bar.get_height() / 2),
                        xytext=(3, 0),  # 3 points horizontal offset
                        textcoords="offset points",
                        ha='left', va='center', fontsize=8, color='#374151')

    ax.set_title(title, pad=20, fontsize=12, fontweight='bold', color='#1f2937')
    fig.tight_layout()
    
    img_buffer = io.BytesIO()
    FigureCanvas(fig).print_png(img_buffer)
    img_buffer.seek(0)
    return img_buffer

def gerar_relatorio_graficos(mes_referencia_str):
    buffer = io.BytesIO()
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import PageBreak, KeepTogether
    
    # Switch to A4 Portrait for this report
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # Introduction
    elements.append(Paragraph(f"Relatório Gerencial Gráfico - {mes_referencia_str}", styles['Title']))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("Este documento apresenta uma análise visual da distribuição de bolsas e recursos financeiros da instituição.", styles['Normal']))
    elements.append(Spacer(1, 20))

    # --- Data Gathering ---
    from sqlalchemy import not_
    from models import ProgramaAcademico
    active_bolsistas = Bolsista.query.join(ProgramaAcademico).filter(
        Bolsista.ativo==True,
        not_(ProgramaAcademico.nome_programa.ilike('%*%'))
    ).all()
    modalidades = Modalidade.query.all()

    # Maps - Keys are now tuples (Name, Campus) where applicable to ensure uniqueness and label info
    campus_count = {}
    campus_invest = {}
    prog_count = {} # Key: (Program Name, Campus Sigla)
    prog_invest = {} # Key: (Program Name, Campus Sigla)

    for b in active_bolsistas:
        # Campus
        c = b.sigla_campus_display or 'N/A'
        campus_count[c] = campus_count.get(c, 0) + 1
        
        # Investment
        val = Decimal('0')
        if b.modalidade:
            val = b.modalidade.valor_mensal
            if getattr(b, 'tem_adicional', False):
                val += b.valor_adicional
            campus_invest[c] = campus_invest.get(c, 0) + val
            
        # Program
        p_name = b.programa_link.nome_programa if b.programa_link else (b.programa if b.programa else 'N/A')
        p_campus = c # Use the campus derived above
        p_key = (p_name, p_campus)
        
        prog_count[p_key] = prog_count.get(p_key, 0) + 1
        
        # Investment per Program (Chart 4)
        prog_invest[p_key] = prog_invest.get(p_key, 0) + val

    # [NEW] Include Residents in Investment Data
    from models import Residente
    active_res = Residente.query.filter_by(ativo=True).all()
    
    for r in active_res:
        # Check if paying scholar
        # Logic: valor_bolsa > 0 OR (recebe_bolsa AND modalidade)
        val_res = Decimal('0')
        if r.valor_bolsa:
            val_res = r.valor_bolsa
        elif r.recebe_bolsa and r.modalidade:
            val_res = r.modalidade.valor_mensal
            if getattr(r, 'tem_adicional', False):
                val_res += r.valor_adicional
                
        if val_res > 0:
            # Resolve Campus
            c_res = "N/A"
            p_name_res = "N/A"
            if r.programa_link:
                p_name_res = r.programa_link.nome_programa
                if r.programa_link.campus:
                    c_res = r.programa_link.campus.sigla_campus
            
            # Add to maps
            campus_invest[c_res] = campus_invest.get(c_res, 0) + val_res
            
            p_key_res = (p_name_res, c_res)
            prog_invest[p_key_res] = prog_invest.get(p_key_res, 0) + val_res

    # Style Definition
    style_explanation = styles['Normal']
    style_explanation.textColor = colors.HexColor("#4b5563")
    style_explanation.fontSize = 10
    style_explanation.leading = 14
    
    # Store images for summary
    summary_images = []

    # 1. Bolsistas por Campus (Bar)
    if campus_count:
        sorted_campus = sorted(campus_count.items(), key=lambda x: x[1], reverse=True)
        c_labels = [x[0] for x in sorted_campus]
        c_values = [x[1] for x in sorted_campus]
        
        img_data = generate_chart_img('bar', c_values, c_labels, "Bolsistas Ativos por Campus", 
                                    color_palette=['#2563eb', '#3b82f6', '#60a5fa', '#93c5fd', '#bfdbfe'])
        
        summary_images.append(Image(img_data, width=200, height=140))
        
        elements.append(KeepTogether([
            Paragraph("<b>1. Distribuição Geográfica de Bolsistas</b>", styles['Heading2']),
            Paragraph("O gráfico abaixo demonstra a quantidade absoluta de bolsistas ativos em cada Campus. Esta métrica ajuda a identificar a capilaridade do programa.", style_explanation),
            Spacer(1, 10),
            Image(img_data, width=450, height=280)
        ]))
        elements.append(PageBreak())

    # 2. Investimento por Campus (Bar Horizontal)
    if campus_invest:
        sorted_invest = sorted(campus_invest.items(), key=lambda x: x[1], reverse=True)
        i_labels = [x[0] for x in sorted_invest]
        i_values = [float(x[1]) for x in sorted_invest]
        
        rainbow_colors = ['#ffadad', '#ffd6a5', '#fdffb6', '#caffbf', '#9bf6ff', '#a0c4ff', '#bdb2ff', '#ffc6ff', '#fffffc']
        
        img_data_h = generate_chart_img('barh', i_values, i_labels, "Investimento Mensal (R$)", 
                                    color_palette=rainbow_colors, 
                                    value_fmt="R$ {:,.0f}")
        
        summary_images.append(Image(img_data_h, width=200, height=140))

        elements.append(KeepTogether([
            Paragraph("<b>2. Investimento Mensal por Campus</b>", styles['Heading2']),
            Paragraph("Volume de recursos financeiros (R$) repassados mensalmente para cada unidade. Visualização horizontal para facilitar a leitura dos valores e evitar sobreposição.", style_explanation),
            Spacer(1, 10),
            Image(img_data_h, width=450, height=280)
        ]))
        elements.append(PageBreak())

    # 3. Bolsistas por Programa (Bar Horizontal) [UPDATED: Include Campus Sigla]
    if prog_count:
        sorted_progs = sorted(prog_count.items(), key=lambda x: x[1], reverse=True)[:10]
        # Format label: "Nome do Programa (SIGLA)"
        labels = []
        for item in sorted_progs:
            p_name, p_campus = item[0]
            label_text = f"{p_name} ({p_campus})"
            # Truncate if too long (keeping sigla at end if possible, but simple truncate for safety)
            if len(label_text) > 40:
                label_text = p_name[:35] + f"... ({p_campus})"
            labels.append(label_text)
            
        values = [x[1] for x in sorted_progs]
        
        prog_colors = ['#7c3aed', '#8b5cf6', '#a78bfa', '#c4b5fd', '#ddd6fe', '#ede9fe']
        
        img_data = generate_chart_img('barh', values, labels, "Bolsistas por Programa (Top 10)", 
                                    color_palette=prog_colors)
        
        summary_images.append(Image(img_data, width=200, height=140))

        elements.append(KeepTogether([
            Paragraph("<b>3. Top 10 Programas com Mais Bolsistas</b>", styles['Heading2']),
            Paragraph("Programas de Pós-Graduação com maior número de beneficiários ativos, com indicação do Campus.", style_explanation),
            Spacer(1, 10),
            Image(img_data, width=450, height=280)
        ]))
        elements.append(PageBreak())

    # 4. Ranking de Arrecadação por Programa [UPDATED: Include Campus Sigla]
    if prog_invest:
        sorted_prog_inv = sorted(prog_invest.items(), key=lambda x: x[1], reverse=True)[:10]
        
        inv_labels = []
        for item in sorted_prog_inv:
            p_name, p_campus = item[0]
            label_text = f"{p_name} ({p_campus})"
            if len(label_text) > 40:
                label_text = p_name[:35] + f"... ({p_campus})"
            inv_labels.append(label_text)

        inv_values = [float(x[1]) for x in sorted_prog_inv]
        
        img_data_inv = generate_chart_img('barh', inv_values, inv_labels, "Ranking de Arrecadação (R$/mês)", 
                                        color_palette=['#0ea5e9', '#38bdf8', '#7dd3fc', '#bae6fd', '#e0f2fe'],
                                        value_fmt="R$ {:,.0f}")
        
        summary_images.append(Image(img_data_inv, width=200, height=140))
        
        elements.append(KeepTogether([
            Paragraph("<b>4. Ranking de Arrecadação por Programa</b>", styles['Heading2']),
            Paragraph("Programas que mais captam recursos financeiros (somatório do valor das bolsas). Indicados com o respectivo Campus.", style_explanation),
            Spacer(1, 10),
            Image(img_data_inv, width=450, height=280)
        ]))
        elements.append(PageBreak())

    # 5. Residentes por Campus [EXISTING]
    from models import Residente
    active_residentes = Residente.query.filter_by(ativo=True).all()
    res_campus_count = {}
    res_prog_count = {} # [NEW]
    res_bolsa_stats = {"Com Bolsa": 0, "Voluntário": 0} # [NEW]
    
    for r in active_residentes:
        # Resolve Campus and Program Link
        c = "N/A"
        p_name = "N/A"
        if r.programa_link:
             p_name = r.programa_link.nome_programa
             if r.programa_link.campus:
                 c = r.programa_link.campus.sigla_campus
        
        res_campus_count[c] = res_campus_count.get(c, 0) + 1
        
        # Resident Program Count
        rp_key = (p_name, c)
        res_prog_count[rp_key] = res_prog_count.get(rp_key, 0) + 1
        
        # Scholarship Status
        if r.recebe_bolsa:
            res_bolsa_stats["Com Bolsa"] += 1
        else:
            res_bolsa_stats["Voluntário"] += 1
        
    if res_campus_count:
        sorted_res = sorted(res_campus_count.items(), key=lambda x: x[1], reverse=True)
        res_labels = [x[0] for x in sorted_res]
        res_values = [x[1] for x in sorted_res]
        
        img_data_res = generate_chart_img('bar', res_values, res_labels, "Residentes por Campus",
                                         color_palette=['#f59e0b', '#fbbf24', '#fcd34d', '#fde68a', '#fef3c7'])
        
        summary_images.append(Image(img_data_res, width=200, height=140))
        
        elements.append(KeepTogether([
            Paragraph("<b>5. Distribuição de Residentes (Pós-Doc) por Campus</b>", styles['Heading2']),
            Paragraph("Concentração de pesquisadores em estágio pós-doutoral (Residentes) por campus.", style_explanation),
            Spacer(1, 10),
            Image(img_data_res, width=450, height=280)
        ]))
        elements.append(PageBreak())

    # 6. [NEW] Residentes por Programa (Horizontal)
    if res_prog_count:
        sorted_res_progs = sorted(res_prog_count.items(), key=lambda x: x[1], reverse=True)[:10] # Top 10
        
        rp_labels = []
        for item in sorted_res_progs:
            p_name, p_campus = item[0]
            label_text = f"{p_name} ({p_campus})"
            if len(label_text) > 40:
                label_text = p_name[:35] + f"... ({p_campus})"
            rp_labels.append(label_text)
            
        rp_values = [x[1] for x in sorted_res_progs]
         
        img_data_rp = generate_chart_img('barh', rp_values, rp_labels, "Residentes por Programa (Top 10)",
                                         color_palette=['#ec4899', '#f472b6', '#fbcfe8', '#fce7f3', '#fdf2f8'])
         
        summary_images.append(Image(img_data_rp, width=200, height=140))
         
        elements.append(KeepTogether([
            Paragraph("<b>6. Residentes por Programa</b>", styles['Heading2']),
            Paragraph("Programas com maior número de pós-doutorandos (Residentes), indicados com o Campus.", style_explanation),
            Spacer(1, 10),
            Image(img_data_rp, width=450, height=280)
        ]))
        elements.append(PageBreak())

    # 7. [NEW] Residentes: Com Bolsa vs Voluntário (Pie/Donut)
    if sum(res_bolsa_stats.values()) > 0:
        rb_labels = list(res_bolsa_stats.keys())
        rb_values = list(res_bolsa_stats.values())
        
        img_data_rb = generate_chart_img('donut', rb_values, rb_labels, "Status do Residente (Bolsa vs Voluntário)",
                                         color_palette=['#10b981', '#6b7280'])
                                         
        summary_images.append(Image(img_data_rb, width=200, height=140))
        
        elements.append(KeepTogether([
            Paragraph("<b>7. Status de Financiamento dos Residentes</b>", styles['Heading2']),
            Paragraph("Proporção de residentes que recebem bolsa fomento vs. residentes voluntários.", style_explanation),
            Spacer(1, 10),
            Image(img_data_rb, width=450, height=280)
        ]))
        elements.append(PageBreak())

    # 6. Financeiro: Previsto vs Realizado (Was 4)
    total_previsto = Decimal('0')
    total_realizado = sum(campus_invest.values()) if campus_invest else Decimal('0')
    for mod in modalidades:
        total_previsto += (mod.vagas * mod.valor_mensal)
        
    img_data = generate_chart_img('bar', [float(total_realizado), float(total_previsto)], ['Realizado (Mensal)', 'Potencial Total'], "Execução Orçamentária (R$)",
                                color_palette=['#ea580c', '#fb923c'], 
                                value_fmt="R$ {:,.0f}")
    
    summary_images.append(Image(img_data, width=200, height=140))

    elements.append(KeepTogether([
        Paragraph("<b>6. Eficiência da Execução Financeira</b>", styles['Heading2']),
        Paragraph("Comparativo entre o teto orçamentário mensal e a execução atual.", style_explanation),
        Spacer(1, 10),
        Image(img_data, width=450, height=280)
    ]))
    
    # 7. Vacancy (Was 5) - [UPDATED] Exclude Post-Doc
    level_stats = {} 
    for mod in modalidades:
        # Filter Logic: Exclude 'PÓS-DOUTORADO'
        if 'DOUTORADO' in mod.nivel.upper() and 'PÓS' in mod.nivel.upper():
            continue
            
        if mod.nivel not in level_stats:
            level_stats[mod.nivel] = {'vagas': 0, 'occupied': 0}
        level_stats[mod.nivel]['vagas'] += mod.vagas
        occ = Bolsista.query.filter_by(modalidade_id=mod.id, ativo=True).count()
        level_stats[mod.nivel]['occupied'] += occ

    v_labels = []
    v_data = [] 
    for lvl, stats in level_stats.items():
        v_labels.append(lvl)
        idle = max(0, stats['vagas'] - stats['occupied'])
        v_data.append(idle)
    
    if v_labels:
         elements.append(PageBreak())
         img_data = generate_chart_img('bar', v_data, v_labels, "Vagas Não Preenchidas (Exceto Pós-Doc)",
                                      color_palette=['#db2777', '#ec4899', '#f472b6'],
                                      value_fmt="{:.0f}")
         
         summary_images.append(Image(img_data, width=200, height=140))
         
         elements.append(KeepTogether([
            Paragraph("<b>7. Vagas Disponíveis (Ociosas)</b>", styles['Heading2']),
            Paragraph("Quantidade de bolsas autorizadas não ocupadas (excluindo Pós-Doutorado).", style_explanation),
            Spacer(1, 10),
            Image(img_data, width=450, height=280)
         ]))
    
    # --- Summary Page ---
    elements.append(PageBreak())
    elements.append(Paragraph("Resumo Executivo", styles['Title']))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("Visão geral dos indicadores chave apresentados neste relatório.", style_explanation))
    elements.append(Spacer(1, 20))

    # Grid of Minimized Charts (2 columns)
    chart_table_data = []
    row_buffer = []
    
    for img in summary_images:
        row_buffer.append(img)
        if len(row_buffer) == 2:
            chart_table_data.append(row_buffer)
            row_buffer = []
    
    if row_buffer:
        # Fill empty cell for alignment if odd number
        row_buffer.append(Spacer(1,1))
        chart_table_data.append(row_buffer)
        
    t = Table(chart_table_data, colWidths=[250, 250])
    t.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
    ]))
    
    elements.append(t)

    doc.build(elements)
    buffer.seek(0)
    return buffer

def gerar_relatorio_programas():
    # [NEW] Exports Programs List
    from models import ProgramaAcademico
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Programas Pós-Graduação"
    
    headers = ["ID", "Código", "Nome", "Sigla", "Campus", "Nota Capes", "Área Avaliação", "Níveis"]
    ws.append(headers)
    
    from sqlalchemy import not_
    progs = ProgramaAcademico.query.filter(not_(ProgramaAcademico.nome_programa.ilike('%*%'))).all()
    
    for p in progs:
        row = [
            p.id,
            p.codigo_programa or "N/A",
            p.nome_programa,
            p.sigla_programa,
            p.campus.nome if p.campus else "N/A",
            p.nota_capes or "-",
            p.area_avaliacao or "-",
            p.niveis or "-"
        ]
        ws.append(row)
        
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output

def gerar_relatorio_devolucao():
    buffer = io.BytesIO()
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    from datetime import date
    from models import Bolsista
    
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    elements.append(Paragraph("Relatório de Monitoramento: Devolução de Valores", styles['Title']))
    elements.append(Paragraph(f"Gerado em: {date.today().strftime('%d/%m/%Y')}", styles['Normal']))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("Discentes monitorados com pendência de devolução de bolsas (Desligados sem Defesa).", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # 1. Fetch Data
    bolsistas = Bolsista.query.filter_by(ativo=False, devolucao_valores=True).all()
    
    # Sort by Campus, then Program, then Name
    bolsistas.sort(key=lambda b: (
        b.programa_link.campus.nome if b.programa_link and b.programa_link.campus else (b.campus.nome if b.campus else ""),
        b.programa_link.nome_programa if b.programa_link else (b.programa or ""),
        b.nome
    ))
    
    # 2. Detailed Table
    data = [["Nome", "CPF", "Programa", "Campus", "Data Desl.", "Motivo"]]
    
    prog_stats = {} # (Nome, Campus) -> Count
    
    for b in bolsistas:
        prog_nome = b.programa_link.nome_programa if b.programa_link else (b.programa or "-")
        campus_nome = b.sigla_campus_display or "-"
        
        # Stats
        key = (prog_nome, campus_nome)
        prog_stats[key] = prog_stats.get(key, 0) + 1
        
        row = [
            b.nome[:25] + "..." if len(b.nome)>25 else b.nome,
            b.cpf,
            prog_nome[:30] + "..." if len(prog_nome)>30 else prog_nome,
            campus_nome,
            b.data_desligamento.strftime('%d/%m/%Y') if b.data_desligamento else "-",
            b.motivo_desligamento[:20] + "..." if b.motivo_desligamento else "-"
        ]
        data.append(row)
        
    if len(data) > 1:
        # Columns Widths: Total ~535pt
        t = Table(data, colWidths=[130, 80, 140, 40, 65, 80])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#9f1239")), # Red header
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ROWBACKGROUNDS', (1, 1), (-1, -1), [colors.white, colors.HexColor("#fff1f2")])
        ]))
        elements.append(t)
    else:
        elements.append(Paragraph("Nenhum registro de devolução pendente encontrado.", styles['Normal']))
        
    elements.append(Spacer(1, 30))
    
    # 3. Ranking Stats
    if prog_stats:
        elements.append(Paragraph("Ranking de Desligamentos com Devolução por Programa/Campus", styles['Heading2']))
        stats_data = [["Programa", "Campus", "Qtd. Desligamentos"]]
        
        sorted_stats = sorted(prog_stats.items(), key=lambda x: x[1], reverse=True)
        
        for (p, c), count in sorted_stats:
            stats_data.append([p, c, str(count)])
            
        t2 = Table(stats_data, colWidths=[300, 80, 100])
        t2.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#334155")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ALIGN', (-1, 0), (-1, -1), 'CENTER')
        ]))
        elements.append(t2)
        
    doc.build(elements)

def gerar_relatorio_eixo_pdf(eixo_filtro='ALL'):
    buffer = io.BytesIO()
    from reportlab.lib.pagesizes import A4, landscape
    from models import Bolsista, Edital
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=30, leftMargin=30, topMargin=40, bottomMargin=30)
    elements = []
    styles = getSampleStyleSheet()
    
    title = f"Relatório de Execução NAPI-Robótica - Eixo: {eixo_filtro}"
    elements.append(Paragraph(title, styles['Title']))
    elements.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y')}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Headers
    headers = ["Edital", "Eixo", "Bolsista", "CPF", "Modalidade", "Valor Mensal", "Início"]
    data = [headers]
    
    query = Bolsista.query.join(Edital)
    if eixo_filtro != 'ALL':
        query = query.filter(Edital.eixo == eixo_filtro)
    
    bolsistas = query.filter(Bolsista.ativo == True).all()
    
    total_mensal = 0.0
    for b in bolsistas:
        val = b.modalidade.valor_mensal if b.modalidade else 0.0
        total_mensal += val
        
        row = [
            b.edital.numero,
            b.edital.eixo or "N/D",
            b.nome[:30],
            b.cpf,
            b.modalidade.nivel if b.modalidade else "-",
            f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            b.data_inicio_bolsa.strftime('%d/%m/%Y') if b.data_inicio_bolsa else "-"
        ]
        data.append(row)
    
    t = Table(data, colWidths=[60, 100, 200, 90, 100, 110, 80])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#00d2ff")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (1, 1), (-1, -1), [colors.white, colors.HexColor("#f0faff")]),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    elements.append(t)
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"<b>Investimento Mensal Total no Eixo {eixo_filtro}: R$ {total_mensal:,.2f}</b>".replace(",", "X").replace(".", ",").replace("X", "."), styles['Normal']))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer
