"""Implantação da bolsa: cadastro antes de liberar pagamentos (FA / FUNTEF).

Usa ``implantacao_pendente`` + ``status_governanca='PENDENTE'`` da governança NAPI.
"""
from models import ComentarioBolsista
from utils.araucaria import is_bolsista_araucaria


class ImplantacaoBolsaService:
    @classmethod
    def _fluxo_funtef_iniciado(cls, bolsista):
        return bool(
            getattr(bolsista, 'implantacao_pendente', False)
            or getattr(bolsista, 'status_governanca', None) == 'PENDENTE'
            or bolsista.conveniar_cadastrado
            or bolsista.funtef_email_enviado_em
        )

    @classmethod
    def pendencias(cls, bolsista, *, exigir_inicio=True):
        """O que falta para liberar pagamentos.

        ``exigir_inicio=False`` na ativação NAPI: a data vem da liberação da Fundação.
        """
        itens = []
        if exigir_inicio and not bolsista.data_inicio_bolsa:
            itens.append('Informe o início da bolsa (ou ative com a data de liberação da Fundação).')
        if not bolsista.meses_duracao:
            itens.append('Informe a duração da bolsa em meses.')

        if is_bolsista_araucaria(bolsista) and cls._fluxo_funtef_iniciado(bolsista):
            if not bolsista.conveniar_cadastrado:
                itens.append('Confirme o cadastro solicitado no Conveniar.')
            if not (bolsista.link_pasta_nuvem or '').strip():
                itens.append('Informe o link da pasta na Nuvem.')
            if not bolsista.funtef_email_enviado_em:
                itens.append(
                    'Aguarde o envio do e-mail à FUNTEF '
                    '(marque o Conveniar, informe o link da Nuvem e salve).'
                )
            if not bolsista.funtef_contrato_pronto:
                itens.append(
                    'Marque o contrato FUNTEF / Fundação Araucária como pronto '
                    '(retorno recebido).'
                )
        return itens

    @classmethod
    def deve_ficar_pendente(cls, bolsista):
        if not bolsista.data_inicio_bolsa or not bolsista.meses_duracao:
            return True
        return bool(
            is_bolsista_araucaria(bolsista) and not bolsista.funtef_contrato_pronto
        )

    @classmethod
    def marcar_pendente(cls, bolsista, user_id=None, registrar_comentario=True):
        bolsista.ativo = False
        bolsista.implantacao_pendente = True
        bolsista.status_governanca = 'PENDENTE'
        bolsista.data_desligamento = None
        bolsista.motivo_desligamento = None
        if not registrar_comentario:
            return
        faltas = cls.pendencias(bolsista, exigir_inicio=False) or [
            'Ativação manual pendente (FUNTEF / Fundação).'
        ]
        texto = (
            '[IMPLANTAÇÃO PENDENTE]\n'
            'Cadastro registrado sem liberar pagamentos (fora da folha e dos '
            'e-mails automáticos até a ativação pela Fundação).\n'
            'Pendências: ' + ' '.join(faltas)
        )
        bolsista.comentarios_historico.append(
            ComentarioBolsista(texto=texto, user_id=user_id)
        )

    @classmethod
    def registrar_ativacao(cls, bolsista, user_id=None):
        from utils import format_date_br

        bolsista.implantacao_pendente = False
        bolsista.status_governanca = 'ATIVO'
        periodo = (
            f'{format_date_br(bolsista.data_inicio_bolsa)} a '
            f'{format_date_br(bolsista.data_fim_bolsa)}'
        )
        bolsista.comentarios_historico.append(
            ComentarioBolsista(
                texto=(
                    '[BOLSA IMPLANTADA]\n'
                    f'Pagamentos liberados para a vigência {periodo}.'
                ),
                user_id=user_id,
            )
        )

    @classmethod
    def label_pendencia(cls, bolsista):
        if is_bolsista_araucaria(bolsista) and not bolsista.funtef_contrato_pronto:
            return 'Aguardando contrato FUNTEF / Fundação Araucária'
        if not bolsista.data_inicio_bolsa or not bolsista.meses_duracao:
            return 'Aguardando definição da vigência da bolsa'
        return 'Aguardando ativação dos pagamentos'
