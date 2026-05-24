"""
MÓDULO DE RELATÓRIOS (BLUEPRINT)
================================
Lógica integradas para geração de relatórios PDF e Excel.
"""

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar
import io
from decimal import Decimal
import traceback
import os
from flask import Blueprint, render_template, send_file, request, flash, redirect, url_for, current_app
from flask_login import login_required
from extensions import db
from models import Edital, Bolsista, Acompanhamento, User, ProgramaAcademico, Campus
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Define Blueprint
reports_bp = Blueprint('reports', __name__)

# NOTA: O filtro 'format_currency' deve ser registrado no app.py principal

@reports_bp.route('/reports')
@login_required
def index():
    editais = Edital.query.all()
    return render_template('relatorios/index.html', editais=editais)

# --- 1. RELATÓRIO INDIVIDUAL (DISCENTE/RESIDENTE) ---

@reports_bp.route('/reports/student/<int:id>/pdf')
def student_report_pdf(id):
    """
    Gera relatório HTML (pdf-friendly) para impressão.
    """
    bolsista = Bolsista.query.get(id)
    tipo = "Discente"
    
    if not bolsista:
        return "Bolsista não encontrado", 404

    # Coletar Extrato
    extrato = []
    total_pago = Decimal('0')
    
    if tipo == "Discente":
        pagamentos = Acompanhamento.query.filter_by(bolsista_id=id).order_by(Acompanhamento.referencia_mes).all()
        valor_mensal = bolsista.modalidade.valor_mensal if bolsista.modalidade else Decimal('0')
        
        for p in pagamentos:
            valor = valor_mensal 
            total_pago += valor
            extrato.append({
                'mes': p.referencia_mes,
                'parcela': p.parcela,
                'valor': valor,
                'obs': p.observacoes
            })
    
    # Se Total Pago for 0, usar Estimativa
    is_estimado = False
    if total_pago == Decimal('0'):
        hoje = date.today()
        if bolsista.data_inicio_bolsa and bolsista.data_fim_bolsa:
            cutoff = min(hoje, bolsista.data_fim_bolsa)
            if cutoff > bolsista.data_inicio_bolsa:
                diff = relativedelta(cutoff, bolsista.data_inicio_bolsa)
                meses_estimados = diff.years * 12 + diff.months
                
                if meses_estimados < 0: meses_estimados = 0
                if meses_estimados > bolsista.meses_duracao: meses_estimados = bolsista.meses_duracao
                
                valor_mensal = bolsista.modalidade.valor_mensal if bolsista.modalidade else Decimal('0')
                total_pago = Decimal(str(meses_estimados)) * valor_mensal
                is_estimado = True
                
                # Gerar Extrato Estimado
                start_date = bolsista.data_inicio_bolsa
                for i in range(meses_estimados):
                    ref_date = start_date + relativedelta(months=i)
                    ref_mes = ref_date.strftime("%Y-%m")
                    
                    extrato.append({
                        'mes': ref_mes,
                        'parcela': i + 1,
                        'valor': valor_mensal,
                        'obs': 'Valor Estimado (Automático)'
                    })

    # Cálculos Previstos
    valor_mensal_atual = bolsista.modalidade.valor_mensal if bolsista.modalidade else Decimal('0')
    total_previsto = valor_mensal_atual * Decimal(str(bolsista.meses_duracao))
    
    saldo = total_previsto - total_pago

    # Renderiza template na pasta 'reports'
    return render_template('reports/report_student.html', 
                           bolsista=bolsista,
                           tipo=tipo,
                           extrato=extrato,
                           total_pago=total_pago,
                           total_previsto=total_previsto,
                           saldo=saldo,
                           is_estimado=is_estimado,
                           hoje=date.today())


# --- 2. RELATÓRIO DE EDITAL (RECURSOS PRÓPRIOS) ---

