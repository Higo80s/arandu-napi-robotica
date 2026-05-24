
from datetime import date
from dateutil.relativedelta import relativedelta

def validate_lax(end_date, limit_date):
    print(f"Testing: End={end_date} vs Limit={limit_date}")
    limit_tuple = (limit_date.year, limit_date.month)
    end_tuple = (end_date.year, end_date.month)
    
    if end_tuple > limit_tuple:
        return "ERROR"
    return "SUCCESS"

print("--- Teste de Validação Relaxada (Mês/Ano) ---")

# Caso do Usuário: Dia 02 vs Dia 01 (Mesmo Mês)
end = date(2026, 1, 2)
limit = date(2026, 1, 1)
res = validate_lax(end, limit)
print(f"Caso 1 (2 Jan vs 1 Jan): {res} [Esperado: SUCCESS]")

# Caso Realmente Inválido: Mês Seguinte
end2 = date(2026, 2, 1)
res2 = validate_lax(end2, limit)
print(f"Caso 2 (1 Fev vs 1 Jan): {res2} [Esperado: ERROR]")

# Caso Limite: Ano Seguinte
end3 = date(2027, 1, 1)
res3 = validate_lax(end3, limit)
print(f"Caso 3 (1 Jan 27 vs 1 Jan 26): {res3} [Esperado: ERROR]")
