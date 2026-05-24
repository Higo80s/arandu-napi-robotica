import pandas as pd
from flask import Flask
from models import db
from sqlalchemy import text

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin123@localhost:5432/gestao_editais'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Ler CSV original
df_original = pd.read_csv('distribuicao_cotas_backup.csv')
print(f"Total no CSV original: {len(df_original)}")

with app.app_context():
    # IDs no PostgreSQL
    result = db.session.execute(text("SELECT id FROM distribuicao_cotas"))
    ids_postgres = {row[0] for row in result}
    print(f"Total no PostgreSQL: {len(ids_postgres)}")
    
    # Identificar faltantes
    faltantes = df_original[~df_original['id'].isin(ids_postgres)]
    
    print(f"\n{'='*80}")
    print(f"REGISTROS NÃO MIGRADOS: {len(faltantes)}")
    print(f"{'='*80}\n")
    
    for idx, row in faltantes.iterrows():
        print(f"ID: {row['id']}")
        print(f"  Edital ID: {row['edital_id']}")
        print(f"  Programa ID: {row['programa_id']}")
        print(f"  Modalidade ID: {row['modalidade_id']}")
        print(f"  Qtd Concedida: {row['qtd_concedida']}")
        
        # Verificar se programa existe
        prog_check = db.session.execute(text("SELECT nome_programa FROM programa_academico WHERE id = :id"), {'id': int(row['programa_id'])})
        prog = prog_check.fetchone()
        if prog:
            print(f"  Programa: {prog[0]}")
        else:
            print(f"  Programa: [NÃO EXISTE - ID {row['programa_id']}]")
        print()