@reports_bp.route('/reports/edital/<int:id>/excel')
def edital_report_excel(id):
    edital = Edital.query.get_or_404(id)
    
    wb = Workbook()
    ws = wb.active
    # Sanitizar titulo da aba (Excel proíbe / \ * ? [ ]) e limita a 31 caracteres
    safe_num = str(edital.numero).replace('/', '-').replace('\\', '-')
    sheet_title = f"Edital {safe_num}"
    ws.title = sheet_title[:31]
    
    headers = [
        "Nome", "CPF", "Programa", "Modalidade", "Início", "Fim", 
        "Duração (Meses)", "Valor Mensal", 
        "Parcelas Pagas (Qtd)", "Total Pago (R$)", 
        "Total Previsto (R$)", "Saldo a Pagar (R$)"
    ]
    ws.append(headers)
    
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="4F81BD", fill_type="solid")
    
    total_geral_pago = Decimal('0')
    total_geral_previsto = Decimal('0')
    
    # 1. Processar Bolsistas
    for b in edital.bolsistas:
        if not b.ativo: continue 
        
        qtd_parcelas_pagas = len(b.acompanhamentos)
        valor_mensal = b.modalidade.valor_mensal if b.modalidade else Decimal('0')
        
        obs_estimado = ""
        
        if qtd_parcelas_pagas > 0:
            total_pago = Decimal(str(qtd_parcelas_pagas)) * valor_mensal
        else:
            # Fallback Estimativa
            hoje = date.today()
            if b.data_inicio_bolsa and b.data_fim_bolsa:
                cutoff = min(hoje, b.data_fim_bolsa)
                if cutoff > b.data_inicio_bolsa:
                    diff = relativedelta(cutoff, b.data_inicio_bolsa)
                    qtd_parcelas_pagas = diff.years * 12 + diff.months
                    if qtd_parcelas_pagas < 0: qtd_parcelas_pagas = 0
                    if qtd_parcelas_pagas > b.meses_duracao: qtd_parcelas_pagas = b.meses_duracao
                else:
                    qtd_parcelas_pagas = 0
            else:
                qtd_parcelas_pagas = 0
            
            total_pago = Decimal(str(qtd_parcelas_pagas)) * valor_mensal
            if qtd_parcelas_pagas > 0:
                obs_estimado = " (Est)"

        total_previsto = Decimal(str(b.meses_duracao)) * valor_mensal
        saldo = total_previsto - total_pago
        
        total_geral_pago += total_pago
        total_geral_previsto += total_previsto
        
        programa_nome = b.programa_link.sigla_programa if b.programa_link else (b.programa or "-")
        modalidade_nome = b.modalidade.nivel if b.modalidade else "-"

        ws.append([
            b.nome,
            b.cpf,
            programa_nome,
            modalidade_nome,
            b.data_inicio_bolsa,
            b.data_fim_bolsa,
            b.meses_duracao,
            valor_mensal,
            f"{qtd_parcelas_pagas}{obs_estimado}",
            total_pago,
            total_previsto,
            saldo
        ])

    # Totais

    # Totais
    last_row = ws.max_row + 1
    total_geral_saldo = total_geral_previsto - total_geral_pago
    
    ws.cell(row=last_row, column=9, value="TOTAL GERAL").font = Font(bold=True)
    ws.cell(row=last_row, column=10, value=total_geral_pago).font = Font(bold=True)
    ws.cell(row=last_row, column=11, value=total_geral_previsto).font = Font(bold=True)
    ws.cell(row=last_row, column=12, value=total_geral_saldo).font = Font(bold=True)
    
    for col in range(1, 13):
        ws.column_dimensions[get_column_letter(col)].width = 15
    ws.column_dimensions['A'].width = 30
    
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    return send_file(output, as_attachment=True, download_name=f"relatorio_financeiro_{edital.numero}.xlsx")

# --- 3. RELATÓRIO DE EDITAL (IMPRESSÃO HTML) ---
@reports_bp.route('/reports/edital/<int:id>/print')
def edital_report_print(id):
    """
    Gera relatório HTML amigável para impressão (Substitui PDF complexo).
    """
    edital = Edital.query.get_or_404(id)
    
    items = []
    total_geral_pago = Decimal('0')
    total_geral_previsto = Decimal('0')
    
    # 1. Bolsistas
    for b in edital.bolsistas:
        if not b.ativo: continue
        
        valor_mensal = b.modalidade.valor_mensal if b.modalidade else Decimal('0')
        qtd_parcelas_pagas = len(b.acompanhamentos)
        
        # Lógica Estimativa (se sem acompanhamentos)
        is_estimado = False
        if qtd_parcelas_pagas == 0 and b.data_inicio_bolsa and b.data_fim_bolsa:
            hoje = date.today()
            cutoff = min(hoje, b.data_fim_bolsa)
            if cutoff > b.data_inicio_bolsa:
                diff = relativedelta(cutoff, b.data_inicio_bolsa)
                qtd_parcelas_pagas = diff.years * 12 + diff.months
                if qtd_parcelas_pagas > b.meses_duracao: qtd_parcelas_pagas = b.meses_duracao
                if qtd_parcelas_pagas < 0: qtd_parcelas_pagas = 0
                is_estimado = True

        total_pago = Decimal(str(qtd_parcelas_pagas)) * valor_mensal
        total_prev = Decimal(str(b.meses_duracao)) * valor_mensal
        saldo = total_prev - total_pago
        
        total_geral_pago += total_pago
        total_geral_previsto += total_prev
        
        # Helper para dados do programa
        campus_sigla = "-"
        prog_codigo = "-"
        prog_nome = "-"
        
        if b.programa_link:
            prog_nome = b.programa_link.nome_programa
            prog_codigo = b.programa_link.codigo_programa or "-"
            if b.programa_link.campus:
                campus_sigla = b.programa_link.campus.sigla_campus
        elif b.programa:
            prog_nome = b.programa
        
        items.append({
            'nome': b.nome,
            'cpf': b.cpf,
            'instituicao': b.instituicao or (b.programa_link.campus.sigla_campus if b.programa_link else (b.campus_sigla or b.campus or "-")),
            'tipo': b.modalidade.nivel if b.modalidade else 'Bolsista',
            'inicio': b.data_inicio_bolsa,
            'fim': b.data_fim_bolsa,
            'valor': valor_mensal,
            'pagos': qtd_parcelas_pagas,
            'total_pago': total_pago,
            'total_prev': total_prev,
            'saldo': saldo,
            'is_estimado': is_estimado
        })
        
    saldo_geral = total_geral_previsto - total_geral_pago
    
    return render_template('reports/print_edital.html',
                           edital=edital,
                           items=items,
                           total_pago=total_geral_pago,
                           total_previsto=total_geral_previsto,
                           saldo_geral=saldo_geral,
                           hoje=date.today())

