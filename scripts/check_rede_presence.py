import sys
import os
from sqlalchemy import func

# Contexto da Aplicação
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, db
from models import BolsaVolumetriaAnual, ProgramaAcademico

def run():
    with app.app_context():
        # Check for REDE programs
        siglas_rede = ['PROFMAT', 'PROFIS', 'PROFÁGUA', 'PROFQUI', 'PROFIAP', 'PROFNIT', 'PROFEPT', 'MNPEF']
        
        print("--- Verificando Presença de Programas em Rede ---")
        count = 0
        for sigla in siglas_rede:
            prog = ProgramaAcademico.query.filter_by(sigla_programa=sigla).first()
            if prog:
                qtd = BolsaVolumetriaAnual.query.filter_by(programa_id=prog.id).count()
                print(f"{sigla}: {qtd} registros")
                count += qtd
            else:
                print(f"{sigla}: Programa não encontrado no banco")
                
        if count == 0:
            print("\nNenhum dado de rede importado via Excel.")
        else:
             print(f"\nTotal de registros de rede encontrados: {count}")

if __name__ == '__main__':
    run()
