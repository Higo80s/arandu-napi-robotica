"""
Teste simples: criar backup manualmente e verificar erros
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set DATABASE_URL for testing
os.environ['DATABASE_URL'] = 'postgresql://test:test@localhost:5432/test'

print("="*60)
print("TESTE MANUAL DO BACKUP SYSTEM")
print("="*60)

try:
    import backup_system
    
    print("\n1. Testando create_backup SEM Flask app...")
    backup_path = backup_system.create_backup(flask_app=None)
    
    if backup_path:
        print(f"\n✅ SUCESSO! Backup criado em:")
        print(f"   {backup_path}")
        print(f"\nVerificando arquivo:")
        if os.path.exists(backup_path):
            size_mb = os.path.getsize(backup_path) / 1024 / 1024
            print(f"   ✅ Arquivo existe ({size_mb:.2f} MB)")
        else:
            print(f"   ❌ Arquivo NÃO existe!")
    else:
        print("\n❌ FALHA! create_backup retornou None")
        print("   Verifique mensagens de erro acima")
        
except Exception as e:
    print(f"\n❌ ERRO CRÍTICO: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
