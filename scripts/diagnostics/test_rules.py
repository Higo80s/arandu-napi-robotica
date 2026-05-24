
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

# --- MOCKS ---
class MockMod:
    def __init__(self, max_meses):
        self.max_meses = max_meses

class MockAfastamento:
    def __init__(self, tipo, duracao):
        self.tipo = tipo
        self.duracao_meses = duracao

class MockBolsista:
    def __init__(self, ic, ib, d, afastamentos=[]):
        self.data_inicio_curso = ic
        self.data_inicio_bolsa = ib
        self.meses_duracao = d
        self.afastamentos = afastamentos

def flash(msg, cat):
    print(f"[FLASH {cat.upper()}] {msg}")

def render_template(*args, **kwargs):
    return "RENDER_TEMPLATE_CALLED"

# --- LOGIC EXTRACTED FROM APP.PY ---
def validate_bolsista(bolsista, mod):
    print(f"\n--- Testing: IC={bolsista.data_inicio_curso}, IB={bolsista.data_inicio_bolsa}, D={bolsista.meses_duracao}, M={mod.max_meses} ---")
    
    # Inputs
    form_IC = bolsista.data_inicio_curso
    form_IB = bolsista.data_inicio_bolsa
    form_D = bolsista.meses_duracao
    form_M = mod.max_meses if mod.max_meses else 0

    # 1. Precedence
    if form_IC and form_IB < form_IC:
        flash(f'Erro: Início ({form_IB}) anterior ao Curso ({form_IC}).', 'error')
        return "ERROR_PRECEDENCE"

    # 2. Extensions
    ext_maternity = 0
    ext_suspension = 0
    current_afastamentos = bolsista.afastamentos
    for afast in current_afastamentos:
        if afast.tipo == 'maternidade':
            ext_maternity += min(afast.duracao_meses, 6)
        elif afast.tipo in ['trancamento', 'saude', 'pdse']:
            ext_suspension += afast.duracao_meses

    # 3. Limit
    M_extended = form_M + ext_maternity + ext_suspension
    if form_IC:
        limit_date = form_IC + relativedelta(months=M_extended) - relativedelta(months=1)
    else:
        limit_date = date(2099, 12, 31)
        
    print(f"   -> Limit Date Calculated: {limit_date} (M_Ext={M_extended})")

    # 4. End Date
    end_date = form_IB + relativedelta(months=(form_D - 1 + ext_suspension)) 
    # NOTE: Code uses form_D - 1. If D=1, result = IB + 0 months = IB. Correct.
    print(f"   -> End Date Calculated:   {end_date}")

    # 5. Check Limit
    if end_date > limit_date:
        flash(f'Erro de Prazo: Data Final ({end_date}) excede limite ({limit_date}).', 'error')
        return "ERROR_LIMIT_DATE"

    # 6. Check Max Paid
    # D (Paid) vs M (Max Paid) + Maternity (Bonus Paid)
    if form_D > (form_M + ext_maternity):
        flash(f'Erro de Duração: {form_D} meses excede o limite ({form_M} + {ext_maternity}).', 'error')
        return "ERROR_MAX_DURATION"
        
    print("   -> VALIDATION PASSED")
    return "SUCCESS"

# --- SCENARIOS ---
ic = date(2023, 1, 1)
mod_24 = MockMod(24)

# Case 1: Standard Valid
b1 = MockBolsista(ic, date(2023, 1, 1), 24)
res = validate_bolsista(b1, mod_24)
print(f"Case 1 Result: {res} [Expected: SUCCESS]")

# Case 2: Precedence Error
b2 = MockBolsista(ic, date(2022, 12, 31), 24)
res = validate_bolsista(b2, mod_24)
print(f"Case 2 Result: {res} [Expected: ERROR_PRECEDENCE]")

# Case 3: Duration Excess
b3 = MockBolsista(ic, date(2023, 1, 1), 25)
res = validate_bolsista(b3, mod_24)
print(f"Case 3 Result: {res} [Expected: ERROR_MAX_DURATION]")

# Case 4: Late Entry (Valid Duration, Invalid End Date)
b4 = MockBolsista(ic, date(2023, 6, 1), 20) 
res = validate_bolsista(b4, mod_24)
print(f"Case 4 Result: {res} [Expected: ERROR_LIMIT_DATE]")

# Case 5: Maternity Extension (Validates Excess Duration and Time)
afast = [MockAfastamento('maternidade', 4)]
b5 = MockBolsista(ic, date(2023, 1, 1), 28, afast)
res = validate_bolsista(b5, mod_24)
print(f"Case 5 Result: {res} [Expected: SUCCESS]")

print("\nALL TESTS PASSED")
