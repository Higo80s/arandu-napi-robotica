"""
SERVIÇO DE RECONCILIAÇÃO DE BOLSISTAS (v10.9)
==============================================

Implementa a lógica de merge entre registros Acadêmicos (identidade) e
CAPES (vínculo de fomento), com checagem de Titulação Antecipada.
"""

from datetime import datetime
from extensions import db
from models import Bolsista
from core.memento import BolsistaCaretaker

_caretaker = BolsistaCaretaker()


def check_titulacao_conflito(bolsista: Bolsista) -> bool:
    """
    Verifica se a defesa já ocorreu antes do fim previsto da bolsa.
    Retorna True se houver conflito (possível pagamento indevido).
    """
    if bolsista.previsao_defesa and bolsista.data_fim_bolsa:
        return bolsista.previsao_defesa < bolsista.data_fim_bolsa
    return False


def get_conflitos() -> list:
    """
    [V10.9] Retorna todos os grupos de CPF com múltiplos registros.
    Cada grupo representa um conflito de identidade a ser resolvido.
    """
    from sqlalchemy import func

    # Encontrar CPFs que aparecem mais de uma vez
    cpfs_duplicados = (
        db.session.query(Bolsista.cpf)
        .group_by(Bolsista.cpf)
        .having(func.count(Bolsista.cpf) > 1)
        .all()
    )
    cpfs = [r[0] for r in cpfs_duplicados if r[0]]

    grupos = []
    for cpf in cpfs:
        registros = Bolsista.query.filter_by(cpf=cpf).order_by(
            Bolsista.ativo.desc(), Bolsista.data_inicio_bolsa.desc()
        ).all()

        tem_conflito_titulacao = any(check_titulacao_conflito(b) for b in registros)

        grupos.append({
            "cpf": cpf,
            "registros": registros,
            "conflito_titulacao": tem_conflito_titulacao,
            "total": len(registros)
        })

    return grupos


def reconcile_merge(academic_id: int, capes_id: int) -> tuple[bool, str]:
    """
    [V10.9] Merge: Absorve a IDENTIDADE do registro acadêmico no registro CAPES.
    O registro CAPES mantém o vínculo de fomento (vigência, edital).
    O registro acadêmico é desativado (soft delete).
    """
    snapshot_id = _caretaker.create_database_snapshot(
        f"Merge Académico ID={academic_id} + CAPES ID={capes_id}"
    )

    try:
        academic = Bolsista.query.get(academic_id)
        capes = Bolsista.query.get(capes_id)

        if not academic or not capes:
            return False, "Registros não encontrados."

        # Injetar identidade acadêmica no registro CAPES (vínculo oficial)
        if academic.matricula:
            capes.matricula = academic.matricula
        if academic.nome:
            capes.nome = academic.nome
        if academic.email and "@alunos" in (academic.email or ""):
            capes.email = academic.email
        if academic.previsao_defesa:
            capes.previsao_defesa = academic.previsao_defesa

        # Soft-delete do registro acadêmico redundante
        academic.ativo = False
        academic.motivo_desligamento = (
            f"Registro mesclado com ID={capes.id} em {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        )
        academic.data_desligamento = datetime.today().date()

        db.session.commit()
        return True, f"Mesclagem concluída. RA '{capes.matricula}' injetado no registro ID={capes.id}."

    except Exception as e:
        db.session.rollback()
        _caretaker.restore_from_snapshot(snapshot_id)
        return False, f"Erro crítico na mesclagem. Snapshot {snapshot_id} restaurado: {str(e)}"


def reconcile_keep_one(keep_id: int, discard_id: int) -> tuple[bool, str]:
    """
    [V10.9] Mantém apenas UMA versão, descartando o duplicado.
    """
    snapshot_id = _caretaker.create_database_snapshot(
        f"Keep ID={keep_id}, Discard ID={discard_id}"
    )

    try:
        discard = Bolsista.query.get(discard_id)
        if not discard:
            return False, "Registro a descartar não encontrado."

        discard.ativo = False
        discard.motivo_desligamento = (
            f"Duplicado de ID={keep_id}. Inativado em {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        )
        discard.data_desligamento = datetime.today().date()

        db.session.commit()
        return True, f"Registro ID={discard_id} inativado. Registro ID={keep_id} mantido como oficial."

    except Exception as e:
        db.session.rollback()
        _caretaker.restore_from_snapshot(snapshot_id)
        return False, f"Erro ao inativar. Snapshot {snapshot_id} restaurado: {str(e)}"
