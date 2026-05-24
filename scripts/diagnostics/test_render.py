import sys
import traceback
from app_flask import app, db
from models import Bolsista, Edital

print("--- TEMPLATE RENDER DIAGNOSTIC ---")
try:
    # Need request context for url_for to work inside template
    with app.test_request_context('/bolsistas'):
        print("1. Querying Data...")
        bolsistas = Bolsista.query.all()
        editais = Edital.query.all()
        
        print(f"2. Rendering 'bolsistas/index.html' with {len(bolsistas)} records...")
        from flask import render_template
        # Passing necessary context variables
        rendered = render_template('bolsistas/index.html', bolsistas=bolsistas, editais=editais, selected_edital=None)
        
        print(f"SUCCESS: Template rendered! Size: {len(rendered)} chars.")
        if "DEBUG ATIVO" in rendered:
             print("   Verified: Debug Title is present in output.")
        else:
             print("   WARNING: Debug Title NOT found in output.")

except Exception:
    print("FAILURE: Template Error Detected!")
    traceback.print_exc()

print("--- END DIAGNOSTIC ---")
