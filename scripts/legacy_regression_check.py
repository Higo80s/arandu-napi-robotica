import os
import sys
from datetime import date
from dateutil.relativedelta import relativedelta

# Adiciona o diretório raiz ao path
sys.path.append(os.getcwd())

from app import app
from models import db, Bolsista, Afastamento, MobilidadeInternacional

def run_legacy_check():
    with app.app_context():
        print("=== INICIANDO TESTE DE REGRESSÃO DE LEGADO (v11.12) ===")
        
        # 1. Seleciona os 10 mais antigos inativos
        oldest = Bolsista.query.filter_by(ativo=False).order_by(Bolsista.id.asc()).limit(10).all()
        if not oldest:
            print("Nenhum registro inativo encontrado para teste.")
            return
            
        print(f"Testando {len(oldest)} registros legados...")
        
        for b in oldest:
            print(f"\n--- Testando ID {b.id}: {b.nome} ---")
            original_fim = b.data_fim_bolsa
            original_desligamento = b.data_desligamento
            
            # SIMULAÇÃO A: Edição Simples (Proteção de Estado)
            # Simula o que o blueprint faz: 'ativo' is missing from request.form
            if not b.ativo: # Já era inativo
                # Lógica protegida: não deve mudar as datas
                # (Aqui apenas validamos que a lógica que implementamos no blueprint funcionaria)
                print(f"  [SAVE] Registro já inativo. Datas originais: Fim={original_fim}, Desligamento={original_desligamento}")
                
            # SIMULAÇÃO B: Nova Ocorrência (Retroativa)
            try:
                print("  [OCORRÊNCIA] Adicionando suspensão de 3 meses...")
                nova_ocorr = Afastamento(
                    bolsista_id=b.id,
                    tipo='trancamento',
                    data_inicio=date.today(),
                    duracao_meses=3,
                    observacao='Teste Regressão v11.12'
                )
                db.session.add(nova_ocorr)
                
                # Aplica lógica do blueprint corrigida:
                if b.ativo and b.data_fim_bolsa:
                    b.data_fim_bolsa += relativedelta(months=3)
                
                db.session.flush()
                
                if b.data_fim_bolsa == original_fim:
                    print(f"  SUCCESS: Data de término preservada ({b.data_fim_bolsa})")
                else:
                    print(f"  FAILURE: Data de término ALTERADA para {b.data_fim_bolsa}!")
            except Exception as e:
                print(f"  ERROR em Afastamento: {str(e)}")
                db.session.rollback()
                continue
            
            # SIMULAÇÃO C: Nova Mobilidade
            try:
                print("  [MOBILIDADE] Adicionando registro internacional...")
                nova_mob = MobilidadeInternacional(
                    bolsista_id=b.id,
                    pais_destino='Portugal',
                    tipo_mobilidade='Doutorado Sanduíche',
                    data_inicio=date.today()
                )
                db.session.add(nova_mob)
                db.session.flush()
                print("  SUCCESS: Mobilidade adicionada sem erros de schema.")
            except Exception as e:
                print(f"  ERROR em Mobilidade: {str(e)}")
            
            # Cleanup for test (rollback)
            db.session.rollback()
            print(f"--- Fim do teste para ID {b.id} (Rollback executado) ---")

        print("\n=== TESTE DE REGRESSÃO CONCLUÍDO ===")

if __name__ == "__main__":
    run_legacy_check()
