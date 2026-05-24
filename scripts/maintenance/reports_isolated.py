"""
MÓDULO DE RELATÓRIOS ISOLADO
============================
Lógica para geração de Excel e PDF dos relatórios solicitados.
"""

from flask import Blueprint, render_template, make_response, send_file
from models import Bolsista, Residente, Edital, Acompanhamento, Modalidade
from io import BytesIO
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from datetime import date
from dateutil.relativedelta import relativedelta

reports_bp = Blueprint('reports_isolated', __name__, template_folder='templates/isolated')

# HELPER: Formatação de Moeda
def format_currency(value):
    if not value: return "R$ 0,00"
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- 1. RELATÓRIO INDIVIDUAL (DISCENTE/RESIDENTE) ---

@reports_bp.route('/student/<int:id>/pdf')
def student_report_pdf(id):
    """
    Gera relatório HTML (pdf-friendly) para impressão.
    """
    # Tenta buscar em Bolsista, se não achar, busca em Residente (workaround simples)
    bolsista = Bolsista.query.get(id)
    tipo = "Discente"
    
    if not bolsista:
        return "Bolsista não encontrado", 404

    # Coletar Extrato (Apenas para Bolsistas, Residentes não têm Acompanhamento)
    extrato = []
    total_pago = 0.0
    
    if tipo == "Discente":
        pagamentos = Acompanhamento.query.filter_by(bolsista_id=id).order_by(Acompanhamento.referencia_mes).all()
        valor_mensal = bolsista.modalidade.valor_mensal if bolsista.modalidade else 0.0
        
        for p in pagamentos:
            # Assume valor atual da modalidade (limitação conhecida)
            valor = valor_mensal 
            total_pago += valor
            extrato.append({
                'mes': p.referencia_mes,
                'parcela': p.parcela,
                'valor': valor,
                'obs': p.observacoes
            })
    
    # [CORREÇÃO] Se Total Pago for 0, usar Estimativa (conforme solicitado)
    is_estimado = False
    if total_pago == 0:
        hoje = date.today()
        if bolsista.data_inicio_bolsa and bolsista.data_fim_bolsa:
            cutoff = min(hoje, bolsista.data_fim_bolsa)
            if cutoff > bolsista.data_inicio_bolsa:
                diff = relativedelta(cutoff, bolsista.data_inicio_bolsa)
                meses_estimados = diff.years * 12 + diff.months
                
                # Proteção de Limites
                if meses_estimados < 0: meses_estimados = 0
                if meses_estimados > bolsista.meses_duracao: meses_estimados = bolsista.meses_duracao
                
                valor_mensal = bolsista.modalidade.valor_mensal if bolsista.modalidade else 0.0
                total_pago = meses_estimados * valor_mensal
                is_estimado = True
                
                # Gerar Extrato Estimado
                start_date = bolsista.data_inicio_bolsa
                for i in range(meses_estimados):
                    # Data de referência (mês i)
                    ref_date = start_date + relativedelta(months=i)
                    ref_mes = ref_date.strftime("%Y-%m")
                    
                    extrato.append({
                        'mes': ref_mes,
                        'parcela': i + 1,
                        'valor': valor_mensal,
                        'obs': 'Valor Estimado (Automático)'
                    })

    # Cálculos Previstos
    valor_mensal_atual = bolsista.modalidade.valor_mensal if bolsista.modalidade else 0.0
    total_previsto = valor_mensal_atual * bolsista.meses_duracao
    
    saldo = total_previsto - total_pago

    return render_template('report_student.html', 
                           bolsista=bolsista,
                           tipo=tipo,
                           extrato=extrato,
                           total_pago=total_pago,
                           total_previsto=total_previsto,
                           saldo=saldo,
                           is_estimado=is_estimado,
                           hoje=date.today())

@reports_bp.route('/resident/<int:id>/pdf')
def resident_report_pdf(id):
    """
    Gera relatório para Residentes (Pós-Doc).
    Lógica de pagamento ESTIMADA.
    """
    residente = Residente.query.get_or_404(id)
    tipo = "Residente Pós-Doc"

    # Lógica Estimada (Conforme aprovado no plano)
    valor_mensal = residente.modalidade.valor_mensal if residente.modalidade else 0.0
    
    # Calcular meses passados desde o início até hoje (limitado ao fim)
    hoje = date.today()
    inicio = residente.data_inicio
    fim = residente.data_fim
    
    # Data efetiva de corte para cálculo do "Pago"
    cutoff = min(hoje, fim)
    
    meses_pagos_estimado = 0
    if cutoff > inicio:
        # Diferença em meses
        r = relativedelta(cutoff, inicio)
        meses_pagos_estimado = r.years * 12 + r.months
        # Se tiver dias quebrados, não conta mês cheio (ou conta? vamos ser conservadores e contar apenas meses cheios ou +1 se passou dia 15? simplificar: meses corridos)
        if cutoff.day >= inicio.day:
             pass # completou o mês
        
        # Ajuste fino: se hoje é dia 25, considera pago o mês atual?
        # Vamos assumir pagamento mensal padrão.
    
    # Proteção
    if meses_pagos_estimado < 0: meses_pagos_estimado = 0
    if meses_pagos_estimado > residente.meses_duracao: meses_pagos_estimado = residente.meses_duracao

    total_pago_estimado = meses_pagos_estimado * valor_mensal
    total_previsto = residente.meses_duracao * valor_mensal
    saldo_estimado = total_previsto - total_pago_estimado

    return render_template('report_resident.html',
                           pessoa=residente,
                           tipo=tipo,
                           valor_mensal=valor_mensal,
                           meses_pagos=meses_pagos_estimado,
                           total_pago=total_pago_estimado,
                           total_previsto=total_previsto,
                           saldo=saldo_estimado,
                           hoje=date.today())

