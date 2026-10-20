"""Helpers de escopo Fundação Araucária (FA)."""


def _texto_indica_fa(raw) -> bool:
    if not raw:
        return False
    s = str(raw).lower().strip()
    if s == 'fa':
        return True
    return 'arauc' in s or 'funtef' in s


def is_bolsista_araucaria(bolsista) -> bool:
    """True se agencia_fomento ou Edital.agencia indica Fundação Araucária."""
    if bolsista is None:
        return False
    if _texto_indica_fa(getattr(bolsista, 'agencia_fomento', None)):
        return True
    edital = getattr(bolsista, 'edital', None)
    if edital and _texto_indica_fa(getattr(edital, 'agencia', None)):
        return True
    return False


def is_edital_araucaria(edital) -> bool:
    return bool(edital and _texto_indica_fa(getattr(edital, 'agencia', None)))
