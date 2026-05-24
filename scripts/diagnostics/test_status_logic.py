
from app import app
from models import Bolsista
from datetime import date, timedelta

# Mock dates
today = date.today()
yesterday = today - timedelta(days=1)
next_month = today + timedelta(days=60)
current_month_end = date(today.year, today.month, 28) # Approximate

class MockBolsista:
    def __init__(self, data_fim, ativo=True):
        self.data_fim_bolsa = data_fim
        self.ativo = ativo
    
    # Copy logic from model for unit testing without DB overhead if desired, 
    # OR better: use the actual method if I can import it? 
    # I can't easily attach the method to a mock object without monkeypatching.
    # So I will test the Model Logic by creating instances in memory if possible?
    # SQLAlchemy models usually need DB session but method check_status_validity is pure logic.
    # Let's import the class and use it.

    def check_status_validity(self):
        # Replicating logic or borrowing from Class? 
        # Easier to just verify the logic I wrote:
        # 1. Expiration
        if self.ativo and self.data_fim_bolsa < today:
            return 'INATIVO'
        # 2. Warning
        if self.ativo:
            if self.data_fim_bolsa.year == today.year and self.data_fim_bolsa.month == today.month:
                return 'FINALIZANDO'
        return 'ATIVO'

print("--- Teste de Lógica de Status ---")

# Caso 1: Vencido
b1 = MockBolsista(yesterday)
print(f"Bolsista Vencido ({yesterday}): {b1.check_status_validity()} [Esperado: INATIVO]")

# Caso 2: Finalizando (Mesmo mês)
b2 = MockBolsista(today) # Hoje ainda é ativo, mas está finalizando pois é o mês de fim?
# Se fim = hoje, ainda é ativo? Sim. Mas é "Finalizando" se estiver no mês.
print(f"Bolsista Finalizando Hoje ({today}): {b2.check_status_validity()} [Esperado: FINALIZANDO]")

# Caso 3: Futuro (Ativo)
b3 = MockBolsista(next_month)
print(f"Bolsista Futuro ({next_month}): {b3.check_status_validity()} [Esperado: ATIVO]")

# Caso 4: Já Inativo Banco
b4 = MockBolsista(next_month, ativo=False)
# Logica: if self.ativo...
# models.py says: if self.ativo and expired -> Inativo.
# if not self.ativo -> Returns 'ATIVO'?? Wait.
# My logic in models.py was:
# if self.ativo and expired: return INATIVO
# if self.ativo: check warning...
# return ATIVO
# ERROR: If self.ativo is False, it returns 'ATIVO'. That is WRONG.
# FIX NEEDED in models.py
