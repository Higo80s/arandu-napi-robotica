
from app import app, db
from models import Bolsista
from datetime import date

def run_update_job():
    print("--- Job de Atualização de Status ---")
    with app.app_context():
        hoje = date.today()
        # Find Active bolsistas that expired
        # Criteria: ativo=True AND data_fim_bolsa < hoje
        
        vencidos = Bolsista.query.filter(Bolsista.ativo == True, Bolsista.data_fim_bolsa < hoje).all()
        
        print(f"Encontrados {len(vencidos)} bolsistas vencidos.")
        
        count = 0
        for b in vencidos:
            try:
                print(f"Desativando: {b.nome} (Fim: {b.data_fim_bolsa})")
                b.ativo = False
                b.motivo_desligamento = "Desligamento automático por fim de vigência"
                b.data_desligamento = hoje
                count += 1
            except Exception as e:
                print(f"Erro ao atualizar {b.id}: {e}")
        
        if count > 0:
            db.session.commit()
            print(f"Sucesso: {count} registros atualizados.")
        else:
            print("Nenhuma atualização necessária.")

if __name__ == "__main__":
    run_update_job()
