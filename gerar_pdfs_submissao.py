"""
Gerador de PDFs para pasta Arandu_submissao (Requisito INPI 3.5.2)
Sistema Arandú — PROPPG/UTFPR
Autor: Higo Figueiredo dos Santos
"""

import os
import sys
import re
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, HRFlowable, PageBreak, Preformatted)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfgen import canvas

# ─── Paleta de cores UTFPR ───────────────────────────────────────────────────
AZUL_UTFPR   = colors.HexColor('#003366')
AZUL_CLARO   = colors.HexColor('#005B9F')
AZUL_BG      = colors.HexColor('#EBF3FB')
CINZA_ESCURO = colors.HexColor('#333333')
CINZA_MEDIO  = colors.HexColor('#666666')
CINZA_LINHA  = colors.HexColor('#CCCCCC')
VERDE        = colors.HexColor('#1A7A3A')
AMARELO      = colors.HexColor('#F5A623')
VERMELHO     = colors.HexColor('#C0392B')
BRANCO       = colors.white
BRANCO_OFF   = colors.HexColor('#F4F4F4')

PAGE_W, PAGE_H = A4

def header_footer(canvas_obj, doc):
    canvas_obj.saveState()
    w, h = A4
    # Cabeçalho
    canvas_obj.setFillColor(AZUL_UTFPR)
    canvas_obj.rect(0, h - 1.8*cm, w, 1.8*cm, fill=True, stroke=False)
    canvas_obj.setFillColor(BRANCO)
    canvas_obj.setFont('Helvetica-Bold', 10)
    canvas_obj.drawString(1.2*cm, h - 1.05*cm, 'SISTEMA ARANDÚ — INPI 3.5.2')
    canvas_obj.setFont('Helvetica', 8)
    canvas_obj.drawRightString(w - 1.2*cm, h - 1.05*cm, doc.title)
    # Rodapé
    canvas_obj.setFillColor(AZUL_UTFPR)
    canvas_obj.rect(0, 0, w, 1.0*cm, fill=True, stroke=False)
    canvas_obj.setFillColor(BRANCO)
    canvas_obj.setFont('Helvetica', 7)
    canvas_obj.drawString(1.2*cm, 0.4*cm, 'Higo Figueiredo dos Santos | UTFPR - PROPPG | Março 2026')
    canvas_obj.drawRightString(w - 1.2*cm, 0.4*cm, f'Página {doc.page}')
    canvas_obj.restoreState()

def build_styles():
    base = getSampleStyleSheet()
    styles = {
        'title': ParagraphStyle('title', fontName='Helvetica-Bold', fontSize=22, textColor=AZUL_UTFPR, spaceAfter=12, leading=26, alignment=TA_CENTER),
        'subtitle': ParagraphStyle('subtitle', fontName='Helvetica', fontSize=14, textColor=CINZA_MEDIO, spaceAfter=10, leading=18, alignment=TA_CENTER),
        'h1': ParagraphStyle('h1', fontName='Helvetica-Bold', fontSize=16, textColor=BRANCO, spaceBefore=16, spaceAfter=8, backColor=AZUL_UTFPR, borderPadding=(6, 10, 6, 10)),
        'h2': ParagraphStyle('h2', fontName='Helvetica-Bold', fontSize=13, textColor=AZUL_UTFPR, spaceBefore=12, spaceAfter=4),
        'h3': ParagraphStyle('h3', fontName='Helvetica-Bold', fontSize=11, textColor=AZUL_CLARO, spaceBefore=10, spaceAfter=3),
        'body': ParagraphStyle('body', fontName='Helvetica', fontSize=10, textColor=CINZA_ESCURO, spaceAfter=6, leading=14, alignment=TA_JUSTIFY),
        'bullet': ParagraphStyle('bullet', fontName='Helvetica', fontSize=10, textColor=CINZA_ESCURO, spaceAfter=4, leftIndent=18, leading=13),
        'code': ParagraphStyle('code', fontName='Courier', fontSize=8.5, textColor=CINZA_ESCURO, spaceAfter=8, backColor=BRANCO_OFF, borderPadding=(8, 10, 8, 10), leading=12),
        'table_header': ParagraphStyle('table_header', fontName='Helvetica-Bold', fontSize=9, textColor=BRANCO, alignment=TA_CENTER),
        'table_cell': ParagraphStyle('table_cell', fontName='Helvetica', fontSize=9, textColor=CINZA_ESCURO, leading=12),
    }
    return styles

