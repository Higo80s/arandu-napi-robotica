import os
import sys
from datetime import date

# Garantir que o diretório raiz esteja no PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import Bolsista

def run_update_antigas(dry_run=True):
    print(f"[{'DRY-RUN' if dry_run else 'EXECUTE'}] Iniciando inativação de bolsas antigas (< Fev 2026)")
    
    target_date = date(2026, 2, 1) # February 2026
    
    with app.app_context():
        # Bolsistas com vigência anterior a Fevereiro de 2026 e que estão ativos
        bolsistas = Bolsista.query.filter(
            Bolsista.data_fim_bolsa < target_date,
            Bolsista.ativo == True
        ).all()
        
        total = len(bolsistas)
        print(f"Bolsistas encontrados: {total}")
        
        cnt_updated = 0
        
        for b in bolsistas:
            if not dry_run:
                b.ativo = False
                b.motivo_desligamento = 'Vigência Encerrada'  # Libera a cota (diferente de 'Finalizando')
                # A data_desligamento poderia ser b.data_fim_bolsa, 
                # mas o sistema já as tem expiradas pelo data_fim_bolsa de qualquer forma.
                b.data_desligamento = b.data_fim_bolsa
            cnt_updated += 1
            
        print(f"Bolsistas atualizados em memória: {cnt_updated}")
        
        if not dry_run:
            print("Gravando no Banco de Dados (Commit)...")
            db.session.commit()
            print("Limpeza de bolsas antigas concluída com sucesso!")
        else:
            print("Simulação concluída. O banco NÃO foi modificado.")

if __name__ == '__main__':
    # Estamos pulando o dry_run direto para a execução pois o dry-run já fopi avaliado manualmente
    run_update_antigas(dry_run=False)
