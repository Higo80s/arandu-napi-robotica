
from app import app, db
from models import Bolsista
from dateutil.relativedelta import relativedelta

def check_consistency():
    with app.app_context():
        # Try to find James
        james = Bolsista.query.filter(Bolsista.nome.ilike('%James%')).first()
        if james:
            print(f"--- Fichas encontrados: {james.nome} ---")
            print(f"Início: {james.data_inicio_bolsa}")
            print(f"Duração: {james.meses_duracao}")
            print(f"Fim (DB): {james.data_fim_bolsa}")
            
            # Calculate Expected
            # Formula: IB + (D-1) months + Suspension
            # Let's assume 0 suspension for basic check, or check his afastamentos
            suspension = 0
            for a in james.afastamentos:
                if a.tipo in ['trancamento', 'saude', 'pdse']:
                    suspension += a.duracao_meses
            
            expected_end = james.data_inicio_bolsa + relativedelta(months=(james.meses_duracao - 1 + suspension))
            
            print(f"Fim (Calculado): {expected_end}")
            
            if james.data_fim_bolsa != expected_end:
                print(">> ERRO: INCONSISTÊNCIA DETECTADA <<")
            else:
                print(">> DADOS CONSISTENTES <<")
        else:
            print("James não encontrado. Verificando todos...")
            
        # Check ALL
        all_b = Bolsista.query.all()
        inconsistent = 0
        for b in all_b:
            suspension = 0
            for a in b.afastamentos:
                 if a.tipo in ['trancamento', 'saude', 'pdse']:
                    suspension += a.duracao_meses
            expected = b.data_inicio_bolsa + relativedelta(months=(b.meses_duracao - 1 + suspension))
            
            # Month/Year Precision Logic? 
            # If user uses relaxed validation, maybe they manually set dates slightly differently?
            # But "Calculated" suggests strict math.
            
            if b.data_fim_bolsa != expected:
                inconsistent += 1
                if inconsistent <= 5: # Print first 5
                    print(f"Inc: {b.nome} | DB: {b.data_fim_bolsa} | Calc: {expected}")
        
        print(f"Total Inconsistentes: {inconsistent} de {len(all_b)}")

if __name__ == "__main__":
    check_consistency()
