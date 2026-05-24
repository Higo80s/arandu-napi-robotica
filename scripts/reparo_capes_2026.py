# --- scripts/reparo_capes_2026.py ---
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import date
from extensions import db
from models import Bolsista, Edital
from app import app 

def reparar_sistema_capes():
    with app.app_context():
        print("🚀 Iniciando reparo de dados CAPES/Arandú...")
        
        try:
            # OPERAÇÃO 1: Reativar Bolsistas Vencidos em Jan/Fev 2026
            # Eles precisam estar ativos para aparecerem na regra M+1 de Março.
            target_ids = [13, 14] # Editais CAPES IES e CAPES PPG
            query_reativacao = Bolsista.query.filter(
                Bolsista.edital_id.in_(target_ids),
                Bolsista.ativo == False,
                Bolsista.data_fim_bolsa >= date(2026, 1, 1),
                Bolsista.data_fim_bolsa < date(2026, 3, 1)
            )
            
            reativados_count = query_reativacao.count()
            query_reativacao.update({
                "ativo": True, 
                "motivo_desligamento": None, 
                "data_desligamento": None
            }, synchronize_session=False)
            
            # OPERAÇÃO 2: Definir Ciclo de Vida dos Editais (Até o fim do ano)
            editais_atualizados = Edital.query.filter(Edital.id.in_(target_ids)).update({
                "data_fim": date(2026, 12, 31)
            }, synchronize_session=False)

            db.session.commit()
            
            print(f"✅ Sucesso: {reativados_count} bolsistas reativados para o fluxo de alertas.")
            print(f"✅ Sucesso: {editais_atualizados} editais institucionais configurados para 31/12/2026.")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erro no reparo de dados: {e}")

if __name__ == "__main__":
    reparar_sistema_capes()
