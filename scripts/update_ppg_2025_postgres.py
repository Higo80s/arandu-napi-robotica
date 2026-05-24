import sys
import os
import logging
from sqlalchemy import text # Fix for V11 (text() required for SQL strings)

# Add parent directory to path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import ProgramaAcademico, Campus

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Data from original script
NEW_PROGRAMS = [
    # (Code, Name, Sigla, CampusSigla, Level, AreaAv, AreaBasic, Year, Grade)
    ("40006018185P5", "Educação Tecnológica", "PPGET", "CT", "M", "Educação", "Educação", 2025, "A"),
    ("40006018184P9", "Design Prospectivo", "PPGDP", "CT", "M", "Arquitetura, Urbanismo e Design", "Design", 2025, "A"),
    ("40006018031P8", "Engenharia de Produção e Sistemas", "PPGEPS", "CT", "D", "ENGENHARIAS III", "ENGENHARIA DE PRODUÇÃO", 2025, "4"),
    ("TEMP_CC_TD_2025", "Ciência da Computação", "PPGCC", "TD", "M", "CIÊNCIA DA COMPUTAÇÃO", "CIÊNCIA DA COMPUTAÇÃO", 2025, "3"),
    ("33283010001P5", "Ensino de Física - PROFIS (Polo)", "DNPEF", "CM", "DP", "ASTRONOMIA / FÍSICA", "FÍSICA", 2025, "5"),
]

LEVEL_UPDATES = [
    ("PPGBIOTEC", "PG", "M, D"),
    ("PPGBIOTEC", "DV", "M, D"),
    ("PPGZO", "DV", "M, D"),
    ("PPGTA", "MD", "M, D"),
    ("PPGTA", "CM", "M, D"),
    ("PPGEPS", "PB", "M, D"),
    ("PPGEPS", "CT", "M, D"),
    ("PPGCTA", "CT", "M, D"),
    ("PPGEC", "CT", "M, D"),
    ("CPGEI", "CT", "M, D"),
    ("PPGEM", "CT", "M, D"),
    ("PPGFCET", "CT", "MP, DP"),
    ("PPGPGP", "CT", "MP, DP"),
    ("PPGTE", "CT", "M, D"),
    ("PPGAG", "PB", "M, D"),
    ("PPGDR", "PB", "M, D"),
    ("PPGEP", "PG", "M, D"),
    ("PPGECT", "PG", "MP, D"),
]

NOTE_UPDATES = [
    ("CPGEI", "CT", "7"),
    ("PPGTE", "CT", "6")
]

def update_ppg_postgres():
    logger.info("Starting PPG 2025 Update on PostgreSQL...")
    
    with app.app_context():
        # 0. Load Campus Map
        campuses = Campus.query.all()
        campus_map = {c.sigla_campus: c.id for c in campuses}
        
        # 1. Insert/Update New Programs
        logger.info("--- Processing New Programs ---")
        for prog in NEW_PROGRAMS:
            code, name, sigla, campus_sigla, level_abbr, area_av, area_b, year, grade = prog
            
            if campus_sigla not in campus_map:
                logger.error(f"Campus {campus_sigla} not found for {name}")
                continue
                
            campus_id = campus_map[campus_sigla]
            
            # Check if exists
            existing = ProgramaAcademico.query.filter(
                (ProgramaAcademico.codigo_programa == code) | (ProgramaAcademico.sigla_programa == sigla),
                ProgramaAcademico.campus_id == campus_id
            ).first()

            if existing:
                logger.info(f"Updating existing program: {name} ({campus_sigla})")
                existing.nome_programa = name
                existing.sigla_programa = sigla
                existing.area_avaliacao = area_av
                existing.area_basica = area_b
                existing.ano_inicio = min(existing.ano_inicio or 9999, year)
                existing.nota_capes = grade
                
                # Append level if missing
                current_levels = existing.niveis or ""
                if level_abbr not in current_levels:
                    existing.niveis = f"{current_levels}, {level_abbr}" if current_levels else level_abbr
            else:
                logger.info(f"Inserting NEW program: {name} ({campus_sigla})")
                new_prog = ProgramaAcademico(
                    codigo_programa=code,
                    nome_programa=name,
                    sigla_programa=sigla,
                    campus_id=campus_id,
                    niveis=level_abbr,
                    area_avaliacao=area_av,
                    area_basica=area_b,
                    ano_inicio=year,
                    nota_capes=grade,
                    tipo_oferta='Acadêmico' # Default
                )
                db.session.add(new_prog)

        # 2. Update Levels
        logger.info("--- Updating Levels ---")
        for sigla, campus_sigla, new_levels in LEVEL_UPDATES:
            if campus_sigla in campus_map:
                campus_id = campus_map[campus_sigla]
                prog = ProgramaAcademico.query.filter_by(sigla_programa=sigla, campus_id=campus_id).first()
                if prog:
                    prog.niveis = new_levels
                    logger.info(f"Updated levels for {sigla} ({campus_sigla})")

        # 3. Update Notes
        logger.info("--- Updating Notes ---")
        for sigla, campus_sigla, new_note in NOTE_UPDATES:
            if campus_sigla in campus_map:
                campus_id = campus_map[campus_sigla]
                prog = ProgramaAcademico.query.filter_by(sigla_programa=sigla, campus_id=campus_id).first()
                if prog:
                    prog.nota_capes = new_note
                    logger.info(f"Updated note for {sigla} ({campus_sigla})")

        db.session.commit()
        logger.info("Update Complete.")

if __name__ == "__main__":
    if 'postgresql' not in app.config['SQLALCHEMY_DATABASE_URI']:
        logger.warning("WARNING: Not connected to PostgreSQL! Check .env")
    
    update_ppg_postgres()