# --- 2. RELATÓRIO DE EDITAL (RECURSOS PRÓPRIOS) ---

@reports_bp.route('/edital/<int:id>/excel')
def edital_report_excel(id):
    edital = Edital.query.get_or_404(id)
    
    wb = Workbook()
    ws = wb.active
    ws.title = f"Relatório Financeiro Edital {edital.numero}"
    
    # Cabeçalho
    headers = [
        "Nome", "CPF", "Programa", "Modalidade", "Início", "Fim", 
        "Duração (Meses)", "Valor Mensal", 
        "Parcelas Pagas (Qtd)", "Total Pago (R$)", 
        "Total Previsto (R$)", "Saldo a Pagar (R$)"
    ]
    ws.append(headers)
    
    # Estilo Cabeçalho
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="4F81BD", fill_type="solid")
    
    total_geral_pago = 0.0
    total_geral_previsto = 0.0
    
    # 1. Processar Bolsistas
    for b in edital.bolsistas:
        if not b.ativo: continue # Opcional: incluir inativos? Pedido diz "dados atualizados", assumirei ativos por padrão ou todos? "cada bolsista". Vou incluir todos.
        
        # Pagamentos Reais
        qtd_parcelas_pagas = len(b.acompanhamentos)
        valor_mensal = b.modalidade.valor_mensal if b.modalidade else 0.0
        
        obs_estimado = ""
        
        if qtd_parcelas_pagas > 0:
            # Tem pagamentos reais
            total_pago = qtd_parcelas_pagas * valor_mensal
        else:
            # Sem pagamentos registrados: Usar ESTIMATIVA (Fallback)
            hoje = date.today()
            if b.data_inicio_bolsa and b.data_fim_bolsa:
                cutoff = min(hoje, b.data_fim_bolsa)
                if cutoff > b.data_inicio_bolsa:
                    diff = relativedelta(cutoff, b.data_inicio_bolsa)
                    qtd_parcelas_pagas = diff.years * 12 + diff.months
                    # Ajuste para incluir o mês corrente se já passou do dia 20 (exemplo) ou simplificar
                    # Vamos manter meses completos para consistência
                    if qtd_parcelas_pagas < 0: qtd_parcelas_pagas = 0
                    if qtd_parcelas_pagas > b.meses_duracao: qtd_parcelas_pagas = b.meses_duracao
                else:
                    qtd_parcelas_pagas = 0
            else:
                qtd_parcelas_pagas = 0
            
            total_pago = qtd_parcelas_pagas * valor_mensal
            if qtd_parcelas_pagas > 0:
                obs_estimado = " (Est)"

        total_previsto = b.meses_duracao * valor_mensal
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

    # 2. Processar Residentes (Se houver Residentes vinculados ao Edital)
    # Nota: Residentes têm link com Edital? Sim (Residente.edital_id)
    # Lógica Estimada para eles
    residentes = Residente.query.filter_by(edital_id=id).all()
    for r in residentes:
        valor_mensal = r.modalidade.valor_mensal if r.modalidade else 0.0
        
        # Estimativa (copiada da lógica acima)
        hoje = date.today()
        cutoff = min(hoje, r.data_fim)
        meses_pagos = 0
        if cutoff > r.data_inicio:
            diff = relativedelta(cutoff, r.data_inicio)
            meses_pagos = diff.years * 12 + diff.months
        
        if meses_pagos > r.meses_duracao: meses_pagos = r.meses_duracao
        if meses_pagos < 0: meses_pagos = 0
        
        total_pago = meses_pagos * valor_mensal
        total_previsto = r.meses_duracao * valor_mensal
        saldo = total_previsto - total_pago
        
        total_geral_pago += total_pago
        total_geral_previsto += total_previsto
        
        ws.append([
            r.nome + " (Residente)",
            r.cpf,
            r.programa_link.sigla_programa if r.programa_link else "-",
            "Pós-Doutorado",
            r.data_inicio,
            r.data_fim,
            r.meses_duracao,
            valor_mensal,
            f"{meses_pagos} (Est)",
            total_pago,
            total_previsto,
            saldo
        ])

    # Linha de Totais
    last_row = ws.max_row + 1
    total_geral_saldo = total_geral_previsto - total_geral_pago
    
    ws.cell(row=last_row, column=9, value="TOTAL GERAL").font = Font(bold=True)
    ws.cell(row=last_row, column=10, value=total_geral_pago).font = Font(bold=True)
    ws.cell(row=last_row, column=11, value=total_geral_previsto).font = Font(bold=True)
    ws.cell(row=last_row, column=12, value=total_geral_saldo).font = Font(bold=True)
    
    # Ajuste de Largura
    for col in range(1, 13):
        ws.column_dimensions[get_column_letter(col)].width = 15
    ws.column_dimensions['A'].width = 30
    
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    return send_file(output, as_attachment=True, download_name=f"relatorio_financeiro_{edital.numero}.xlsx")

@reports_bp.route('/test')
def test():
    return "Módulo de Relatórios OK"
