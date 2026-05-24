from datetime import date, datetime
from typing import Optional, Union

def calcular_parcelas(data_inicio, data_referencia, data_desligamento=None):
    """
    Calcula o número da parcela com base na data de início e a data de referência.
    Retorna 0 se a bolsa ainda não começou.
    Retorna -1 (ou trata conforme regra) se já terminou/desligado (opcional).
    """
    if not data_inicio:
        return 0
    
    # Se houver desligamento e for anterior à referência, talvez não deva pagar
    # Mas a função parece apenas calcular qual seria o número da parcela
    
    # Cálculo de meses
    diff_anos = data_referencia.year - data_inicio.year
    diff_meses = data_referencia.month - data_inicio.month
    
    parcela = (diff_anos * 12) + diff_meses + 1
    
    if parcela < 1:
        return 0
        
    return parcela


# ===== HELPERS DE DATA (NOVO - FASE 2 UX/UI) =====

def parse_flexible_date(date_str: Union[str, date, None]) -> Optional[date]:
    """
    Aceita múltiplos formatos de data e retorna objeto date
    
    Formatos aceitos:
    - DD/MM/AAAA (padrão brasileiro)
    - AAAA-MM-DD (ISO, usado em input type="date")
    - DD-MM-AAAA
    - DD.MM.AAAA (Excel às vezes usa)
    - AAAA/MM/DD
    
    Args:
        date_str: String de data em qualquer formato aceito, ou None
        
    Returns:
        Objeto date ou None se conversão falhar
    """
    # Se já é date, retorna
    if isinstance(date_str, date):
        return date_str
    
    # Se None ou vazio, retorna None
    if not date_str or str(date_str).strip() == '':
        return None
    
    date_string = str(date_str).strip()
    
    # Formatos a tentar (ordem importa: mais específico primeiro)
    formats = [
        '%d/%m/%Y',   # DD/MM/AAAA (brasileiro)
        '%Y-%m-%d',   # AAAA-MM-DD (ISO)
        '%d-%m-%Y',   # DD-MM-AAAA
        '%d.%m.%Y',   # DD.MM.AAAA
        '%Y/%m/%d',   # AAAA/MM/DD
        '%d/%m/%y',   # DD/MM/AA (ano com 2 dígitos)
        '%d-%m-%y',   # DD-MM-AA
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt).date()
        except ValueError:
            continue
    
    # Se nenhum formato funcionar, tenta remover caracteres extras
    cleaned = ''.join(c for c in date_string if c.isdigit() or c in '/-.')
    if cleaned != date_string:
        return parse_flexible_date(cleaned)
    
    raise ValueError(f"Formato de data não reconhecido: '{date_str}'. Use DD/MM/AAAA")


def format_date_br(date_obj: Optional[Union[date, str]]) -> str:
    """
    Formata data para padrão brasileiro DD/MM/AAAA
    
    Args:
        date_obj: Objeto date, string de data, ou None
        
    Returns:
        String no formato DD/MM/AAAA ou '' se None
    """
    if not date_obj:
        return ''
    
    # Se é string, converte primeiro
    if isinstance(date_obj, str):
        date_obj = parse_flexible_date(date_obj)
        if not date_obj:
            return ''
    
    return date_obj.strftime('%d/%m/%Y')


def format_date_iso(date_obj: Optional[Union[date, str]]) -> str:
    """
    Formata data para padrão ISO AAAA-MM-DD (para input type="date")
    
    Args:
        date_obj: Objeto date, string de data, ou None
        
    Returns:
        String no formato AAAA-MM-DD ou '' se None
    """
    if not date_obj:
        return ''
    
    if isinstance(date_obj, str):
        date_obj = parse_flexible_date(date_obj)
        if not date_obj:
            return ''
    
    return date_obj.strftime('%Y-%m-%d')
