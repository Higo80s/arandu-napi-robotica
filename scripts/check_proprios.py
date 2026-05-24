import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from sqlalchemy import text

def normalize(name):
    if not name: return "NI"
    name = name.upper().strip()
    if ' - ' in name:
        parts = name.split(' - ')
        if len(parts) > 1: return parts[1].strip()
    return name

with app.app_context():
    # Query para buscar programas com bolsas ativas de Recursos Próprios
    # Edital ID 1 ou Descricao contendo PROPRIOS
    sql = """
        SELECT DISTINCT p.nome_programa, m.nivel
        FROM bolsistas b 
        JOIN editais e ON b.edital_id = e.id 
        JOIN programa_academico p ON b.programa_id = p.id
        LEFT JOIN modalidades m ON b.modalidade_id = m.id
        WHERE (e.id = 1 OR UPPER(e.descricao) LIKE '%PROPRIOS%' OR UPPER(e.descricao) LIKE '%PRÓPRIOS%') 
          AND b.ativo = true
    """
    rows = db.session.execute(text(sql)).fetchall()
    
    print("--- PROGRAMAS RECURSOS PROPRIOS ---")
    for r in rows:
        print(f"('{r.nivel}', '{r.nome_programa}')")
