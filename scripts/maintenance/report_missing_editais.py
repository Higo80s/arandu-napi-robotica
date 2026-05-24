import json
from flask import Flask
from models import db, Edital
from sqlalchemy import text

# Carregar dump JSON
with open('universal_dump_20260129_0148.json', encoding='utf-8') as f:
    data = json.load(f)

editais_dump = data.get('editais', [])
print(f"Editais no dump JSON: {len(editais_dump)}\n")

# Conectar ao PostgreSQL
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin123@localhost:5432/gestao_editais'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    editais_postgres = Edital.query.all()
    ids_postgres = {e.id for e in editais_postgres}
    
    print(f"Editais no PostgreSQL: {len(editais_postgres)}\n")
    print("=" * 80)
    print("EDITAIS NÃO MIGRADOS (6):")
    print("=" * 80)
    
    for edital_dump in editais_dump:
        if edital_dump['id'] not in ids_postgres:
            print(f"\nID: {edital_dump['id']}")
            print(f"  Número: {edital_dump.get('numero', 'N/A')}")
            print(f"  Descrição: {edital_dump.get('descricao', 'N/A')[:80]}")
            print(f"  Agência: {edital_dump.get('agencia', 'N/A')}")
            print(f"  Código Projeto: {edital_dump.get('codigo_projeto', 'N/A')[:50]}")
