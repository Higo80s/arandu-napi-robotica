import psycopg2
from models import Bolsista, Edital, Residente, db
import inspect

def get_db_columns(table_name):
    conn = psycopg2.connect(dbname='arandu_napi_robotica', user='postgres', password='admin123', host='localhost')
    cur = conn.cursor()
    cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}'")
    cols = [r[0] for r in cur.fetchall()]
    conn.close()
    return cols

def get_model_columns(model):
    return [c.key for c in model.__table__.columns]

def run_diff():
    models_to_check = {
        'bolsistas': Bolsista,
        'editais': Edital,
        'residentes': Residente
    }
    
    for table_name, model in models_to_check.items():
        print(f"\n--- Checking Table: {table_name} ---")
        try:
            db_cols = get_db_columns(table_name)
            model_cols = get_model_columns(model)
            
            missing_in_db = [c for c in model_cols if c not in db_cols]
            extra_in_db = [c for c in db_cols if c not in model_cols]
            
            if missing_in_db:
                print(f"MISSING in DB: {missing_in_db}")
            else:
                print("No missing columns in DB.")
                
            if extra_in_db:
                print(f"Extra in DB (not in model): {extra_in_db}")
        except Exception as e:
            print(f"Error checking {table_name}: {e}")

if __name__ == "__main__":
    from flask import Flask
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin123@localhost:5432/arandu_napi_robotica'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    with app.app_context():
        run_diff()
