
import os
import sys
from datetime import date

# Add current directory to path
sys.path.append(os.getcwd())

from app import app
from models import db, Bolsista, Edital, Acompanhamento

def run_transition():
    with app.app_context():
        print("--- Arandú v12.0: Ciclo Março/2026 ---")
        
        # 1. Identify FA Editais
        fa_editais = Edital.query.filter(Edital.agencia.ilike('%Araucária%')).all()
        fa_ids = [e.id for e in fa_editais]
        
        # 2. Active FA Bolsistas
        active_fa = Bolsista.query.filter(Bolsista.edital_id.in_(fa_ids), Bolsista.ativo == True).all()
        print(f"Bolsistas Ativos FA: {len(active_fa)}")
        
        processed = 0
        flagged = 0
        new_acomps = 0
        
        for b in active_fa:
            # Saneamento: Flag pendente_manual para quem não tem CPF
            if not b.cpf or len(b.cpf.strip()) < 11:
                if b.processo_sei != 'pendente_manual':
                    b.processo_sei = 'pendente_manual'
                    flagged += 1
            
            # Incremento de Parcela Março/2026
            # Buscar última parcela de Fev/2026 ou anterior
            last_acomp = Acompanhamento.query.filter_by(bolsista_id=b.id).order_by(Acompanhamento.referencia_mes.desc()).first()
            
            next_parcela = (last_acomp.parcela + 1) if last_acomp and last_acomp.parcela else 1
            ref_marco = "2026-03"
            
            # Check if Mar/2026 already exists
            exists = Acompanhamento.query.filter_by(bolsista_id=b.id, referencia_mes=ref_marco).first()
            if not exists:
                new_acc = Acompanhamento(
                    bolsista_id=b.id,
                    referencia_mes=ref_marco,
                    parcela=next_parcela,
                    observacoes="Incremento automático v12.0 (Março/2026)"
                )
                db.session.add(new_acc)
                new_acomps += 1
            
            processed += 1
            
        db.session.commit()
        print(f"Processamento concluído.")
        print(f" - Bolsistas analisados: {processed}")
        print(f" - Marcados como 'pendente_manual' (sem CPF): {flagged}")
        print(f" - Novos acompanhamentos (Mar/2026): {new_acomps}")

if __name__ == "__main__":
    run_transition()
