import sys
import traceback
from app_flask import app, db
from models import Bolsista

print("--- RUNTIME DIAGNOSTIC ---")
try:
    with app.app_context():
        print("1. Querying Bolsistas...")
        bolsistas = Bolsista.query.all()
        print(f"   Found {len(bolsistas)} bolsistas.")
        
        print("2. Simulate Render Index...")
        from flask import render_template
        # We can't easily call render_template outside request context without mocking request
        # But we can verify accessing attributes accessed in template
        
        for b in bolsistas:
            # Template accesses: nome, modalidade.nivel, edital.numero, data_inicio..., status
            _ = b.nome
            _ = b.modalidade.nivel if b.modalidade else 'No Mod'
            _ = b.edital.numero if b.edital else 'No Edital'
            _ = b.status
            # Check debug access
            print(f"   Check: {b.nome} - Status: {b.status}")
            
        print("SUCCESS: No errors detected during query/access.")

except Exception:
    print("FAILURE: Runtime Error Detected!")
    traceback.print_exc()

print("--- END DIAGNOSTIC ---")