# --- 4. RELATÓRIO INTEGRADO (DATA SCIENCE) ---

@reports_bp.route('/reports/integrated/pdf')
def integrated_report_pdf():
    """
    Gera relatório integrado com insights de Data Science.
    """
    # Filter Active Editais (Active logic: Not finalized and Not expired)
    all_editais = Edital.query.all()
    active_editais = []
    
    # Logic matching dashboard active criteria
    for e in all_editais:
        is_expired = False
        if e.data_fim and e.data_fim < date.today():
             is_expired = True
        
        if not e.prestacao_contas and not is_expired:
            active_editais.append(e)

    stats = {
        'total_ofertadas': 0,
        'total_ativas': 0,
        'total_ociosas': 0,
        'taxa_ocupacao': Decimal('0'),
        'por_fonte': {
            'NAPI/FUNTEF': {'ofertadas': 0, 'ativas': 0, 'ociosas': 0, 'taxa': 0},
            'CNPq': {'ofertadas': 0, 'ativas': 0, 'ociosas': 0, 'taxa': 0},
            'Araucária': {'ofertadas': 0, 'ativas': 0, 'ociosas': 0, 'taxa': 0},
            'Próprios': {'ofertadas': 0, 'ativas': 0, 'ociosas': 0, 'taxa': 0},
            'Outros': {'ofertadas': 0, 'ativas': 0, 'ociosas': 0, 'taxa': 0}
        },
        'por_nivel': {'mestrado': 0, 'doutorado': 0, 'posdoc': 0},
        'editais': [],
        'programas_ociosos_capes': set()
    }
    
    for e in active_editais:
        # 1. Classification
        titulo = (e.descricao or "").upper()
        fonte = 'Outros'
        if 'FUNTEF' in titulo or 'NAPI' in titulo or 'DS' in titulo or '14' in str(e.numero): fonte = 'NAPI/FUNTEF'
        elif 'CNPQ' in titulo: fonte = 'CNPq'
        elif 'ARAUC' in titulo or 'FUNDAÇÃO' in titulo: fonte = 'Araucária'
        elif 'PROPR' in titulo or 'IES' in titulo or '13' in str(e.numero): fonte = 'Próprios'
        
        # 2. Metrics
        vagas = sum(m.vagas for m in e.modalidades)
        
        ativos_count = 0
        niveis_set = set()
        
        # Count Active Bolsistas (True OR Finalizando)
        for b in e.bolsistas:
            if b.ativo or b.motivo_desligamento == 'Finalizando':
                ativos_count += 1
                modalidade_nome = b.modalidade.nivel if b.modalidade else ""
                if 'MESTRADO' in modalidade_nome.upper(): stats['por_nivel']['mestrado'] += 1
                elif 'DOUTORADO' in modalidade_nome.upper(): stats['por_nivel']['doutorado'] += 1

        # residents logic removed (blueprint decommissioning)
            
        # Levels from Modality
        for m in e.modalidades:
            if 'MESTRADO' in m.nivel.upper(): niveis_set.add("Mestrado")
            if 'DOUTORADO' in m.nivel.upper(): niveis_set.add("Doutorado")
            if 'POS' in m.nivel.upper(): niveis_set.add("Pós-Doc")

        ociosas = vagas - ativos_count
        if ociosas < 0: ociosas = 0
        
        # 3. Aggregate
        stats['total_ofertadas'] += vagas
        stats['total_ativas'] += ativos_count
        stats['total_ociosas'] += ociosas
        
        stats['por_fonte'][fonte]['ofertadas'] += vagas
        stats['por_fonte'][fonte]['ativas'] += ativos_count
        stats['por_fonte'][fonte]['ociosas'] += ociosas
        
        # Campuses
        campi = set()
        for b in e.bolsistas:
            if b.ativo and b.programa_link and b.programa_link.campus:
                campi.add(b.programa_link.campus.sigla_campus)
        campi_list = sorted(list(campi))
        
        stats['editais'].append({
            'numero': e.numero,
            'titulo': e.descricao,
            'vagas': vagas,
            'ativos': ativos_count,
            'ociosas': ociosas,
            'campi': campi_list,
            'niveis': sorted(list(niveis_set))
        })

    # 4. CAPES Detailed Analysis (PPG & IES)
    stats['capes_detalhado'] = []
    
    # helper to process capes edital
    def process_capes_programas(edital_id, tipo_label):
        # Dictionary to aggregate: {referencia: {'programa': name, 'nivel': level, 'cota': 0, 'ocupado': 0}}
        # We use (programa_id, nivel) as key
        data_map = {}
        
        # 1. Start with Quotas if available (DistribuicaoCotas)
        try:
            sql_cotas = """
                SELECT p.id as p_id, p.nome_programa, m.nivel, c.qtd_concedida
                FROM distribuicao_cotas c
                JOIN programa_academico p ON c.programa_id = p.id
                JOIN modalidades m ON c.modalidade_id = m.id
                WHERE c.edital_id = :eid
            """
            rs_cotas = db.session.execute(text(sql_cotas), {'eid': edital_id})
            for r in rs_cotas:
                key = (r.p_id, r.nivel) # Use ID instead of name for key safety
                data_map[key] = {
                    'programa': r.nome_programa,
                    'nivel': r.nivel,
                    'cota': r.qtd_concedida,
                    'ocupado': 0
                }
        except Exception as e:
            print(f"No quota table for {edital_id}: {e}")
            
        # 2. Count Active Bolsistas (Source of Truth for Occupancy)
        # We query all active bolsistas for this Edital and group by Program/Level
        sql_ativos = """
            SELECT b.programa_id, m.nivel, p.nome_programa, COUNT(b.id) as total
            FROM bolsistas b
            JOIN modalidades m ON b.modalidade_id = m.id
            JOIN programa_academico p ON b.programa_id = p.id
            WHERE b.edital_id = :eid AND (b.ativo = true OR b.motivo_desligamento = 'Finalizando')
            GROUP BY b.programa_id, m.nivel, p.nome_programa
        """
        rs_ativos = db.session.execute(text(sql_ativos), {'eid': edital_id})
        
        for r in rs_ativos:
            key = (r.programa_id, r.nivel)
            if key not in data_map:
                # Program has active students but NO quota record (maybe IES without rigid quota distribution?)
                data_map[key] = {
                    'programa': r.nome_programa,
                    'nivel': r.nivel,
                    'cota': '-', # Undefined quota
                    'ocupado': 0
                }
            
            data_map[key]['ocupado'] = r.total

        # Convert to list and append to stats
        for k, v in data_map.items():
            # Calculate saldo for insights
            saldo = 0
            if v['cota'] != '-': 
                saldo = v['cota'] - v['ocupado']
                
            stats['capes_detalhado'].append({
                'tipo': tipo_label,
                'programa': v['programa'],
                'nivel': v['nivel'],
                'cota': v['cota'],
                'ocupado': v['ocupado'],
                'saldo': saldo if v['cota'] != '-' else 0,
                'status': 'Lotado' if (v['cota'] != '-' and v['ocupado'] >= v['cota']) else 'Vagas'
            })

    # Process Edital 14 (PPG - NAPI/FUNTEF)
    process_capes_programas(14, 'NAPI/FUNTEF PPG')
    
    # Process Edital 13 (NAPI/FUNTEF IES)
    process_capes_programas(13, 'NAPI/FUNTEF IES')
    
    # Sort by Program Name
    stats['capes_detalhado'].sort(key=lambda x: x['programa'])

    # Calculate Rates
    for source, data in stats['por_fonte'].items():
        if data['ofertadas'] > 0:
            data['taxa'] = int(round((data['ativas'] / data['ofertadas']) * 100))
            
    if stats['total_ofertadas'] > 0:
        stats['taxa_ocupacao'] = round((stats['total_ativas'] / stats['total_ofertadas']) * 100, 1)
    
    # Remove empty sources
    stats['por_fonte'] = {k:v for k,v in stats['por_fonte'].items() if v['ofertadas'] > 0}

    return render_template('reports/report_integrated.html', stats=stats, hoje=date.today())

