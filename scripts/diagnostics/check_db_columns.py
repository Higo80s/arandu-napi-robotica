import sqlite3
import os

def check_schema(db_path):
    print(f"--- Checking {db_path} ---")
    if not os.path.exists(db_path):
        print("File does not exist.")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(bolsistas)")
        cols = cursor.fetchall()
        for col in cols:
            print(col)
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_ROOT = os.path.join(BASE_DIR, "gestao_editais.db")
    DB_NEW = os.path.join(BASE_DIR, "gestao_editais_new.db") # As per app_flask config
    DB_INSTANCE = os.path.join(BASE_DIR, "instance", "gestao_editais_new.db")

    check_schema(DB_ROOT)
    check_schema(DB_NEW)
    check_schema(DB_INSTANCE)
