"""Log individual de pagamentos — mesmas colunas/regras da folha enviada à Nuvem."""
from datetime import date
from dateutil.relativedelta import relativedelta

from models import Modalidade, Edital
from services.financeiro_service import VencimentoFactory
from utils.date_utils import calcular_parcelas

# Mesmas colunas de reports.gerar_relatorio_excel
PAGAMENTO_HEADERS = [
    'Edital', 'SEI', 'CPF', 'Nome', 'E-mail', 'Orientador', 'Instituição',
    'Banco', 'Agência', 'Conta', 'Tipo', 'Nível',
    'Valor', 'Início Bolsa', 'Referência', 'Vencimento',
    'Parcela Atual', 'Total Parcelas',
]


class PagamentoBolsistaService:
    @classmethod
    def _ultimo_mes_referencia(cls, bolsista, hoje=None):
        hoje = hoje or date.today()
        fim = hoje
        if bolsista.data_desligamento and bolsista.data_desligamento < fim:
            fim = bolsista.data_desligamento
        if bolsista.data_fim_bolsa and bolsista.data_fim_bolsa < fim:
            fim = bolsista.data_fim_bolsa
        return date(fim.year, fim.month, 1)

    @classmethod
    def _iter_meses(cls, inicio, fim):
        """Yield YYYY-MM from inicio month through fim month inclusive."""
        cursor = date(inicio.year, inicio.month, 1)
        last = date(fim.year, fim.month, 1)
        while cursor <= last:
            yield cursor.strftime('%Y-%m')
            cursor = cursor + relativedelta(months=1)

    @classmethod
    def build_row(cls, bolsista, mes_referencia_str, parcela=None):
        """Uma linha no mesmo formato do Excel da Nuvem."""
        mod = bolsista.modalidade or Modalidade.query.get(bolsista.modalidade_id)
        edital = bolsista.edital or Edital.query.get(bolsista.edital_id)
        if not mod or not edital or not bolsista.data_inicio_bolsa:
            return None

        ref_date = date.fromisoformat(f'{mes_referencia_str}-01')
        if parcela is None:
            parcela = calcular_parcelas(
                bolsista.data_inicio_bolsa, ref_date, bolsista.data_desligamento
            )
        if not (parcela > 0 and parcela <= (bolsista.meses_duracao or 0)):
            return None

        valor = mod.valor_mensal
        valor_txt = f'R$ {valor:.2f}' if valor is not None else '—'

        return {
            'edital': edital.numero,
            'sei': bolsista.processo_sei or edital.processo_sei or 'N/A',
            'cpf': bolsista.cpf or '—',
            'nome': bolsista.nome,
            'email': bolsista.email or 'N/Informado',
            'orientador': bolsista.orientador or 'N/Informado',
            'instituicao': bolsista.instituicao or getattr(bolsista, 'sigla_campus_display', None) or 'N/I',
            'banco': bolsista.banco or '—',
            'agencia': bolsista.agencia or '—',
            'conta': bolsista.conta or '—',
            'tipo': bolsista.tipo_conta or '—',
            'nivel': mod.nivel or '—',
            'valor': valor_txt,
            'inicio_bolsa': bolsista.data_inicio_bolsa.strftime('%d/%m/%Y'),
            'referencia': mes_referencia_str,
            'vencimento': VencimentoFactory.get_strategy(edital.numero).get_vencimento_label(),
            'parcela_atual': parcela,
            'total_parcelas': bolsista.meses_duracao,
        }

    @classmethod
    def listar_pagamentos(cls, bolsista, hoje=None):
        """
        Linhas de pagamento já devidas (início → mês corrente/fim),
        recalculadas a partir de data_inicio_bolsa — igual à folha Nuvem.
        """
        hoje = hoje or date.today()
        if not bolsista or not bolsista.data_inicio_bolsa or not bolsista.meses_duracao:
            return []

        inicio = bolsista.data_inicio_bolsa
        fim = cls._ultimo_mes_referencia(bolsista, hoje=hoje)
        if fim < date(inicio.year, inicio.month, 1):
            return []

        rows = []
        for mes in cls._iter_meses(inicio, fim):
            row = cls.build_row(bolsista, mes)
            if row:
                rows.append(row)
        return rows