# --- 5. RELATÓRIO DE AUDITORIA (BOLSAS 2025) ---
@reports_bp.route('/reports/audit/excel')
def audit_report_excel_route():
    from sqlalchemy import text
    
    # --- CONFIGURAÇÃO DA LISTA DE PROGRAMAS (ORDEM EXATA) ---
    # Formato: (Nivel, Nome Exibido)
    RAW_ORDER_LIST = [
    #    ("Doutorado", "Discente IES Participante (Plataforma Sucupira)"), -- REMOVED AS PER USER REQUEST
    #    ("Mestrado", "Discente IES Participante (Plataforma Sucupira)"),  -- REMOVED AS PER USER REQUEST
        ("Mestrado", "40006018044P2 - ADMINISTRAÇÃO"),
        ("Mestrado", "40006018043P6 - AGROECOSSISTEMAS"),
        ("Doutorado", "40006018005P7 - AGRONOMIA"),
        ("Mestrado", "40006018005P7 - AGRONOMIA"),
        ("Doutorado", "40001016175P8 - BIOINFORMÁTICA"),
        ("Mestrado", "40006018037P6 - BIOINFORMÁTICA"),
        ("Doutorado", "40006018176P6 - BIOTECNOLOGIA"),
        ("Mestrado", "40006018176P6 - BIOTECNOLOGIA"),
        ("Mestrado", "40006018171P4 - CIÊNCIA DA COMPUTAÇÃO"),
        ("Mestrado", "40006018182P6 - CIÊNCIA DA COMPUTAÇÃO"),
        ("Mestrado", "40006018175P0 - CIÊNCIA E ENGENHARIA DE MATERIAIS"),
        ("Doutorado", "40006018013P0 - CIÊNCIA E TECNOLOGIA AMBIENTAL"),
        ("Mestrado", "40006018013P0 - CIÊNCIA E TECNOLOGIA AMBIENTAL"),
        ("Doutorado", "40006018010P0 - Desenvolvimento Regional"),
        ("Mestrado", "40006018010P0 - Desenvolvimento Regional"),
        ("Mestrado", "40006018173P7 - Educação Física"),
        ("Mestrado", "40006018023P5 - Engenharia Ambiental"),
        ("Mestrado", "40006018174P3 - Engenharia Ambiental: Análise e Tecnologia Ambiental"),
        ("Doutorado", "40006018008P6 - ENGENHARIA CIVIL"),
        ("Mestrado", "40006018008P6 - ENGENHARIA CIVIL"),
        ("Mestrado", "40006018030P1 - Engenharia Civil (PPGEC)"),
        ("Doutorado", "40006018004P0 - ENGENHARIA DE PRODUÇÃO"),
        ("Mestrado", "40006018004P0 - ENGENHARIA DE PRODUÇÃO"),
        ("Mestrado", "40006018031P8 - Engenharia de Produção e Sistemas (PPGEPS)"),
        ("Doutorado", "40002012171P9 - ENGENHARIA ELETRICA"),
        ("Mestrado", "40006018022P9 - Engenharia Elétrica"),
        ("Mestrado", "40006018012P3 - Engenharia Elétrica - Cornélio Procópio"),
        ("Mestrado", "40006018009P2 - Engenharia Elétrica e de Computação"),
        ("Doutorado", "40006018001P1 - ENGENHARIA ELÉTRICA E INFORMÁTICA INDUSTRIAL"),
        ("Mestrado", "40006018001P1 - ENGENHARIA ELÉTRICA E INFORMÁTICA INDUSTRIAL"),
        ("Mestrado", "40006018024P1 - Engenharia Mecânica"),
        ("Mestrado", "40006018029P3 - Engenharia Mecânica"),
        ("Doutorado", "40006018003P4 - ENGENHARIA MECÂNICA E DE MATERIAIS"),
        ("Mestrado", "40006018003P4 - ENGENHARIA MECÂNICA E DE MATERIAIS"),
        ("Mestrado", "40006018177P2 - ENGENHARIA QUÍMICA"),
        ("Mestrado", "40006018179P5 - ENGENHARIA QUÍMICA"),
        ("Doutorado", "40006018028P7 - ENSINO DE CIÊNCIA E TECNOLOGIA"),
        ("Mestrado", "40006018035P3 - ESTUDOS DE LINGUAGENS"),
        ("Mestrado", "40006018172P0 - FÍSICA E ASTRONOMIA"),
        ("Mestrado", "40006018036P0 - LETRAS"),
        ("Mestrado", "40006018021P1 - MATEMÁTICA"),
        ("Mestrado", "40006018033P0 - PROCESSOS QUÍMICOS E BIOTECNOLÓGICOS"),
        ("Mestrado", "40006018032P4 - Química"),
        ("Mestrado", "40006018178P9 - RECURSOS NATURAIS E SUSTENTABILIDADE"),
        ("Doutorado", "40006018181P0 - SUSTENTABILIDADE AMBIENTAL URBANA"),
        ("Doutorado", "40006018016P9 - TECNOLOGIA DE ALIMENTOS"),
        ("Mestrado", "40006018016P9 - Tecnologia de Alimentos"),
        ("Mestrado", "40006018020P6 - Tecnologia de Processos Químicos e Bioquímicos"),
        ("Doutorado", "40006018002P8 - TECNOLOGIA E SOCIEDADE"),
        ("Mestrado", "40006018002P8 - TECNOLOGIA E SOCIEDADE"),
        ("Mestrado", "40006018026P4 - Tecnologias Ambientais"),
        ("Mestrado", "40006018034P7 - TECNOLOGIAS COMPUTACIONAIS PARA O AGRONEGÓCIO"),
        ("Mestrado", "40006018183P2 - TÊXTIL E MODA"),
        ("Doutorado", "40015017009P8 - Zootecnia (Associação Unioeste)"),
        ("Mestrado", "40015017009P8 - Zootecnia (Associação Unioeste)"),
        ("Mestrado", "40006018184P9 - Design Prospectivo"), 
        ("Mestrado", "40006018185P5 - Educação Tecnológica")
    ]
    
    # [NEW] Dynamic Append: Recursos Próprios at the end
    # Fetch programs with Active scholarships from Edital 1 (Recursos Proprios) or matching description
    # that are NOT already in the list.
    
    try:
        sql_proprios = """
            SELECT DISTINCT p.nome_programa, m.nivel
            FROM bolsistas b 
            JOIN editais e ON b.edital_id = e.id 
            JOIN programa_academico p ON b.programa_id = p.id
            LEFT JOIN modalidades m ON b.modalidade_id = m.id
            WHERE (e.id = 1 OR UPPER(e.descricao) LIKE '%PROPRIOS%' OR UPPER(e.descricao) LIKE '%PRÓPRIOS%') 
              AND b.ativo = true
        """
        rows_proprios = db.session.execute(text(sql_proprios)).fetchall()
        
        # Helper to check if exists (Local definition to avoid scope issues)
        def is_in_list(tgt_nivel, tgt_name, current_list):
            def norm(n): 
                if not n: return "NI"
                n = n.upper().strip()
                if ' - ' in n: return n.split(' - ')[1].strip()
                return n

            tn = norm(tgt_name)
            for (l_nivel, l_name) in current_list:
                ln = norm(l_name)
                if tn == ln and (tgt_nivel or "").upper() == (l_nivel or "").upper():
                    return True
            return False

        for r in rows_proprios:
            p_name = r.nome_programa
            p_nivel = r.nivel or "Mestrado" # Default if null
            
            if not is_in_list(p_nivel, p_name, RAW_ORDER_LIST):
                RAW_ORDER_LIST.append((p_nivel, p_name))
                print(f"Dynamically appended Resource Proprios program: {p_name}")
                
    except Exception as e:
        print(f"Error fetching Recursos Proprios dynamic list: {e}")

    # --- HELPER: NORMALIZAÇÃO ---
    def normalize_prog_name(name):
        if not name: return "NI"
        name = name.upper().strip()
        if ' - ' in name:
            parts = name.split(' - ')
            if len(parts) > 1: return parts[1].strip()
        return name

    # --- CATEGORIAS ---
    def get_cat(edital_id, numero, descricao, agencia):
        numero = str(numero).strip()
        desc = (descricao or "").upper()
            
        if 'PROPPG' in desc and 'CAPES' in desc:
            if '14/25' in numero or '14/2025' in numero: return '14_25_INTER'
            return 'CAPES_PROPPG'
        if edital_id == 14: return 'CAPES_PROPPG'
        
        if 'IES' in desc and 'CAPES' in desc: return 'CAPES_IES'
        if edital_id == 13: return 'CAPES_IES'
        
        if 'PDPG' in desc: return 'PDPG'
        if 'MAI' in desc and 'DAI' in desc: return 'MAI_DAI'
        if '32' in numero and ('2025' in numero or '25' in numero): return '32_2025'
        
        if '14' in numero and ('2025' in numero or '25' in numero): return '14_25_INTER'
        
        if 'PROPRIOS' in desc or 'PRÓPRIOS' in desc or edital_id == 1: return 'REC_PROPRIOS'
        
        return 'OUTROS'

    # 1. Map Editais
    editais = db.session.execute(text("SELECT id, numero, descricao, agencia FROM editais")).fetchall()
    edital_map = {}
    for e in editais:
        edital_map[e.id] = get_cat(e.id, e.numero, e.descricao, e.agencia)
        
    # 2. Fetch Active Data (Utilizada) - Strict "Ativas Atualmente"
    sql = """
        SELECT b.id, b.nome, b.cpf, b.edital_id, m.nivel, p.nome_programa, p.codigo_programa
        FROM bolsistas b
        LEFT JOIN modalidades m ON b.modalidade_id = m.id
        LEFT JOIN programa_academico p ON b.programa_id = p.id
        WHERE b.ativo = true
    """
    rows = db.session.execute(text(sql)).fetchall()
    
    data_active = {}
    
    for r in rows:
        prog_raw = r.nome_programa
        prog_clean = "DISCENTE IES PARTICIPANTE (PLATAFORMA SUCUPIRA)" if not prog_raw or "IES" in (prog_raw or "").upper() else normalize_prog_name(prog_raw)
        
        nivel = r.nivel or "Mestrado"
        cat = edital_map.get(r.edital_id, 'OUTROS')
        
        if prog_clean not in data_active: data_active[prog_clean] = {}
        if nivel not in data_active[prog_clean]: data_active[prog_clean][nivel] = {}
        if cat not in data_active[prog_clean][nivel]: data_active[prog_clean][nivel][cat] = 0
        
        data_active[prog_clean][nivel][cat] += 1

    # 3. Fetch Quotas (Concedida) - Mainly for CAPES PROPPG (Edital 14)
    data_quotas = {}
    try:
        # Check if table exists
        chk = db.session.execute(text("SELECT to_regclass('public.distribuicao_cotas')")).fetchone() # Postgres check
        if not chk or not chk[0]:
             # Fallback check for SQLite
             chk = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='distribuicao_cotas'")).fetchone()
        
        if chk:
             q_rows = db.session.execute(text("""
                SELECT p.nome_programa, m.nivel, c.edital_id, c.qtd_concedida
                FROM distribuicao_cotas c
                JOIN programa_academico p ON c.programa_id = p.id
                JOIN modalidades m ON c.modalidade_id = m.id
             """)).fetchall()
             
             for qr in q_rows:
                 q_prog = normalize_prog_name(qr.nome_programa)
                 q_lvl = qr.nivel
                 q_cat = edital_map.get(qr.edital_id, 'OUTROS')
                 
                 if q_prog not in data_quotas: data_quotas[q_prog] = {}
                 if q_lvl not in data_quotas[q_prog]: data_quotas[q_prog][q_lvl] = {}
                 
                 # Sum in case multiple entries
                 current = data_quotas[q_prog][q_lvl].get(q_cat, 0)
                 data_quotas[q_prog][q_lvl][q_cat] = current + qr.qtd_concedida
    except Exception as e:
        print(f"Quota Fetch Error: {e}")

    # 4. Build Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Relatório Bolsas 2025"
    
    cats_order = ['CAPES_PROPPG', 'PDPG', 'CAPES_IES', 'MAI_DAI', '32_2025', 'REC_PROPRIOS', '14_25_INTER']
    cat_labels = {
        'CAPES_PROPPG': 'CAPES PROPPG', 'PDPG': 'PDPG', 'CAPES_IES': 'CAPES IES PPG',
        'MAI_DAI': 'MAI/DAI (CNPq)', '32_2025': '32/2025 (Internacionalização)',
        'REC_PROPRIOS': 'Recursos Próprios', '14_25_INTER': '14/25 (Mest/Dout Int)',
        'OUTROS': 'Outros'
    }
    
    # Headers
    bold_font = Font(bold=True)
    center_align = Alignment(horizontal='center')
    
    ws['A1'] = "Modalidade"
    ws['B1'] = "PPG/Área"
    ws['A2'] = "Modalidade"
    ws['B2'] = "PPG/Área"
    
    col_idx = 3
    cat_start_cols = {}
    
    for cat in cats_order:
        cat_start_cols[cat] = col_idx
        ws.cell(row=1, column=col_idx, value=cat_labels[cat])
        ws.merge_cells(start_row=1, start_column=col_idx, end_row=1, end_column=col_idx+2)
        cell = ws.cell(row=1, column=col_idx)
        cell.font = bold_font
        cell.alignment = center_align
        
        ws.cell(row=2, column=col_idx, value="Concedida")
        ws.cell(row=2, column=col_idx+1, value="Utilizada")
        ws.cell(row=2, column=col_idx+2, value="Disponível")
        col_idx += 3

    ws.cell(row=1, column=col_idx, value="SOMA")
    ws.cell(row=2, column=col_idx, value="Total Ativas")
    
    # Fill Data
    row_num = 3
    
    for (nivel_req, prog_display) in RAW_ORDER_LIST:
        ws.cell(row=row_num, column=1, value=nivel_req)
        ws.cell(row=row_num, column=2, value=prog_display)
        
        lookup_name = normalize_prog_name(prog_display)
        if "DISCENTE IES" in prog_display.upper():
             lookup_name = "DISCENTE IES PARTICIPANTE (PLATAFORMA SUCUPIRA)"

        row_total_active = 0
        
        for cat in cats_order:
            c_idx = cat_start_cols[cat]
            
            # Utilizada (Active)
            u_val = 0
            if lookup_name in data_active and nivel_req in data_active[lookup_name]:
                u_val = data_active[lookup_name][nivel_req].get(cat, 0)
            
            # Concedida (Quota)
            # Priority: 1. DB Distribuição (Strict for CAPES_PROPPG)
            #           2. Active Count (Fallback for others)
            q_val = 0
            
            if lookup_name in data_quotas and nivel_req in data_quotas[lookup_name]:
                 q_val = data_quotas[lookup_name][nivel_req].get(cat, 0)
            
            # Fallback for non-quota tracked editais (assume fully allocated or dynamic)
            if q_val == 0 and u_val > 0:
                 q_val = u_val
            
            # Disponivel
            d_val = q_val - u_val
            
            ws.cell(row=row_num, column=c_idx, value=q_val)
            ws.cell(row=row_num, column=c_idx+1, value=u_val)
            ws.cell(row=row_num, column=c_idx+2, value=d_val)
            
            row_total_active += u_val
            
        ws.cell(row=row_num, column=col_idx, value=row_total_active)
        row_num += 1

    # Adjust Widths
    ws.column_dimensions['A'].width = 15
    ws.column_dimensions['B'].width = 50

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    return send_file(output, as_attachment=True, download_name="relatorio_bolsas_audit_2025.xlsx")

