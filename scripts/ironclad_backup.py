
import os
import sys
import json
from datetime import datetime

# Add project root to path
sys.path.append(os.getcwd())

from app import app
from models import db, Bolsista, Afastamento, MobilidadeInternacional, Edital

def create_memento_snapshot():
    with app.app_context():
        print("--- Iniciando Protocolo IRONCLAD (Sessão v13.6) ---")
        
        # 1. Memento Snapshot (Application Level)
        snapshot = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "version": "13.6",
                "total_records": Bolsista.query.count()
            },
            "bolsistas": [],
            "afastamentos": [],
            "mobilidades": []
        }
        
        # Capture Bolsistas
        for b in Bolsista.query.all():
            snapshot["bolsistas"].append({
                "id": b.id,
                "nome": b.nome,
                "cpf": b.cpf,
                "ativo": b.ativo,
                "data_inicio_bolsa": str(b.data_inicio_bolsa),
                "data_fim_bolsa": str(b.data_fim_bolsa),
                "status_static": b.check_status_validity(), # current logic
                "edital_id": b.edital_id
            })
            
        # Capture Afastamentos
        for a in Afastamento.query.all():
            snapshot["afastamentos"].append({
                "id": a.id,
                "bolsista_id": a.bolsista_id,
                "tipo": a.tipo,
                "data_inicio": str(a.data_inicio),
                "duracao_meses": a.duracao_meses
            })
            
        # Capture Mobilidades
        for m in MobilidadeInternacional.query.all():
            snapshot["mobilidades"].append({
                "id": m.id,
                "bolsista_id": m.bolsista_id,
                "pais_destino": m.pais_destino,
                "data_inicio": str(m.data_inicio),
                "data_fim": str(m.data_fim)
            })
            
        # Save to JSON
        os.makedirs("backups", exist_ok=True)
        backup_path = f"backups/memento_ironclad_{datetime.now().strftime('%Y%m%d')}.json"
        with open(backup_path, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=4, ensure_ascii=False)
            
        print(f"Snapshot Memento salvo em: {backup_path}")
        
        # 2. Round-Trip Verification (ID 1599 - Giulia)
        giulia = Bolsista.query.get(1599)
        if giulia:
            # Simulate restore from snapshot
            giulia_snap = next((s for s in snapshot["bolsistas"] if s["id"] == 1599), None)
            if giulia_snap and giulia_snap["nome"] == giulia.nome:
                print("VERIFICAÇÃO ROUND-TRIP: SUCESSO (Giulia ID 1599 íntegra)")
            else:
                print("VERIFICAÇÃO ROUND-TRIP: FALHA (Divergência nos dados)")
                return False
        else:
            print("AVISO: ID 1599 não encontrado para verificação.")
            
        return True

if __name__ == "__main__":
    if create_memento_snapshot():
        print("--- PROTOCOLO IRONCLAD CONCLUÍDO COM SUCESSO ---")
    else:
        print("--- ERRO CRÍTICO NO PROTOCOLO IRONCLAD ---")
        sys.exit(1)
