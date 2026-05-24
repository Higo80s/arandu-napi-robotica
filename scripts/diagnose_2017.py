import sys
import os
from sqlalchemy import func

# Contexto da Aplicação
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, db
from models import BolsaVolumetriaAnual, ProgramaAcademico

def run():
    with app.app_context():
        # Lista de siglas ampliada
        siglas_rede = ['PROFMAT', 'PROFIS', 'ProfÁgua', 'PROFQUI', 'PROFIAP', 'PROFNIT', 'PROFEPT', 'MNPEF']
        
        # Mapa de IDs de programas REDE
        prog_ids = []
        for p in ProgramaAcademico.query.all():
            if p.sigla_programa in siglas_rede:
                prog_ids.append(p.id)
                
        output = []
        output.append("--- DETALHAMENTO 2017 (REDE) ---")
        
        results = db.session.query(
            BolsaVolumetriaAnual.programa_id, 
            BolsaVolumetriaAnual.qtd_sistema
        ).filter(
            BolsaVolumetriaAnual.programa_id.in_(prog_ids),
            BolsaVolumetriaAnual.ano_referencia == 2021,
            BolsaVolumetriaAnual.nivel == 'Mestrado'
        ).all()
        
        total = 0
        for r in results:
            prog = ProgramaAcademico.query.get(r[0])
            line = f"Prog: {prog.sigla_programa} ({prog.nome_programa}) - Campus: {prog.campus.sigla_campus} | Qtd: {r[1]}"
            output.append(line)
            total += r[1]
            
        output.append(f"Total Banco: {total}")
        
        with open("diagnosis_2021.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(output))
            print("Salvo em diagnosis_2021.txt")

if __name__ == '__main__':
    run()
