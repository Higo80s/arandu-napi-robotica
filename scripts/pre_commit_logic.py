import sys
import subprocess
import os

def run_tests():
    print("🛡️ [PRE-COMMIT] Iniciando Verificação Silenciosa (Pytest)...")
    result = subprocess.run(["pytest", "tests/test_financeiro.py", "tests/test_dashboard_api.py"], capture_output=True, text=True)
    if result.returncode != 0:
        print("❌ [ERRO] Falha nos testes de governança financeira!")
        print(result.stdout)
        print(result.stderr)
        return False
    print("✅ [OK] Cálculos Financeiros e APIs Validados.")
    return True

def create_memento_snapshot():
    print("📸 [PRE-COMMIT] Gerando Snapshot Preventivo (Memento)...")
    try:
        from app import app
        from models import db, UIMementoHistory
        with app.app_context():
            snapshot = UIMementoHistory(
                data_snapshot={"event": "pre-commit", "status": "stable"},
                description="Auto-snapshot antes de commit (CI/CD Blindado)"
            )
            db.session.add(snapshot)
            db.session.commit()
            print(f"✅ [OK] Snapshot #{snapshot.id} criado com sucesso.")
    except Exception as e:
        print(f"⚠️ [AVISO] Falha ao criar snapshot memento: {e}")

if __name__ == "__main__":
    if not run_tests():
        sys.exit(1)
    
    # Se os testes passarem, cria o snapshot
    create_memento_snapshot()
    
    print("🚀 [CI/CD] Tudo pronto para o commit!")
    sys.exit(0)