def gerar_relatorio_pendencias_pdf(mes_ref_str):
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        
        c_lightgrey = colors.HexColor('#e5e7eb')
        
        try:
            dt_ref = datetime.strptime(mes_ref_str, '%Y-%m').date()
        except:
            dt_ref = date.today()
            
        year = dt_ref.year
        month = dt_ref.month
        last_day = calendar.monthrange(year, month)[1]
        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)

        if month == 12:
            next_month = 1
            next_year = year + 1
        else:
            next_month = month + 1
            next_year = year
        start_next = date(next_year, next_month, 1)
        end_next = date(next_year, next_month, calendar.monthrange(next_year, next_month)[1])

        alert_bolsistas = Bolsista.query.filter(Bolsista.data_fim_bolsa.between(start_date, end_date), Bolsista.ativo == True).all()
        expiring_editais = Edital.query.filter(Edital.data_fim.between(start_date, end_next)).all()
        pending_acc = Edital.query.filter(Edital.data_fim < end_date, Edital.prestacao_contas == False).all()

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
        elements = []
        styles = getSampleStyleSheet()
        elements.append(Paragraph(f"Relatório de Gestão e Prazos - {mes_ref_str}", styles['Title']))
        
        # [Simplified table logic for brevity in blueprint]
        if alert_bolsistas:
             elements.append(Paragraph("Bolsistas Finalizando", styles['Heading2']))
             data = [["Nome", "Fim da Bolsa"]]
             for b in alert_bolsistas: data.append([b.nome, b.data_fim_bolsa.strftime('%d/%m/%Y')])
             elements.append(Table(data))

        doc.build(elements)
        buffer.seek(0)
        return buffer
    except Exception as e:
        buffer = io.BytesIO()
        buffer.write(f"Erro ao gerar PDF: {str(e)}".encode('utf-8'))
        buffer.seek(0)
        return buffer

