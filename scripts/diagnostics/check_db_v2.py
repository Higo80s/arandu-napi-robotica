import sqlite3
import os

def check_schema(name, db_path):
    if not os.path.exists(db_path):
        print(f"{name}: NOT FOUND")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(bolsistas)")
        cols = [c[1] for c in cursor.fetchall()]
        print(f"{name}: {cols}")
        conn.close()
    except Exception as e:
        print(f"{name}: Error {e}")

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    check_schema("ROOT_DB", os.path.join(BASE_DIR, "gestao_editais.db"))
    check_schema("NEW_DB", os.path.join(BASE_DIR, "gestao_editais_new.db"))
    check_schema("INSTANCE_DB", os.path.join(BASE_DIR, "instance", "gestao_editais_new.db"))
