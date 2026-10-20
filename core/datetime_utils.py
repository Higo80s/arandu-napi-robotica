"""Datas/horas: armazenar em UTC, exibir em America/Sao_Paulo."""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

BR_TZ = ZoneInfo('America/Sao_Paulo')
UTC = ZoneInfo('UTC')


def utc_now():
    return datetime.now(UTC).replace(tzinfo=None)


def format_datetime_br(dt):
    """Converte datetime UTC (naive) para exibicao BRT."""
    if not dt:
        return ''
    local = dt.replace(tzinfo=UTC).astimezone(BR_TZ)
    return local.strftime('%d/%m/%Y %H:%M')


def repair_comentarios_mixed_tz(session):
    """Corrige criado_em gravado 1h atras em relacao ao UTC real."""
    from models import ComentarioBolsista

    fixed = 0
    for c in ComentarioBolsista.query.all():
        if not c.criado_em or not c.atualizado_em:
            continue
        ch, ah = c.criado_em.hour, c.atualizado_em.hour
        # Ambos errados no insert (ex.: datetime local com offset errado)
        if 10 <= ch <= 12 and 10 <= ah <= 12 and abs((c.atualizado_em - c.criado_em).total_seconds()) < 120:
            c.criado_em += timedelta(hours=1)
            c.atualizado_em += timedelta(hours=1)
            fixed += 1
        # criado errado, atualizado ja em UTC apos edicao
        elif 10 <= ch <= 12 and ah >= 12 and c.atualizado_em > c.criado_em:
            c.criado_em += timedelta(hours=1)
            fixed += 1
    if fixed:
        session.commit()
    return fixed


def undo_atualizado_overcorrection(session):
    """Remove +1h indevido em atualizado_em apos reparo duplicado."""
    from models import ComentarioBolsista

    fixed = 0
    for c in ComentarioBolsista.query.all():
        if not c.criado_em or not c.atualizado_em:
            continue
        if c.atualizado_em.hour >= 13 and c.criado_em.hour == 12:
            c.atualizado_em -= timedelta(hours=1)
            fixed += 1
    if fixed:
        session.commit()
    return fixed