@reports_bp.route('/reports/devolucao/pdf')
def devolucao_valores_pdf():
    from reports import gerar_relatorio_devolucao
    return send_file(gerar_relatorio_devolucao(), as_attachment=False, mimetype='application/pdf')

@reports_bp.route('/relatorios/gerar', methods=['POST'])
def relatorios_gerar():
    tipo = request.form['tipo']
    mes = request.form['mes']
    
    # [FIX] Compatibilidade com <input type="date"> que envia YYYY-MM-DD
    if len(mes) > 7:
        mes = mes[:7]
        
    from reports import gerar_relatorio_excel, gerar_relatorio_pdf, gerar_relatorio_graficos
    
    if tipo == 'excel':
        output = gerar_relatorio_excel(mes)
        return send_file(output, download_name=f'pagamento_{mes}.xlsx', as_attachment=True)
    elif tipo == 'pdf':
        output = gerar_relatorio_pdf(mes)
        return send_file(output, download_name=f'pagamento_{mes}.pdf', as_attachment=True)
    elif tipo == 'graficos':
        output = gerar_relatorio_graficos(mes)
        return send_file(output, download_name=f'relatorio_grafico_{mes}.pdf', as_attachment=True)
    elif tipo == 'acoes_pendentes_pdf':
        output = gerar_relatorio_pendencias_pdf(mes)
        return send_file(output, download_name=f'Relatorio_Alertas_{mes}.pdf', as_attachment=True)
    
    return "Tipo de relatório não suportado", 400

@reports_bp.route('/relatorios/eixo', methods=['POST'])
@login_required
def gerar_relatorio_eixo():
    eixo = request.form.get('eixo', 'ALL')
    from reports import gerar_relatorio_eixo_pdf
    output = gerar_relatorio_eixo_pdf(eixo)
    return send_file(output, download_name=f'relatorio_eixo_{eixo}_{date.today().strftime("%Y-%m-%d")}.pdf', as_attachment=True)
