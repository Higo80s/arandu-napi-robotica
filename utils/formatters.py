import re
from datetime import datetime

def converter_data_br_para_iso(data_str):
    """
    Converte 'DD/MM/AAAA' para 'YYYY-MM-DD'.
    Essencial para preencher inputs HTML5 e campos DATE do PostgreSQL.
    """
    if not data_str:
        return ""
    
    try:
        # Remove espaços em branco e caracteres invisíveis
        data_limpa = data_str.strip()
        # Tenta o parsing no formato brasileiro
        obj_data = datetime.strptime(data_limpa, '%d/%m/%Y')
        return obj_data.strftime('%Y-%m-%d')
    except (ValueError, TypeError):
        # Retorna vazio para evitar que o frontend exiba 'None' ou datas inválidas
        return ""

def sanitizar_nome(nome_str):
    """
    Padroniza nomes para UPPERCASE e remove espaços extras.
    Mantém a consistência visual nos relatórios da PROPPG.
    """
    if not nome_str:
        return ""
    # Converte para maiúsculas e remove espaços no início/fim e duplos no meio
    return " ".join(nome_str.strip().upper().split())

def sanitizar_cpf(cpf_str):
    """
    Remove pontos, traços e espaços, mantendo apenas os 11 dígitos.
    Garante que a busca por CPF no banco de dados seja sempre exata.
    """
    if not cpf_str:
        return ""
    # Regex para manter apenas dígitos
    return re.sub(r'\D', '', cpf_str)

def formatar_agencia_conta(valor_str):
    """
    Remove caracteres não alfanuméricos de agências e contas, 
    preservando apenas letras e números (útil para bancos com dígito 'X').
    """
    if not valor_str:
        return ""
    # Remove tudo que não for letra ou número
    return re.sub(r'[^a-zA-Z0-9]', '', valor_str).upper()

def normalizar_edital(edital_str):
    """
    Sanitiza o número do edital: remove espaços extras, converte para UPPERCASE
    e padroniza separadores para evitar duplicações de hifens.
    Ex: ' edital 01 / 2024 ' -> 'EDITAL-01/2024'
    """
    if not edital_str:
        return ""
    
    # Converte para maiúsculo e remove espaços nas extremidades
    limpo = edital_str.upper().strip()
    
    # Remove espaços ao redor de separadores comuns (/ e -)
    limpo = re.sub(r'\s*/\s*', '/', limpo)
    limpo = re.sub(r'\s*-\s*', '-', limpo)
    
    # Substitui espaços remanescentes por hifens
    limpo = re.sub(r'\s+', '-', limpo)
    
    # Reduz sequências de hifens para um único hífen (ex: --- -> -)
    limpo = re.sub(r'-+', '-', limpo)
    
    return limpo
