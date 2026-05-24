"""
Gerador de PDFs para DOCUMENTACAO.md e COMO_USAR.md
Sistema Arandú — PROPPG/UTFPR
Autor: Higo Figueiredo dos Santos
"""

import os
import sys
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, HRFlowable, PageBreak, Preformatted)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfgen import canvas
import re

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
PRETO        = colors.black

PAGE_W, PAGE_H = A4


def header_footer(canvas_obj, doc):
    """Cabeçalho e rodapé em todas as páginas."""
    canvas_obj.saveState()
    w, h = A4

    # ── Cabeçalho ──
    canvas_obj.setFillColor(AZUL_UTFPR)
    canvas_obj.rect(0, h - 2*cm, w, 2*cm, fill=True, stroke=False)

    canvas_obj.setFillColor(BRANCO)
    canvas_obj.setFont('Helvetica-Bold', 11)
    canvas_obj.drawString(1.5*cm, h - 1.1*cm, 'Sistema Arandú — PROPPG/UTFPR')
    canvas_obj.setFont('Helvetica', 8)
    canvas_obj.drawRightString(w - 1.5*cm, h - 1.1*cm, doc.title)

    # ── Rodapé ──
    canvas_obj.setFillColor(AZUL_UTFPR)
    canvas_obj.rect(0, 0, w, 1.2*cm, fill=True, stroke=False)

    canvas_obj.setFillColor(BRANCO)
    canvas_obj.setFont('Helvetica', 7.5)
    canvas_obj.drawString(1.5*cm, 0.45*cm,
        'Higo Figueiredo dos Santos | Universidade Tecnológica Federal do Paraná | Março 2026')
    canvas_obj.drawRightString(w - 1.5*cm, 0.45*cm, f'Página {doc.page}')

    canvas_obj.restoreState()


def build_styles():
    """Define todos os estilos do documento."""
    base = getSampleStyleSheet()

    styles = {
        'title': ParagraphStyle('title',
            fontName='Helvetica-Bold', fontSize=22,
            textColor=AZUL_UTFPR, spaceAfter=6,
            alignment=TA_CENTER),

        'subtitle': ParagraphStyle('subtitle',
            fontName='Helvetica', fontSize=12,
            textColor=CINZA_MEDIO, spaceAfter=4,
            alignment=TA_CENTER),

        'version': ParagraphStyle('version',
            fontName='Helvetica-Oblique', fontSize=9,
            textColor=CINZA_MEDIO, spaceAfter=20,
            alignment=TA_CENTER),

        'h1': ParagraphStyle('h1',
            fontName='Helvetica-Bold', fontSize=15,
            textColor=BRANCO, spaceBefore=14, spaceAfter=6,
            leftIndent=0, backColor=AZUL_UTFPR,
            borderPadding=(6, 10, 6, 10)),

        'h2': ParagraphStyle('h2',
            fontName='Helvetica-Bold', fontSize=12,
            textColor=AZUL_UTFPR, spaceBefore=12, spaceAfter=4,
            borderPadding=(4, 0, 4, 0)),

        'h3': ParagraphStyle('h3',
            fontName='Helvetica-Bold', fontSize=10,
            textColor=AZUL_CLARO, spaceBefore=8, spaceAfter=3),

        'body': ParagraphStyle('body',
            fontName='Helvetica', fontSize=9.5,
            textColor=CINZA_ESCURO, spaceAfter=5,
            leading=14, alignment=TA_JUSTIFY),

        'bullet': ParagraphStyle('bullet',
            fontName='Helvetica', fontSize=9.5,
            textColor=CINZA_ESCURO, spaceAfter=3,
            leftIndent=18, leading=13),

        'code': ParagraphStyle('code',
            fontName='Courier', fontSize=8,
            textColor=CINZA_ESCURO, spaceAfter=6,
            backColor=colors.HexColor('#F4F4F4'),
            borderPadding=(6, 8, 6, 8),
            leading=12),

        'table_header': ParagraphStyle('table_header',
            fontName='Helvetica-Bold', fontSize=8.5,
            textColor=BRANCO, alignment=TA_CENTER),

        'table_cell': ParagraphStyle('table_cell',
            fontName='Helvetica', fontSize=8.5,
            textColor=CINZA_ESCURO, leading=12),

        'footer_note': ParagraphStyle('footer_note',
            fontName='Helvetica-Oblique', fontSize=8,
            textColor=CINZA_MEDIO, spaceAfter=4,
            alignment=TA_CENTER),
    }
    return styles


