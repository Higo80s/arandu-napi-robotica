from typing import Protocol, List
from models import Bolsista, Candidatura

class RegraAcumuloStrategy(Protocol):
    def validar(self, cpf: str, bolsista_id_ignorar: int = None) -> bool:
        """
        Retorna True se passar na validação (Não há violação).
        bolsista_id_ignorar é útil na edição (não comparar com o próprio registro).
        """
        pass

class AcumuloBolsaAtivaStrategy:
    """
    Verifica se JÁ EXISTE uma bolsa ATIVA correndo para este CPF (excluindo a própria se for edição).
    """
    def validar(self, cpf: str, bolsista_id_ignorar: int = None) -> bool:
        query = Bolsista.query.filter_by(cpf=cpf, ativo=True)
        if bolsista_id_ignorar:
            query = query.filter(Bolsista.id != bolsista_id_ignorar)
            
        bolsa_ativa = query.first()
        return bolsa_ativa is None # Só é válido se retornar None

class AcumuloProcessoSeletivoStrategy:
    """
    Verifica se o candidato está convocado/selecionado em outro processo aberto, 
    indicando concomitância indesejada.
    """
    def validar(self, cpf: str, bolsista_id_ignorar: int = None) -> bool:
        # Busca candidaturas do CPF onde status indica seleção ou convocação ativas.
        # Aqui, vamos considerar 'SELECIONADO' e 'CONVOCADO'
        candidatura_bloqueante = Candidatura.query.filter(
            Candidatura.cpf == cpf,
            Candidatura.status.in_(['SELECIONADO', 'CONVOCADO'])
        ).first()
        return candidatura_bloqueante is None

class ValidadorAcumuloContext:
    def __init__(self, strategies: List[RegraAcumuloStrategy]):
        self._strategies = strategies
        
    def executar_validacoes(self, cpf: str, bolsista_id_ignorar: int = None) -> list[str]:
        erros = []
        if self._strategies and not self._strategies[0].validar(cpf, bolsista_id_ignorar):
            erros.append("O discente já possui uma bolsa ativa.")
            
        if len(self._strategies) > 1 and not self._strategies[1].validar(cpf, bolsista_id_ignorar):
            erros.append("O discente possui uma candidatura classificada (SELECIONADO) em andamento.")
            
        return erros

class DuplicidadeMatriculaStrategy:
    """
    [NEW V10.8] Verifica se já existe um bolsista ATIVO com a mesma MATRÍCULA.
    """
    def validar(self, matricula: str, bolsista_id_ignorar: int = None) -> bool:
        if not matricula:
            return True # Válido se estiver vazio (Soft Warning se aplica ao preencher)
            
        query = Bolsista.query.filter_by(matricula=matricula, ativo=True)
        if bolsista_id_ignorar:
            query = query.filter(Bolsista.id != bolsista_id_ignorar)
            
        return query.first() is None
