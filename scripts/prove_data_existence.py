import sys
import os
from sqlalchemy import func, text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import BolsaHistorico, ProgramaAcademico, Edital

def prove_data():
    print("--- PROVA DE EXISTÊNCIA DE DADOS (AUDITORIA) ---\n")
    
    with app.app_context():
        # 1. HISTORICAL DATA (The "3 Hours Work" core)
        hist_count = db.session.query(func.count(BolsaHistorico.id)).scalar()
        print(f"1. Tabela 'bolsa_historico':")
        print(f"   -> TOTAL REGISTROS: {hist_count}")
        if hist_count > 0:
            latest = db.session.query(BolsaHistorico).order_by(BolsaHistorico.ano.desc()).first()
            print(f"   -> Último Registro: Ano {latest.ano} | Nível: {latest.nivel} | Qtd: {latest.quantidade}")
        else:
            print("   -> [ALERTA] Tabela vazia!")

        # 2. AUDIT LOGS (Governance)
        audit_count = db.session.execute(text("SELECT count(*) FROM auditoria_logs")).scalar()
        print(f"\n2. Tabela 'auditoria_logs':")
        print(f"   -> TOTAL REGISTROS: {audit_count}")
        
        # 3. PROFESSIONAL PROGRAMS (Data Sanity)
        prof_count = db.session.query(func.count(ProgramaAcademico.id)).filter_by(tipo_oferta='Profissional').scalar()
        print(f"\n3. Programas Profissionais:")
        print(f"   -> TOTAL IDENTIFICADOS: {prof_count}")
        
        # 4. ACTIVE EDITAIS (For the PDF Report)
        active_editais = Edital.query.filter(Edital.ativo == True).count()
        print(f"\n4. Editais Ativos (Base do Relatório PDF):")
        print(f"   -> TOTAL: {active_editais}")
        print("   (Se este número for 0 ou baixo, o Relatório PDF parecerá vazio, mas o Histórico (Item 1) está cheio)")

if __name__ == "__main__":
    prove_data()
