import psycopg2
import json
from datetime import datetime

def take_initial_memento():
    try:
        conn = psycopg2.connect(
            host='localhost', 
            port='5432', 
            user='postgres', 
            password='admin123', 
            database='gestao_editais'
        )
        cur = conn.cursor()
        
        # 1. Get current UI State
        cur.execute("SELECT element_key, current_text FROM ui_state")
        ui_snapshot = {rec[0]: rec[1] for rec in cur.fetchall()}
        
        # 2. Get Higo's user_id
        cur.execute("SELECT id FROM usuarios WHERE email = 'higosantos@utfpr.edu.br'")
        user_id = cur.fetchone()[0]
        
        # 3. Insert Memento
        print("Taking initial Memento snapshot...")
        cur.execute("""
            INSERT INTO ui_memento_history (timestamp, user_id, description, ui_snapshot)
            VALUES (%s, %s, %s, %s)
        """, (datetime.now(), user_id, "Snapshot Inicial: Protocolo Rebirth Concluído", json.dumps(ui_snapshot)))
        
        conn.commit()
        print("Initial Memento Snapshot Successful!")
        conn.close()
    except Exception as e:
        print(f"Error taking Memento: {e}")

if __name__ == "__main__":
    take_initial_memento()
