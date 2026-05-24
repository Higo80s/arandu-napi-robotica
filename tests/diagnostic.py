print("🔍 Instando diagnóstico de importação...")
try:
    from app import app
    print("✅ app imported")
    from models import db, Bolsista, Modalidade, Acompanhamento, UIMementoHistory
    print("✅ models imported")
    from services.financeiro_service import FinanceiroService
    print("✅ service imported")
    
    with app.app_context():
        print("✅ app_context active")
        db.create_all()
        print("✅ db.create_all() successful (SQLite in-memory or default)")
    
    print("🚀 Diagnóstico concluído sem erros fatais.")
except Exception as e:
    print(f"❌ [ERRO] Diagnóstico falhou: {e}")
    import traceback
    traceback.print_exc()
