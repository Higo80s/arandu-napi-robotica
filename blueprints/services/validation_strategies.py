from typing import Protocol, List, Optional

from models import Bolsista, Candidatura
from utils.formatters import sanitizar_cpf


class RegraAcumuloStrategy(Protocol):
    def validar(
        self,
        cpf: str,
        bolsista_id_ignorar: int = None,
        candidatura_id_ignorar: int = None,
    ) -> bool:
        """
        Retorna True se passar na validação (Não há violação).
        bolsista_id_ignorar: edição (não comparar com o próprio registro).
        candidatura_id_ignorar: promoção seleção→bolsista (não flagrar a própria candidatura).
        """
        pass


def _cpf_key(cpf: str) -> Optional[str]:
    return sanitizar_cpf(cpf) or None


class AcumuloBolsaAtivaStrategy:
    """
    Verifica se JÁ EXISTE uma bolsa ATIVA correndo para este CPF (excluindo a própria se for edição).

    CPF é EncryptedString (Fernet): filter_by(cpf=...) não funciona — compara em Python
    após descriptografia do TypeDecorator (mesmo padrão de utils/idempotency.py).
    """
    def validar(
        self,
        cpf: str,
        bolsista_id_ignorar: int = None,
        candidatura_id_ignorar: int = None,
    ) -> bool:
        key = _cpf_key(cpf)
        if not key:
            return True

        rows = (
            Bolsista.query.with_entities(Bolsista.id, Bolsista.cpf)
            .filter_by(ativo=True)
            .all()
        )
        for bid, bcpf in rows:
            if bolsista_id_ignorar and bid == bolsista_id_ignorar:
                continue
            if sanitizar_cpf(bcpf) == key:
                return False
        return True


class AcumuloProcessoSeletivoStrategy:
    """
    Verifica se o candidato está convocado/selecionado em outro processo,
    indicando concomitância indesejada.

    Ignora candidatura_id_ignorar (a que está sendo efetivada neste cadastro).
    """
    def validar(
        self,
        cpf: str,
        bolsista_id_ignorar: int = None,
        candidatura_id_ignorar: int = None,
    ) -> bool:
        key = _cpf_key(cpf)
        if not key:
            return True

        rows = (
            Candidatura.query.with_entities(Candidatura.id, Candidatura.cpf)
            .filter(Candidatura.status.in_(['SELECIONADO', 'CONVOCADO']))
            .all()
        )
        for cid, ccpf in rows:
            if candidatura_id_ignorar and cid == candidatura_id_ignorar:
                continue
            if sanitizar_cpf(ccpf) == key:
                return False
        return True


class ValidadorAcumuloContext:
    def __init__(self, strategies: List[RegraAcumuloStrategy]):
        self._strategies = strategies

    def executar_validacoes(
        self,
        cpf: str,
        bolsista_id_ignorar: int = None,
        candidatura_id_ignorar: int = None,
    ) -> list[str]:
        erros = []
        kwargs = {
            'bolsista_id_ignorar': bolsista_id_ignorar,
            'candidatura_id_ignorar': candidatura_id_ignorar,
        }
        if self._strategies and not self._strategies[0].validar(cpf, **kwargs):
            erros.append("O discente já possui uma bolsa ativa.")

        if len(self._strategies) > 1 and not self._strategies[1].validar(cpf, **kwargs):
            erros.append(
                "O discente possui uma candidatura classificada (SELECIONADO) "
                "em andamento em outro processo."
            )

        return erros


class DuplicidadeMatriculaStrategy:
    """
    [NEW V10.8] Verifica se já existe um bolsista ATIVO com a mesma MATRÍCULA.
    """
    def validar(self, matricula: str, bolsista_id_ignorar: int = None) -> bool:
        if not matricula:
            return True  # Válido se estiver vazio (Soft Warning se aplica ao preencher)

        query = Bolsista.query.filter_by(matricula=matricula, ativo=True)
        if bolsista_id_ignorar:
            query = query.filter(Bolsista.id != bolsista_id_ignorar)

        return query.first() is None
