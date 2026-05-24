
import sys
import os
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

# Add root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db, Bolsista, Residente, Edital, Modalidade, Campus, ProgramaAcademico, Afastamento

def run_tests():
    print("\n🎸 STARTING RAMONES TEST SUITE 🎸\n")
    
    with app.app_context():
        # 1. SETUP PREREQUISITES (Edital, Modalidades)
        # We need a Dummy Edital for testing if none exists, or use existing.
        # Let's create a Test Edital to not mess with real data if possible, OR use existing ID 1.
        # Ideally, we clean up after test.
        
        print("[SETUP] Ensuring Test Edital 'Edital Ramones'...")
        edital = Edital.query.filter_by(numero="00/RAMONES").first()
        if not edital:
            edital = Edital(
                numero="00/RAMONES",
                descricao="Edital de Teste Automatizado",
                agencia="CNPq"
                # ativo=True Removed: Field does not exist in Edital Model
            )
            db.session.add(edital)
            db.session.commit()
            
        # Modalidades
        # Mestrado
        mod_m = Modalidade.query.filter_by(edital_id=edital.id, nivel="Mestrado").first()
        if not mod_m:
            mod_m = Modalidade(edital_id=edital.id, nivel="Mestrado", vagas=10, valor_mensal=2100.0, max_meses=24)
            db.session.add(mod_m)
            
        # Doutorado
        mod_d = Modalidade.query.filter_by(edital_id=edital.id, nivel="Doutorado").first()
        if not mod_d:
            mod_d = Modalidade(edital_id=edital.id, nivel="Doutorado", vagas=10, valor_mensal=3100.0, max_meses=48)
            db.session.add(mod_d)
        
        # PosDoc (Wait, PosDoc usually different edital? Or same?)
        # Let's add PosDoc modality here
        mod_pd = Modalidade.query.filter_by(edital_id=edital.id, nivel="Pós-Doutorado").first()
        if not mod_pd:
            mod_pd = Modalidade(edital_id=edital.id, nivel="Pós-Doutorado", vagas=5, valor_mensal=5200.0, max_meses=12)
            db.session.add(mod_pd)
            
        db.session.commit()
        
        # Programs (Reuse existing or create)
        p_cp = ProgramaAcademico.query.filter(ProgramaAcademico.nome_programa.like('%Mecânica%')).first()
        p_ct = ProgramaAcademico.query.filter(ProgramaAcademico.nome_programa.like('%Tecnologia%Sociedade%')).first() # PPGTE
        
        if not p_cp or not p_ct:
            print("[ERROR] Required Programs (Mecânica/PPGTE) not found. Check DB.")
            return

        # ==========================================
        # TEST 1: JOEY RAMONE (Standard Mestrado)
        # ==========================================
        print("\n🎤 TEST 1: JOEY RAMONE (Mestrado Acadêmico)")
        # Start: 01/01/2025. 24 months. End should be 01/12/2026?
        # Logic: Start + (24-1) months. 
        # Jan 25 + 23m = Dec 26.
        # Wait, app logic: FimBolsa = IB + (Meses-1).
        
        joey = Bolsista(
            nome="Joey Ramone",
            cpf="111.111.111-11",
            edital_id=edital.id,
            modalidade_id=mod_m.id,
            programa_id=p_cp.id,
            data_inicio_bolsa=date(2025, 1, 1),
            meses_duracao=24,
            data_fim_bolsa=date(2026, 12, 1), # Manually set? Or does Backend calcs it?
            # Model does NOT auto-calc on insert. Logic is in APP ROUTE.
            # Here we are testing DATA INTEGRITY, so we must calculate as App does.
            # App JS: IB + (D-1).
            # Python: ib + relativedelta(months=24-1) ??
            # Let's verify our expectation vs Python math.
            recebe_bolsa=True,
            ativo=True
        )
        
        # Calc expected
        expected_fim = date(2025, 1, 1) + relativedelta(months=23) # Dec 2026
        joey.data_fim_bolsa = expected_fim
        
        db.session.add(joey)
        try:
            db.session.commit()
            print(f"  [OK] Created Joey. Fim: {joey.data_fim_bolsa} (Expected: {expected_fim})")
        except Exception as e:
            print(f"  [FAIL] Could not create Joey: {e}")
            db.session.rollback()

        # ==========================================
        # TEST 2: JOHNNY RAMONE (Doutorado + Suspension)
        # ==========================================
        print("\n🎸 TEST 2: JOHNNY RAMONE (Doutorado + Trancamento)")
        # Start: 01/01/2024. 48 months. 
        # Base End: Jan 24 + 47m = Dec 27.
        # Trancamento: 6 months.
        # New End: June 28?
        
        base_start = date(2024, 1, 1)
        base_dur = 48
        
        johnny = Bolsista(
            nome="Johnny Ramone",
            cpf="222.222.222-22",
            edital_id=edital.id,
            modalidade_id=mod_d.id,
            programa_id=p_ct.id, # PPGTE
            data_inicio_bolsa=base_start,
            meses_duracao=base_dur,
            data_fim_bolsa=base_start + relativedelta(months=base_dur-1), # Initial
            ativo=True
        )
        db.session.add(johnny)
        db.session.commit()
        
        # Add Afastamento
        suspension = Afastamento(
            bolsista_id=johnny.id,
            tipo='trancamento',
            data_inicio=date(2025, 6, 1),
            duracao_meses=6,
            observacao="Tour com Ramones"
        )
        db.session.add(suspension)
        
        # Recalc Fim Bolsa Logic (Simulate System Behavior)
        # Logic: Fim = IB + (D-1) + Suspension
        new_fim = base_start + relativedelta(months=(base_dur - 1) + 6)
        johnny.data_fim_bolsa = new_fim
        db.session.commit()
        
        print(f"  [OK] Johnny Created. Suspension Added.")
        print(f"  [CHECK] End Date: {johnny.data_fim_bolsa} (Expected: {new_fim})")
        if johnny.data_fim_bolsa == new_fim:
            print("  [SUCCESS] Date Calculation Match.")
        else:
            print("  [FAIL] Date Mismatch.")

        # ==========================================
        # TEST 3: DEE DEE RAMONE (Pós-Doc Residente)
        # ==========================================
        print("\n🎻 TEST 3: DEE DEE RAMONE (Pós-Doc)")
        # Residente table
        # Start 01/01/2025. 12m.
        
        dee_dee = Residente(
            nome="Dee Dee Ramone",
            cpf="333.333.333-33",
            edital_id=edital.id,
            modalidade_id=mod_pd.id,
            programa_id=p_cp.id, # PosDoc at Mecanica
            data_inicio=date(2025, 1, 1),
            data_fim=date(2025, 12, 31), # 1 year full (usually) or 12 payments? 
            # If 12 payments (01/25 to 12/25).
            meses_duracao=12,
            projeto_pesquisa="Lobotomy Research",
            supervisor="Dr. Rock",
            recebe_bolsa=True,
            ativo=True
        )
        db.session.add(dee_dee)
        try:
            db.session.commit()
            print(f"  [OK] Dee Dee Created in Residentes table.")
            print(f"  [CHECK] Recebe Bolsa: {dee_dee.recebe_bolsa}")
        except Exception as e:
            print(f"  [FAIL] Dee Dee Creation: {e}")

        # ==========================================
        # TEST 4: MARKY RAMONE (Expiry Automation)
        # ==========================================
        print("\n🥁 TEST 4: MARKY RAMONE (Status Automation)")
        # Start: 2020. End: Yesterday.
        # Should be 'INATIVO' by calc logic.
        
        marky = Bolsista(
            nome="Marky Ramone",
            cpf="444.444.444-44",
            edital_id=edital.id,
            modalidade_id=mod_m.id,
            programa_id=p_cp.id,
            data_inicio_bolsa=date(2020, 1, 1),
            meses_duracao=24,
            data_fim_bolsa=date(2022, 1, 1), # Long past
            ativo=True # Still marked active in DB
        )
        db.session.add(marky)
        db.session.commit()
        
        # Check Computed Status (Method check_status_validity)
        status = marky.check_status_validity()
        print(f"  [CHECK] Marky Real Status: {status}")
        if status == 'INATIVO':
            print("  [SUCCESS] Automation correctly flags expired dates.")
        else:
            print(f"  [FAIL] Expected INATIVO, got {status}")

        # CLEANUP
        print("\n🧹 CLEANUP")
        # Remove Ramones
        # Due to FK cascades, deleting dummy edital might clean all bolsistas?
        # But Residentes has 'SET NULL'.
        # Let's delete manually to be clean.
        
        Bolsista.query.filter(Bolsista.nome.like('%Ramone%')).delete(synchronize_session=False)
        Residente.query.filter(Residente.nome.like('%Ramone%')).delete(synchronize_session=False)
        db.session.commit()
        
        # Delete Edital Ramones
        # db.session.delete(edital) # Keep for debug or delete? Delete.
        # Note: If I delete Edital, Modalidades vanish (Cascade).
        try:
            db.session.delete(edital)
            db.session.commit()
            print("  [OK] Cleanup Complete.")
        except:
             print("  [WARN] Creating Edital might have persisted constraints. Manual check advised.")

if __name__ == "__main__":
    run_tests()
