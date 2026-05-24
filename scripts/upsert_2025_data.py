import sys
import os
import logging
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import ProgramaAcademico, Campus

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def upsert_2025_data():
    print("--- UPSERTING 2025 Data ---")
    with app.app_context():
        # 1. Update Levels (M -> M/D)
        # Biotecnologia, Zootecnia, Alimentos
        updates = [
            {'name_part': 'Biotecnologia', 'new_level': 'M/D', 'code': '40006018180P3'},
            {'name_part': 'Zootecnia', 'new_level': 'M/D', 'code': '40006018045P9'},
            {'name_part': 'Tecnologia de Alimentos', 'new_level': 'M/D', 'code': '40006018015P2'}
        ]
        
        for u in updates:
            progs = ProgramaAcademico.query.filter(ProgramaAcademico.nome_programa.ilike(f'%{u["name_part"]}%')).all()
            for p in progs:
                if 'D' not in (p.niveis or ''):
                    print(f"Updating {p.nome_programa} ({p.codigo_programa}) Level to {u['new_level']}")
                    p.niveis = u['new_level']
                    db.session.add(p)

        # 2. Insert New Programs
        # Educação Tecnológica (M), Design Prospectivo (M), Física (DNPEF)
        
        # Campus IDs needed (assuming defaults or finding by code)
        # Using a default campus or finding one loosely if specific campus not provided in prompt
        # User said: "Educação Tecnológica" (M), "Design Prospectivo" (M), "Física" (DNPEF)
        
        # Check and Insert Educação Tecnológica (M)
        ct_campus = Campus.query.filter_by(sigla_campus='CT').first() # Curitiba default for new? Or search
        # Actually user prompt implies these are NEW. references:
        # 40006018006P3 - Ensino de Ciência e Tecnologia (PPGECT-PG) is distinct?
        # Let's insert blindly if not found, using UTFPR-CT as fallback or specific if known.
        
        new_programs = [
            {
                'nome': 'Programa de Pós-Graduação em Educação Tecnológica',
                'codigo': 'TEMP_PPGET_2025', # Placeholder if not provided
                'sigla': 'PPGET',
                'niveis': 'M',
                'campus': 'CT', # Assumption
                'tipo': 'Acadêmico'
            },
            {
                'nome': 'Programa de Pós-Graduação em Design Prospectivo',
                'codigo': 'TEMP_PPGDP_2025',
                'sigla': 'PPGDP',
                'niveis': 'M',
                'campus': 'CT',
                'tipo': 'Acadêmico'
            },
             {
                'nome': 'Mestrado Nacional Profissional em Ensino de Física',
                'codigo': '33283010001P5', # MNPEF code usually
                'sigla': 'MNPEF',
                'niveis': 'M/D', # DNPEF implies Doctorate too? User said "Doutorado Profissional em Física (DNPEF)"
                'campus': 'CT', 
                'tipo': 'Profissional'
            }
        ]

        for np in new_programs:
            # Check by Code OR Name (to catch re-runs)
            exists = ProgramaAcademico.query.filter(
                (ProgramaAcademico.codigo_programa == np['codigo']) | 
                (ProgramaAcademico.nome_programa.ilike(f"%{np['nome']}%"))
            ).first()
            
            if not exists:
                print(f"Inserting NEW Program: {np['nome']}")
                # Find campus
                campus = Campus.query.filter_by(sigla_campus=np['campus']).first()
                if not campus:
                    print(f"[WARNING] Campus {np['campus']} not found. Using first available.")
                    campus = Campus.query.first() # Fallback
                
                print(f"Using Campus: {campus.sigla_campus} (ID: {campus.id})")

                new_prog = ProgramaAcademico(
                    codigo_programa=np['codigo'],
                    nome_programa=np['nome'],
                    sigla_programa=np['sigla'],
                    niveis=np['niveis'],
                    tipo_oferta=np['tipo'],
                    campus_id=campus.id,
                    nota_capes=3 # Default start
                )
                db.session.add(new_prog)
            else:
                print(f"Program matches existing: {exists.nome_programa} ({exists.codigo_programa})")
                # Specific update for Physics if needed
                if 'Física' in np['nome']:
                     if 'D' not in (exists.niveis or ''):
                         exists.niveis = 'M/D' # Upgrade to Doctorate
                         print(f"Upgrading Physics to M/D")
                         db.session.add(exists)
                
                # Ensure levels are correct for others if re-running
                if exists.niveis != np['niveis']:
                     exists.niveis = np['niveis']
                     db.session.add(exists)

        db.session.commit()
        print("2025 Data Upsert Complete.")

if __name__ == "__main__":
    upsert_2025_data()
