
from datetime import date
from dateutil.relativedelta import relativedelta

# REPLICATING LOGIC FROM APP.PY
def check_bolsa_logic(ic_str, ib_str, m_months, d_duration):
    # Inputs
    IC = date.fromisoformat(ic_str)
    IB = date.fromisoformat(ib_str)
    M = m_months
    D = d_duration
    
    print(f"\n--- TESTING: IC={IC}, IB={IB}, M={M}, D={D} ---")

    # 1. Precedence IB >= IC
    if IB < IC:
        print("FAIL: IB < IC")
        return "ERROR_PRECEDENCE"

    # 2. Fatal Limit
    # Limit = IC + M - 1 month.
    limit_date = IC + relativedelta(months=M)
    limit_date = limit_date - relativedelta(months=1)
    
    print(f"CALC: Limit Date = {limit_date}")

    # 3. End Date
    # End = IB + (D - 1) months
    end_date = IB + relativedelta(months=(D - 1))
    print(f"CALC: End Date = {end_date}")

    # 4. Validation
    if end_date > limit_date:
        print(f"FAIL: End ({end_date}) > Limit ({limit_date})")
        return "ERROR_LIMIT"
    
    if D > M:
        print(f"FAIL: D ({D}) > M ({M})")
        return "ERROR_MAX"

    print("SUCCESS: Valid.")
    return "OK"

# SCENARIOS FROM USER SPEC
# M = 24 (Mestrado)
# Cenario 1: IC=01/05/2025, IB=01/05/2025, D=24. Result: OK. End=01/04/2027.
r1 = check_bolsa_logic("2025-05-01", "2025-05-01", 24, 24)

# Cenario 2: IC=01/05/2025, IB=01/06/2025, D=24. Result: ERROR (End=01/05/2027 > Limit 01/04/2027).
r2 = check_bolsa_logic("2025-05-01", "2025-06-01", 24, 24)

# Cenario 3: IC=01/05/2025, IB=01/06/2025, D=12. Result: OK. End=01/05/2026.
r3 = check_bolsa_logic("2025-05-01", "2025-06-01", 24, 12)

# Cenario 4: IC=01/05/2025, IB=01/05/2026, D=12. Result: OK. End=01/04/2027.
r4 = check_bolsa_logic("2025-05-01", "2026-05-01", 24, 12)

# Assertion
print("\n--- REPORT ---")
if r1 == "OK": print("Scenario 1: PASS") 
else: print("Scenario 1: FAILED")

if r2 == "ERROR_LIMIT": print("Scenario 2: PASS (Correctly Blocked)") 
else: print(f"Scenario 2: FAILED (Expected ERROR_LIMIT, got {r2})")

if r3 == "OK": print("Scenario 3: PASS") 
else: print("Scenario 3: FAILED")

if r4 == "OK": print("Scenario 4: PASS") 
else: print("Scenario 4: FAILED")