def md_inline(text):
    """Converte markdown inline básico para ReportLab markup."""
    # Bold: **texto** ou __texto__
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'__(.+?)__',     r'<b>\1</b>', text)
    # Italic: *texto* ou _texto_
    text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
    # Code inline: `texto`
    text = re.sub(r'`([^`]+)`', r'<font name="Courier" size="8">\1</font>', text)
    # Escape & < >
    text = text.replace('&', '&amp;').replace('<b>', '<b>').replace('</b>', '</b>')
    return text


def parse_markdown(md_text, styles):
    """Converte Markdown para lista de Flowables ReportLab."""
    story = []
    lines = md_text.split('\n')
    i = 0
    in_code = False
    code_lines = []
    in_table = False
    table_rows = []

    while i < len(lines):
        line = lines[i]
        raw = line.rstrip()

        # ── Bloco de código ──────────────────────────────────────────
        if raw.startswith('```'):
            if not in_code:
                in_code = True
                code_lines = []
            else:
                in_code = False
                code_text = '\n'.join(code_lines)
                story.append(Preformatted(code_text, styles['code']))
                story.append(Spacer(1, 4))
            i += 1
            continue

        if in_code:
            code_lines.append(raw)
            i += 1
            continue

        # ── Tabela Markdown ──────────────────────────────────────────
        if '|' in raw and raw.strip().startswith('|'):
            cells = [c.strip() for c in raw.strip().strip('|').split('|')]
            if all(set(c.replace('-','').replace(':','').replace(' ','')) == set() for c in cells):
                i += 1
                continue
            table_rows.append(cells)
            i += 1
            # Ler próximas linhas da tabela
            while i < len(lines) and '|' in lines[i] and lines[i].strip().startswith('|'):
                nxt = lines[i].rstrip()
                row_cells = [c.strip() for c in nxt.strip().strip('|').split('|')]
                if not all(set(c.replace('-','').replace(':','').replace(' ','')) == set() for c in row_cells):
                    table_rows.append(row_cells)
                i += 1
            # Renderizar tabela
            if table_rows:
                story += render_table(table_rows, styles)
                table_rows = []
            continue

        # ── Separador ────────────────────────────────────────────────
        if raw.strip() in ('---', '***', '___'):
            story.append(HRFlowable(width='100%', thickness=1,
                                    color=CINZA_LINHA, spaceAfter=6, spaceBefore=6))
            i += 1
            continue

        # ── Título # ─────────────────────────────────────────────────
        h_match = re.match(r'^(#{1,3})\s+(.*)', raw)
        if h_match:
            level = len(h_match.group(1))
            text = h_match.group(2).strip()
            # Remover ### e número de secção decorativos
            text = re.sub(r'^\*+|\*+$', '', text).strip()
            if level == 1:
                # Título principal — só no início
                story.append(Paragraph(md_inline(text), styles['title']))
            elif level == 2:
                story.append(Spacer(1, 6))
                story.append(Paragraph(f'  {md_inline(text)}', styles['h1']))
            else:
                story.append(Paragraph(md_inline(text), styles['h2']))
            i += 1
            continue

        # ── Bullet ───────────────────────────────────────────────────
        bullet_match = re.match(r'^(\s*[-*])\s+(.*)', raw)
        if bullet_match:
            text = bullet_match.group(2).strip()
            story.append(Paragraph(f'• {md_inline(text)}', styles['bullet']))
            i += 1
            continue

        # ── Numerado ─────────────────────────────────────────────────
        num_match = re.match(r'^\s*(\d+)\.\s+(.*)', raw)
        if num_match:
            n = num_match.group(1)
            text = num_match.group(2).strip()
            story.append(Paragraph(f'{n}. {md_inline(text)}', styles['bullet']))
            i += 1
            continue

        # ── Checkbox ─────────────────────────────────────────────────
        cb_match = re.match(r'^\s*[-*]?\s*\[([ xX])\]\s+(.*)', raw)
        if cb_match:
            checked = '✅' if cb_match.group(1).lower() == 'x' else '☐'
            text = cb_match.group(2).strip()
            story.append(Paragraph(f'{checked} {md_inline(text)}', styles['bullet']))
            i += 1
            continue

        # ── Linha em branco ─────────────────────────────────────────
        if raw.strip() == '':
            story.append(Spacer(1, 4))
            i += 1
            continue

        # ── Parágrafo normal ─────────────────────────────────────────
        if raw.strip():
            # Ignorar linhas que são só "###" título de frontmatter
            if raw.strip().startswith('**') and raw.strip().endswith('**'):
                story.append(Paragraph(md_inline(raw.strip()), styles['subtitle']))
            else:
                story.append(Paragraph(md_inline(raw.strip()), styles['body']))
        i += 1

    return story


