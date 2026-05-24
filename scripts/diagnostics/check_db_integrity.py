import sqlite3
import os

DB_PATH = 'gestao_editais.db'

def check_db():
    if not os.path.exists(DB_PATH):
        print(f"ERROR: DB file not found at {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tables found: {[t[0] for t in tables]}")
        
        # Check specific table
        cursor.execute("SELECT count(*) FROM bolsistas")
        count = cursor.fetchone()[0]
        print(f"Bolsistas count: {count}")
        
        conn.close()
        print("DB Integrity Check: PASS")
    except Exception as e:
        print(f"DB Integrity Check: FAIL - {e}")

if __name__ == "__main__":
    check_db()
