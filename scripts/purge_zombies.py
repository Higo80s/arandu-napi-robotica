
import os
import sys
from datetime import date

# Add project root to path
sys.path.append(os.getcwd())

from app import app
from models import db, Bolsista
from audit import log_action

def purge_zombies():
    with app.app_context():
        print("--- Iniciando OPERAÇÃO THE PURGE: EXTINÇÃO DE ZUMBIS (v14.1) ---")
        
        # 1. Identify Zombies (Expired but marked as Active)
        zombies = Bolsista.query.filter(Bolsista.data_fim_bolsa < date.today(), Bolsista.ativo == True).all()
        
        if not zombies:
            print("Nenhum estado zumbi encontrado. Sistema já está sincronizado.")
            return
            
        print(f"Detectados {len(zombies)} registros inconsistentes. Iniciando saneamento...")
        
        count = 0
        for z in zombies:
            # Importante: O State Pattern (check_status_validity) já diria que ele é INATIVO.
            # Aqui estamos apenas forçando a flag 'ativo' para False para limpar o legado.
            
            # Ponto de Restauração (Memento Snapshot)
            z.create_snapshot(contexto="The Purge v14.1: Saneamento automático de Estado Zumbi.")
            
            # Deativação Lógica
            z.ativo = False
            if not z.data_desligamento:
                z.data_desligamento = z.data_fim_bolsa
            if not z.motivo_desligamento:
                z.motivo_desligamento = "Saneamento Automático: Bolsa Vencida (Purge v14.1)"
                
            count += 1
            if count % 20 == 0:
                print(f"Processados {count}...")
                
        db.session.commit()
        log_action('THE_PURGE_ZOMBIES', tabela='bolsistas', detalhes=f"{count} zumbis extintos com sucesso.")
        print(f"--- SUCESSO: {count} ZUMBIS PACIFICADOS ---")

if __name__ == "__main__":
    purge_zombies()
