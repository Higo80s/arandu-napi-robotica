"""
Gera PDF do relatório de auditoria do sistema Arandu.
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                  TableStyle, HRFlowable, PageBreak)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
import os

OUTPUT = os.path.join(os.path.dirname(__file__), '..', 'docs', 'auditoria_sistema_arandu.pdf')

doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=A4,
    rightMargin=2*cm,
    leftMargin=2*cm,
    topMargin=2*cm,
    bottomMargin=2*cm
)

styles = getSampleStyleSheet()

# Custom styles
title_style = ParagraphStyle('Title2', parent=styles['Title'],
    fontSize=18, textColor=colors.HexColor('#002e6d'), spaceAfter=6)
subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'],
    fontSize=11, textColor=colors.HexColor('#555555'), spaceAfter=12, alignment=TA_CENTER)
h1_style = ParagraphStyle('H1', parent=styles['Heading1'],
    fontSize=13, textColor=colors.HexColor('#002e6d'), spaceBefore=16, spaceAfter=6,
    borderPad=4, backColor=colors.HexColor('#f0f4ff'))
h2_style = ParagraphStyle('H2', parent=styles['Heading2'],
    fontSize=11, textColor=colors.HexColor('#1d4ed8'), spaceBefore=12, spaceAfter=4)
body_style = ParagraphStyle('Body2', parent=styles['Normal'],
    fontSize=9, leading=14, spaceAfter=4)
note_style = ParagraphStyle('Note', parent=styles['Normal'],
    fontSize=8, textColor=colors.HexColor('#555555'), italic=True, spaceAfter=6)
alert_style = ParagraphStyle('Alert', parent=styles['Normal'],
    fontSize=9, textColor=colors.HexColor('#991b1b'), backColor=colors.HexColor('#fff1f2'),
    borderPad=6, spaceAfter=6)

def tbl_style(header_color='#002e6d'):
    return TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(header_color)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#d1d5db')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ])

story = []

# ── CAPA
story.append(Spacer(1, 2*cm))
story.append(Paragraph("RELATÓRIO DE AUDITORIA TÉCNICA", title_style))
story.append(Paragraph("Sistema Arandu — Gestão de Editais e Bolsas", subtitle_style))
story.append(Paragraph("UTFPR / PROPPG &nbsp;|&nbsp; 27/02/2026 &nbsp;|&nbsp; Versão V25+", subtitle_style))
story.append(Spacer(1, 0.5*cm))
story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#002e6d')))
story.append(Spacer(1, 1*cm))

# ── 1. VISÃO GERAL
story.append(Paragraph("1. VISÃO GERAL DO SISTEMA", h1_style))
story.append(Paragraph(
    "O <b>Arandu</b> (nome Guarani para 'conhecimento/sabedoria') é um sistema web institucional "
    "desenvolvido para a Diretoria de Pesquisa e Pós-Graduação (PROPPG) da UTFPR, dedicado ao "
    "<b>gerenciamento de editais de fomento, bolsas de pesquisa e acompanhamento financeiro</b> "
    "de bolsistas e residentes (Pós-Doutores).", body_style))

kpi_data = [
    ['Indicador', 'Valor'],
    ['Editais cadastrados', '25'],
    ['Modalidades de bolsa', '30'],
    ['Bolsistas (total, histórico)', '747'],
    ['Bolsistas ativos', '521'],
    ['Residentes / Pós-Doutores', '119'],
    ['Programas de Pós-Graduação', '109'],
    ['Campi cobertos', '14'],
    ['Rodadas de Seleção', '5'],
    ['Rotas HTTP registradas', '117'],
]
t = Table(kpi_data, colWidths=[10*cm, 5*cm])
t.setStyle(tbl_style())
story.append(t)
story.append(Spacer(1, 0.5*cm))

# ── 2. ARQUITETURA
story.append(Paragraph("2. ARQUITETURA TÉCNICA", h1_style))
stack_data = [
    ['Camada', 'Tecnologia'],
    ['Backend', 'Python 3.x + Flask'],
    ['ORM', 'SQLAlchemy'],
    ['Banco de Dados', 'PostgreSQL (produção) / SQLite (desenvolvimento)'],
    ['Servidor WSGI', 'Waitress (produção local)'],
    ['Frontend', 'HTML5 / CSS3 / JavaScript Vanilla'],
    ['Autenticação', 'Flask-Login + RBAC (admin/regular)'],
    ['Segurança CSRF', 'Flask-WTF CSRFProtect'],
    ['Rate Limiting', 'Flask-Limiter'],
    ['Headers de Segurança', 'Flask-Talisman (CSP, HSTS, X-Frame)'],
    ['E-mail', 'Flask-Mail'],
    ['Containerização', 'Docker + docker-compose'],
    ['Deploy alternativo', 'PythonAnywhere / Gunicorn (wsgi.py)'],
]
t = Table(stack_data, colWidths=[7*cm, 9*cm])
t.setStyle(tbl_style())
story.append(t)
story.append(Spacer(1, 0.5*cm))

# ── 3. MÓDULOS
story.append(Paragraph("3. MÓDULOS DO SISTEMA", h1_style))

story.append(Paragraph("3.1  Blueprints Registrados", h2_style))
bp_data = [
    ['Blueprint', 'Arquivo', 'Função Principal', 'Tam.'],
    ['auth', 'blueprints/auth.py', 'Login, logout, 2FA, troca de senha', '8 KB'],
    ['editais', 'blueprints/editais.py', 'CRUD de Editais e Modalidades', '12 KB'],
    ['bolsistas', 'blueprints/bolsistas.py', 'CRUD completo de bolsistas', '34 KB'],
    ['posdoc', 'blueprints/posdoc.py', 'Residentes / Pós-Doutores', '24 KB'],
    ['proap', 'blueprints/proap.py', 'Apoio PROAP, repasses financeiros', '37 KB'],
    ['admin_users', 'blueprints/admin_users.py', 'Gestão de usuários do sistema', '4 KB'],
    ['api_utils', 'blueprints/api_utils.py', 'Utilitários de API (CSRF refresh)', '1 KB'],
    ['internacionalizacao', 'blueprints/internacionalizacao.py', 'Mobilidade internacional', '5 KB'],
    ['profissionais', 'blueprints/profissionais.py', 'Programas profissionais', '6 KB'],
]
t = Table(bp_data, colWidths=[3.5*cm, 4*cm, 6*cm, 1.5*cm])
t.setStyle(tbl_style())
story.append(t)
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("3.2  Módulos de Relatórios", h2_style))
rel_data = [
    ['Módulo', 'Arquivo', 'Função'],
    ['reports_bp', 'reports_bp.py', 'Relatórios financeiros por Edital, impressão, Excel, bulk print (51 KB)'],
    ['reports_strategic', 'reports_strategic.py', 'Dashboard estratégico / BI (26 KB)'],
    ['dashboard_bp', 'dashboard_bp.py', 'Painel principal com KPIs (16 KB)'],
    ['reports (legado)', 'reports.py', 'Relatórios consolidados legados (35 KB)'],
]
t = Table(rel_data, colWidths=[4*cm, 4.5*cm, 7.5*cm])
t.setStyle(tbl_style())
story.append(t)

story.append(PageBreak())

# ── 4. BANCO DE DADOS
story.append(Paragraph("4. BANCO DE DADOS", h1_style))
db_data = [
    ['Item', 'Status', 'Observações'],
    ['Normalização', '✅ Boa', 'Tabelas Campus e Programa evitam inconsistências de digitação'],
    ['Relacionamentos', '✅ FKs configuradas', 'Cascade delete aplicado onde adequado'],
    ['Índices', '⚠️ Parcial', 'CPF indexado, mas queries complexas sem índice composto'],
    ['Integridade', '⚠️ Atenção', 'Modalidades com vagas=999 (placeholder) exigem limpeza'],
    ['Histórico', '✅ Implementado', 'BolsaHistorico registra alterações de bolsa'],
    ['SQLite local', '⚠️ Obsoleto', 'Versões desatualizadas de .db encontradas na raiz do projeto'],
]
t = Table(db_data, colWidths=[4*cm, 3*cm, 9*cm])
t.setStyle(tbl_style())
story.append(t)

# ── 5. SEGURANÇA
story.append(Paragraph("5. SEGURANÇA", h1_style))
sec_data = [
    ['Dispositivo', 'Status', 'Observações'],
    ['CSRF Protection', '✅ Ativo', 'Flask-WTF global via csrf.init_app(app)'],
    ['Rate Limiting', '✅ Ativo', '200/dia, 50/hora via Flask-Limiter'],
    ['RBAC (Roles)', '✅ Implementado', 'admin / regular via @admin_required'],
    ['2FA (TOTP)', '✅ Disponível', 'Blueprint auth com suporte a autenticador'],
    ['Headers HTTP', '✅ Flask-Talisman', 'CSP, HSTS, X-Frame-Options'],
    ['Session Timeout', '✅ 4 horas', 'PERMANENT_SESSION_LIFETIME configurado'],
    ['CORS', '✅ Restrito', 'Apenas origens autorizadas'],
    ['Criptografia de dados', '⚠️ Parcial', 'encryption.py existe mas aplicação incompleta nos modelos'],
    ['Senhas em .env', '✅ Correto', 'Variáveis de ambiente, não hard-coded'],
    ['SECRET_KEY', '🔴 CRÍTICO', 'os.urandom(24) sem persist — invalida sessões ao reiniciar servidor'],
]
t = Table(sec_data, colWidths=[4*cm, 3*cm, 9*cm])
t.setStyle(tbl_style())
story.append(t)

# ── 6. BACKUP
story.append(Paragraph("6. SISTEMA DE BACKUP", h1_style))
bk_data = [
    ['Item', 'Status'],
    ['Lógica de backup implementada', '✅ Sim'],
    ['pg_dump discovery automático (Windows)', '✅ Sim'],
    ['JSON fallback (escrita em partes)', '✅ Sim'],
    ['Cópia para nuvem (Google Drive / OneDrive)', '✅ Auto-detectado'],
    ['Backup agendado automático', '❌ Não implementado'],
    ['Teste de restore documentado', '❌ Ausente'],
]
t = Table(bk_data, colWidths=[12*cm, 4*cm])
t.setStyle(tbl_style())
story.append(t)

story.append(PageBreak())

# ── 7. PORTABILIDADE
story.append(Paragraph("7. ADAPTABILIDADE PARA OUTRAS INSTITUIÇÕES", h1_style))
story.append(Paragraph(
    "O sistema pode ser adaptado para outra universidade com <b>esforço moderado (3–5 dias úteis)</b> "
    "para outra IFES brasileira. Os pontos que necessitam parametrização:", body_style))
port_data = [
    ['Item', 'Situação'],
    ['Nome UTFPR hardcoded nos relatórios', '⚠️ Parametrizável — exige alteração'],
    ['Campi específicos da UTFPR (14)', '⚠️ Dados iniciais via script — reconfiguráveis'],
    ['Agências de fomento (CAPES, CNPq)', '✅ Genérico'],
    ['Lógica de bolsas / modalidades', '✅ Genérica (baseada em configuração)'],
    ['Idioma', '⚠️ Apenas português (sem i18n)'],
    ['Branding / Logo PROPPG', '⚠️ Hardcoded no layout base'],
]
t = Table(port_data, colWidths=[10*cm, 6*cm])
t.setStyle(tbl_style())
story.append(t)

# ── 8. PARECERES CRÍTICOS
story.append(Paragraph("8. PARECERES CRÍTICOS DOS ESPECIALISTAS", h1_style))

story.append(Paragraph("🧑‍💻  Engenharia de Software", h2_style))
issues_eng = [
    "1. app.py monolítico com 3.837 linhas — dificulta testes, manutenção e colaboração.",
    "2. Ausência de testes automatizados efetivos — cobertura estimada < 20%.",
    "3. Duplicação nos módulos de relatórios (4 arquivos com sobreposição de responsabilidade).",
    "4. Sem Flask-Migrate (Alembic) — alterações de schema são manuais e arriscadas.",
    "5. SECRET_KEY = os.urandom(24) — nova chave a cada restart invalida sessões de todos os usuários.",
]
for i in issues_eng:
    story.append(Paragraph(i, body_style))

story.append(Paragraph("📊  Ciência de Dados", h2_style))
issues_data = [
    "1. KPIs calculados em runtime sem cache — queries complexas degradam com volume.",
    "2. Dados históricos ricos (747 bolsistas) não explorados para análises preditivas.",
    "3. Inconsistência de dados — bolsistas com modalidade_id=NULL e vagas=999 prejudicam relatórios.",
    "4. Sem integração com ferramentas BI (Power BI, Metabase) — dados presos no sistema.",
]
for i in issues_data:
    story.append(Paragraph(i, body_style))

story.append(Paragraph("🎨  Design e Usabilidade (UX/UI)", h2_style))
issues_ux = [
    "1. Navegação inconsistente entre páginas — topbar não padronizado.",
    "2. Formulário de bolsista complexo — dezenas de campos sem agrupamento visual.",
    "3. Mensagens de erro genéricas — 'Sessão Expirada' aparece em erros de banco de dados.",
    "4. Responsividade limitada — sistema desenhado para desktop; mobile não suportado.",
    "5. Acessibilidade — ausência de atributos ARIA e suporte a leitores de tela.",
]
for i in issues_ux:
    story.append(Paragraph(i, body_style))

story.append(PageBreak())

# ── 9. PLANEJAMENTO
story.append(Paragraph("9. PLANEJAMENTO ESTRATÉGICO", h1_style))

story.append(Paragraph("🔴  Críticos — Resolver Imediatamente", h2_style))
crit_data = [
    ['#', 'Problema', 'Solução', 'Prazo'],
    ['1', 'SECRET_KEY regenerada a cada restart', 'Definir SECRET_KEY fixo e forte no .env', '1h'],
    ['2', 'Template caching (auto_reload=False)', 'Adicionar app.jinja_env.auto_reload = True', '1h'],
    ['3', 'Bolsistas vinculados à modalidade errada', 'Script de migração + validação na inclusão', '1 dia'],
    ['4', 'Erros de BD mascarados como "Sessão Expirada"', 'Refatorar error handlers (400 vs 500)', '1 dia'],
]
t = Table(crit_data, colWidths=[0.8*cm, 5*cm, 7*cm, 2*cm])
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc2626')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 8),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fff1f2')]),
    ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#d1d5db')),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('LEFTPADDING', (0, 0), (-1, -1), 5),
    ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ('TOPPADDING', (0, 0), (-1, -1), 4),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
]))
story.append(t)

story.append(Spacer(1, 0.4*cm))
story.append(Paragraph("🟡  Importantes — 30 dias", h2_style))
imp_data = [
    ['#', 'Problema', 'Solução'],
    ['5', 'app.py monolítico (3.837 linhas)', 'Extrair rotas em blueprints (mínimo 5 novos módulos)'],
    ['6', 'Sem backup automático agendado', 'Integrar APScheduler ou tarefa cron'],
    ['7', 'Sem Flask-Migrate', 'Migrar para Flask-Migrate para gestão de schema'],
    ['8', 'Testes automatizados < 20%', 'Implementar suite pytest com dados fixtures'],
    ['9', 'Relatórios duplicados (4 módulos)', 'Consolidar em reports_bp.py + dashboard_bp.py'],
]
t = Table(imp_data, colWidths=[0.8*cm, 5*cm, 9.2*cm])
t.setStyle(tbl_style('#d97706'))
story.append(t)

story.append(Spacer(1, 0.4*cm))
story.append(Paragraph("🟢  Estratégicos — 60–90 dias", h2_style))
strat_data = [
    ['#', 'Melhoria', 'Benefício'],
    ['10', 'Cache Redis para dashboard', 'Performance 10x em KPIs complexos'],
    ['11', 'API REST + OpenAPI/Swagger', 'Integração com Power BI e outros sistemas'],
    ['12', 'Internacionalização (i18n/Babel)', 'Adaptabilidade para outras universidades'],
    ['13', 'Dashboard preditivo (scikit-learn)', 'Alertas de evasão, projeção de vagas'],
    ['14', 'Responsividade mobile', 'Acesso pelo smartphone para coordenadores'],
    ['15', 'Pipeline CI/CD (GitHub Actions)', 'Deploy automatizado com testes'],
    ['16', 'Parametrizar identidade institucional', 'Sistema white-label para outras IFES'],
    ['17', 'Auditoria WCAG 2.1', 'Conformidade legal e inclusão digital'],
]
t = Table(strat_data, colWidths=[0.8*cm, 6.5*cm, 7.7*cm])
t.setStyle(tbl_style('#047857'))
story.append(t)

# ── 10. AVALIAÇÃO GERAL
story.append(PageBreak())
story.append(Paragraph("10. AVALIAÇÃO GERAL", h1_style))
aval_data = [
    ['Dimensão', 'Nota', 'Comentário'],
    ['Funcionalidade', '8 / 10', 'Cobre bem os processos-chave de gestão de editais'],
    ['Segurança', '7 / 10', 'Controles básicos presentes, mas SECRET_KEY e criptografia incompleta'],
    ['Manutenibilidade', '5 / 10', 'app.py monolítico é o maior obstáculo a longo prazo'],
    ['Performance', '6 / 10', 'Sem cache — queries complexas degradam com volume crescente'],
    ['Usabilidade', '6 / 10', 'Funcional, mas com curva de aprendizado elevada'],
    ['Qualidade de Dados', '7 / 10', 'Modelo bem estruturado, com inconsistências pontuais'],
    ['Backup/Recuperação', '6 / 10', 'Implementado, mas sem automação e sem teste de restore'],
    ['Portabilidade', '6 / 10', 'UTFPR hardcoded em vários pontos do sistema'],
]
t = Table(aval_data, colWidths=[5*cm, 2.5*cm, 8.5*cm])
t.setStyle(tbl_style())
story.append(t)

story.append(Spacer(1, 1*cm))
story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#002e6d')))
story.append(Spacer(1, 0.3*cm))
story.append(Paragraph(
    "<b>Conclusão:</b> O sistema está <b>operacional e funcional</b> para seu propósito. "
    "A prioridade imediata é corrigir os problemas críticos de infraestrutura (SECRET_KEY, template reload) "
    "e iniciar a refatoração do app.py em blueprints menores para garantir sustentabilidade a longo prazo. "
    "O sistema tem potencial para ser adaptado para uso em outras IFES brasileiras com esforço moderado.",
    body_style))

story.append(Spacer(1, 0.5*cm))
story.append(Paragraph("Emitido por: IA Antigravity | Sistema Arandu — UTFPR/PROPPG | 27/02/2026", note_style))

doc.build(story)
print(f"PDF gerado em: {os.path.abspath(OUTPUT)}")