def md_inline(text):
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'__(.+?)__',     r'<b>\1</b>', text)
    text = re.sub(r'\*(.+?)\*',     r'<i>\1</i>', text)
    text = re.sub(r'`([^`]+)`',     r'<font name="Courier" size="9">\1</font>', text)
    return text

def render_table(rows, styles):
    if not rows: return []
    col_count = max(len(r) for r in rows)
    norm = [ (r + [''] * col_count)[:col_count] for r in rows ]
    avail = PAGE_W - 3*cm
    col_w = [avail / col_count] * col_count
    data = []
    for ri, row in enumerate(norm):
        st = styles['table_header'] if ri == 0 else styles['table_cell']
        data.append([Paragraph(md_inline(c), st) for c in row])
    t = Table(data, colWidths=col_w, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), AZUL_UTFPR),
        ('TEXTCOLOR',  (0,0), (-1,0), BRANCO),
        ('ALIGN',      (0,0), (-1,-1), 'LEFT'),
        ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
        ('GRID',       (0,0), (-1,-1), 0.5, CINZA_LINHA),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [BRANCO, AZUL_BG]),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    return [Spacer(1, 8), t, Spacer(1, 8)]

def parse_markdown(md_text, styles):
    story = []
    lines = md_text.split('\n')
    i = 0
    in_code = False
    code_lines = []
    while i < len(lines):
        line = lines[i].rstrip()
        if line.startswith('```'):
            if not in_code: in_code = True; code_lines = []
            else:
                in_code = False
                story.append(Preformatted('\n'.join(code_lines), styles['code']))
            i += 1; continue
        if in_code: code_lines.append(line); i += 1; continue
        if line.strip() == '' or line.strip() == '---':
            if line.strip() == '---':
                story.append(Spacer(1, 6))
                story.append(HRFlowable(width='100%', thickness=1, color=CINZA_LINHA, spaceAfter=6, spaceBefore=6))
            else: story.append(Spacer(1, 6))
            i += 1; continue
        if '|' in line and line.strip().startswith('|'):
            table_rows = []
            while i < len(lines) and '|' in lines[i] and lines[i].strip().startswith('|'):
                if not set(lines[i].strip().replace('|','').replace('-','').replace(':','').replace(' ','')):
                    i += 1; continue
                table_rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')])
                i += 1
            story += render_table(table_rows, styles)
            continue
        h_match = re.match(r'^(#{1,4})\s+(.*)', line)
        if h_match:
            lvl = len(h_match.group(1)); txt = h_match.group(2).strip()
            if lvl == 1: story.append(Paragraph(md_inline(txt), styles['title']))
            elif lvl == 2: story.append(Paragraph(md_inline(txt), styles['h1']))
            elif lvl == 3: story.append(Paragraph(md_inline(txt), styles['h2']))
            else: story.append(Paragraph(md_inline(txt), styles['h3']))
            i += 1; continue
        bullet_match = re.match(r'^(\s*[-*])\s+(.*)', line)
        if bullet_match:
            story.append(Paragraph(f'• {md_inline(bullet_match.group(2).strip())}', styles['bullet']))
            i += 1; continue
        cb_match = re.match(r'^\s*[-*]?\s*\[([ xX])\]\s+(.*)', line)
        if cb_match:
            icon = '✅' if cb_match.group(1).lower() == 'x' else '☐'
            story.append(Paragraph(f'{icon} {md_inline(cb_match.group(2).strip())}', styles['bullet']))
            i += 1; continue
        if line.strip():
            story.append(Paragraph(md_inline(line.strip()), styles['body']))
        i += 1
    return story

