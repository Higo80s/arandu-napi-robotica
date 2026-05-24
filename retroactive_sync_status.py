
from app import app
from models import db, Candidatura, Bolsista, Residente
from encryption import cipher_suite
import time

def retroactive_sync():
    """
    Sincroniza candidaturas antigas (status != 'EFETIVADO') cruzando CPFs em memória.
    Resolve casos como o da Letícia Bito (ID 14).
    """
    print("🚀 Iniciando Sincronização Retroativa de Status...")
    start_time = time.time()
    
    with app.app_context():
        # 1. Construir índice de CPFs efetivados (Match em Memória devido ao Fernet)
        print("🔍 Mapeando CPFs de Bolsistas e Residentes...")
        cpfs_efetivados = set()
        
        # Bolsistas
        bolsistas = Bolsista.query.all()
        for b in bolsistas:
            if b.cpf:
                try:
                    # O TypeDecorator EncryptedString descriptografa automaticamente no .cpf
                    cpfs_efetivados.add(b.cpf.strip())
                except:
                    continue
        
        # Residentes
        residentes = Residente.query.all()
        for r in residentes:
            if r.cpf:
                try:
                    cpfs_efetivados.add(r.cpf.strip())
                except:
                    continue
        
        print(f"✅ Total de CPFs efetivados mapeados: {len(cpfs_efetivados)}")
        
        # 2. Varredura de Candidaturas
        print("📡 Verificando candidaturas pendentes...")
        candidaturas = Candidatura.query.filter(Candidatura.status != 'EFETIVADO').all()
        
        count = 0
        ids_sincronizados = []
        
        for cand in candidaturas:
            if cand.cpf:
                try:
                    clean_cpf = cand.cpf.strip()
                    if clean_cpf in cpfs_efetivados:
                        cand.status = 'EFETIVADO'
                        count += 1
                        ids_sincronizados.append(cand.id)
                except:
                    continue
        
        if count > 0:
            db.session.commit()
            print(f"✨ SUCESSO: {count} candidaturas foram marcadas como 'EFETIVADO'.")
            print(f"📝 IDs afetados: {ids_sincronizados}")
        else:
            print("PHEW! Nenhuma candidatura pendente com CPF já cadastrado foi encontrada.")
            
    end_time = time.time()
    print(f"⏱️ Tempo total: {end_time - start_time:.2f}s")

if __name__ == "__main__":
    retroactive_sync()