def render_table(rows, styles):
    """Renderiza uma tabela Markdown como Table ReportLab."""
    flowables = []
    if not rows:
        return flowables

    col_count = max(len(r) for r in rows)
    # Normalizar número de colunas
    norm = []
    for r in rows:
        while len(r) < col_count:
            r.append('')
        norm.append(r[:col_count])

    # Largura das colunas distribuída proporcionalmente
    avail = PAGE_W - 3*cm
    col_w = [avail / col_count] * col_count

    # Construir dados com Paragraphs
    data = []
    for ri, row in enumerate(norm):
        if ri == 0:
            data.append([Paragraph(c, styles['table_header']) for c in row])
        else:
            data.append([Paragraph(c, styles['table_cell'])   for c in row])

    t = Table(data, colWidths=col_w, repeatRows=1)
    t.setStyle(TableStyle([
        # Cabeçalho
        ('BACKGROUND', (0,0), (-1,0), AZUL_UTFPR),
        ('TEXTCOLOR',  (0,0), (-1,0), BRANCO),
        ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0,0), (-1,0), 8.5),
        ('ALIGN',      (0,0), (-1,0), 'CENTER'),
        ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
        # Corpo
        ('FONTNAME',   (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE',   (0,1), (-1,-1), 8.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [BRANCO, AZUL_BG]),
        # Bordas
        ('GRID',       (0,0), (-1,-1), 0.4, CINZA_LINHA),
        ('BOX',        (0,0), (-1,-1), 0.8, AZUL_UTFPR),
        # Padding
        ('TOPPADDING',    (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING',   (0,0), (-1,-1), 6),
        ('RIGHTPADDING',  (0,0), (-1,-1), 6),
    ]))
    flowables.append(Spacer(1, 6))
    flowables.append(t)
    flowables.append(Spacer(1, 8))
    return flowables


def draw_cover(canvas_obj, doc):
    """Desenha a capa completa via canvas (posicionamento absoluto — sem sobreposições)."""
    canvas_obj.saveState()
    w, h = A4

    # ── Faixa superior azul escuro ──────────────────────────────────────────
    canvas_obj.setFillColor(AZUL_UTFPR)
    canvas_obj.rect(0, h - 5.5*cm, w, 5.5*cm, fill=True, stroke=False)

    # ── Sigla UTFPR ─────────────────────────────────────────────────────────
    canvas_obj.setFillColor(BRANCO)
    canvas_obj.setFont('Helvetica-Bold', 42)
    canvas_obj.drawCentredString(w/2, h - 2.5*cm, 'UTFPR')

    # ── Nome completo da universidade ────────────────────────────────────────
    canvas_obj.setFont('Helvetica', 11)
    canvas_obj.drawCentredString(w/2, h - 3.5*cm,
        'Universidade Tecnológica Federal do Paraná')

    # ── Subtítulo da unidade ─────────────────────────────────────────────────
    canvas_obj.setFont('Helvetica-Oblique', 9)
    canvas_obj.setFillColor(colors.HexColor('#B0C8E8'))
    canvas_obj.drawCentredString(w/2, h - 4.4*cm,
        'Pró-Reitoria de Pesquisa e Pós-Graduação — PROPPG')

    # ── Linha divisória decorativa ────────────────────────────────────────────
    canvas_obj.setStrokeColor(colors.HexColor('#B0C8E8'))
    canvas_obj.setLineWidth(1)
    canvas_obj.line(2*cm, h - 5.2*cm, w - 2*cm, h - 5.2*cm)

    # ── Bloco central — nome do sistema ──────────────────────────────────────
    canvas_obj.setFillColor(AZUL_CLARO)
    canvas_obj.setFont('Helvetica-Bold', 16)
    canvas_obj.drawCentredString(w/2, h - 8.0*cm, 'Sistema Arandú')

    # ── Linha separadora fina ─────────────────────────────────────────────────
    canvas_obj.setStrokeColor(AZUL_CLARO)
    canvas_obj.setLineWidth(0.5)
    canvas_obj.line(w/2 - 5*cm, h - 8.6*cm, w/2 + 5*cm, h - 8.6*cm)

    # ── Título do documento ───────────────────────────────────────────────────
    canvas_obj.setFillColor(AZUL_UTFPR)
    canvas_obj.setFont('Helvetica-Bold', 28)
    canvas_obj.drawCentredString(w/2, h - 11.5*cm, doc._cover_title)

    # ── Subtítulo do documento ────────────────────────────────────────────────
    canvas_obj.setFillColor(CINZA_MEDIO)
    canvas_obj.setFont('Helvetica', 12)
    canvas_obj.drawCentredString(w/2, h - 13.2*cm, doc._cover_subtitle)

    # ── Linha separadora central ──────────────────────────────────────────────
    canvas_obj.setStrokeColor(AZUL_UTFPR)
    canvas_obj.setLineWidth(1.5)
    canvas_obj.line(3*cm, h - 14.5*cm, w - 3*cm, h - 14.5*cm)

    # ── Bloco de metadados ────────────────────────────────────────────────────
    meta = [
        ('Criador',       'Higo Figueiredo dos Santos'),
        ('Instituição',   'PROPPG / UTFPR'),
        ('Versão',        '26.x'),
        ('Data',          'Março 2026'),
    ]
    y_meta = h - 17.0*cm
    row_h  = 1.2*cm
    col1_x = 2.5*cm
    col2_x = 7.5*cm

    for idx, (label, value) in enumerate(meta):
        # Fundo alternado
        bg = AZUL_BG if idx % 2 == 0 else BRANCO
        canvas_obj.setFillColor(bg)
        canvas_obj.rect(col1_x - 0.3*cm, y_meta - 0.25*cm,
                        w - 2*(col1_x - 0.3*cm), row_h,
                        fill=True, stroke=False)
        # Label
        canvas_obj.setFillColor(AZUL_UTFPR)
        canvas_obj.setFont('Helvetica-Bold', 10)
        canvas_obj.drawString(col1_x, y_meta + 0.3*cm, label)
        # Valor
        canvas_obj.setFillColor(CINZA_ESCURO)
        canvas_obj.setFont('Helvetica', 10)
        canvas_obj.drawString(col2_x, y_meta + 0.3*cm, value)
        y_meta -= row_h

    # ── Rodapé da capa ────────────────────────────────────────────────────────
    canvas_obj.setFillColor(AZUL_UTFPR)
    canvas_obj.rect(0, 0, w, 1.5*cm, fill=True, stroke=False)
    canvas_obj.setFillColor(BRANCO)
    canvas_obj.setFont('Helvetica', 8)
    canvas_obj.drawCentredString(w/2, 0.55*cm,
        'Documento gerado para o processo de Registro de Software — AGINT/UTFPR')

    canvas_obj.restoreState()


def cover_page(doc_title, subtitle, styles):
    """Retorna apenas um PageBreak — a capa é desenhada pelo onFirstPage=draw_cover."""
    return [PageBreak()]


def generate_pdf(md_path, pdf_path, doc_title, subtitle):
    """Função principal de geração do PDF."""
    styles = build_styles()

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=1.5*cm,
        rightMargin=1.5*cm,
        topMargin=2.5*cm,
        bottomMargin=2.0*cm,
        title=doc_title,
        author='Higo Figueiredo dos Santos',
        subject='Sistema Arandú — PROPPG/UTFPR',
    )

    # Passar atributos da capa para o canvas handler aceder
    doc._cover_title    = doc_title
    doc._cover_subtitle = subtitle

    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    story = []
    story += cover_page(doc_title, subtitle, styles)   # PageBreak da capa
    story += parse_markdown(md_text, styles)           # Conteúdo real

    # Capa: draw_cover (canvas directo) | Resto: header_footer normal
    doc.build(story, onFirstPage=draw_cover, onLaterPages=header_footer)
    print(f'✅ PDF gerado: {pdf_path}')


# ─── Execução ────────────────────────────────────────────────────────────────

BASE = r'C:\Users\higosantos\Documents\gestao_editais\gestao_editais_novo'

generate_pdf(
    md_path  = os.path.join(BASE, 'DOCUMENTACAO.md'),
    pdf_path = os.path.join(BASE, 'docs', 'Arandu_Documentacao_Tecnica.pdf'),
    doc_title = 'Documentação Técnica',
    subtitle  = 'Arquitectura, Módulos, Segurança e Infraestrutura',
)

generate_pdf(
    md_path  = os.path.join(BASE, 'COMO_USAR.md'),
    pdf_path = os.path.join(BASE, 'docs', 'Arandu_Como_Usar.pdf'),
    doc_title = 'Manual de Uso',
    subtitle  = 'Instalação, Configuração e Guia do Utilizador',
)