def draw_cover(canvas_obj, doc):
    canvas_obj.saveState()
    w, h = A4
    canvas_obj.setFillColor(AZUL_UTFPR)
    canvas_obj.rect(0, h - 6*cm, w, 6*cm, fill=True, stroke=False)
    canvas_obj.setFillColor(BRANCO)
    canvas_obj.setFont('Helvetica-Bold', 48)
    canvas_obj.drawCentredString(w/2, h - 2.8*cm, 'UTFPR')
    canvas_obj.setFont('Helvetica', 12)
    canvas_obj.drawCentredString(w/2, h - 3.8*cm, 'Universidade Tecnológica Federal do Paraná')
    canvas_obj.setFont('Helvetica-Oblique', 10)
    canvas_obj.setFillColor(colors.HexColor('#ADC9E9'))
    canvas_obj.drawCentredString(w/2, h - 4.6*cm, 'Pró-Reitoria de Pesquisa e Pós-Graduação — PROPPG')
    canvas_obj.setFillColor(AZUL_CLARO)
    canvas_obj.setFont('Helvetica-Bold', 18)
    canvas_obj.drawCentredString(w/2, h - 8.5*cm, 'Sistema Arandú')
    # ── Título do documento (usando Paragraph para quebra automática) ──
    from reportlab.platypus import Paragraph
    styles = build_styles()
    p_title = Paragraph(doc.title.upper(), styles['title'])
    w_title, h_title = p_title.wrap(w - 4*cm, 10*cm)
    # Posicionar o topo do parágrafo em h - 11.0cm
    p_title.drawOn(canvas_obj, 2*cm, h - 11.0*cm - h_title)

    # ── Subtítulo do documento ──
    p_sub = Paragraph(doc._cover_subtitle, styles['subtitle'])
    w_sub, h_sub = p_sub.wrap(w - 6*cm, 10*cm)
    # Posicionar o topo do parágrafo em h - 13.8cm
    p_sub.drawOn(canvas_obj, 3*cm, h - 13.8*cm - h_sub)

    # ── Linha separadora central ──
    canvas_obj.setStrokeColor(AZUL_UTFPR); canvas_obj.setLineWidth(1.5)
    canvas_obj.line(3*cm, h - 15.5*cm, w - 3*cm, h - 15.5*cm)

    # ── Bloco de metadados ──
    canvas_obj.setFillColor(AZUL_UTFPR); canvas_obj.setFont('Helvetica-Bold', 10)
    canvas_obj.drawString(6*cm, h - 17.5*cm, 'Responsável:')
    canvas_obj.drawString(6*cm, h - 18.5*cm, 'Data:')
    canvas_obj.drawString(6*cm, h - 19.5*cm, 'Requisito:')
    canvas_obj.setFillColor(CINZA_ESCURO); canvas_obj.setFont('Helvetica', 10)
    canvas_obj.drawString(10*cm, h - 17.5*cm, 'Higo Figueiredo dos Santos')
    canvas_obj.drawString(10*cm, h - 18.5*cm, 'Março de 2026')
    canvas_obj.drawString(10*cm, h - 19.5*cm, 'INPI — Item 3.5.2')
    canvas_obj.setFillColor(AZUL_UTFPR)
    canvas_obj.rect(0, 0, w, 1.5*cm, fill=True, stroke=False)
    canvas_obj.setFillColor(BRANCO); canvas_obj.setFont('Helvetica', 8)
    canvas_obj.drawCentredString(w/2, 0.6*cm, 'DOCUMENTO PARA REGISTRO DE PROGRAMA DE COMPUTADOR — AGINT/UTFPR')
    canvas_obj.restoreState()

def generate_pdf(md_path, pdf_path, doc_title, subtitle):
    styles = build_styles()
    doc = SimpleDocTemplate(pdf_path, pagesize=A4, leftMargin=1.5*cm, rightMargin=1.5*cm, topMargin=3.5*cm, bottomMargin=2.0*cm, title=doc_title)
    doc._cover_subtitle = subtitle
    with open(md_path, 'r', encoding='utf-8') as f: md_text = f.read()
    # Adicionado Spacer(1, 1*cm) no início para evitar sobreposição com o cabeçalho na página 2
    story = [PageBreak(), Spacer(1, 1*cm)] + parse_markdown(md_text, styles)
    doc.build(story, onFirstPage=draw_cover, onLaterPages=header_footer)
    print(f'✅ Concluído: {os.path.basename(pdf_path)}')

if __name__ == '__main__':
    BASE = r'C:\Users\higosantos\Documents\gestao_editais\gestao_editais_novo\Arandu_submissao'
    files = [
        ('DOCUMENTACAO_INPI.md', '3.5.2_DOCUMENTACAO_INPI.pdf', 'Documentação Técnica - SISTEMA ARANDÚ', 'Arquitetura, Stack Tecnológica e Navegação'),
        ('MANUAL_INSTALACAO.md', '3.5.2_MANUAL_INSTALACAO.pdf', 'Manual de Instalação - SISTEMA ARANDÚ', 'Requisitos, Docker e Implantação Manual'),
        ('MANUAL_APLICABILIDADE.md', '3.5.2_MANUAL_APLICABILIDADE.pdf', 'Manual de Aplicabilidade - SISTEMA ARANDÚ', 'Público-Alvo, Módulos e Fluxo de Trabalho'),
    ]
    for md, pdf, title, sub in files:
        generate_pdf(os.path.join(BASE, md), os.path.join(BASE, pdf), title, sub)
