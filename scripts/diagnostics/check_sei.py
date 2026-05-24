import sqlite3

try:
    conn = sqlite3.connect('instance/gestao_editais_new.db')
    c = conn.cursor()
    print("--- Bolsista SEI Data ---")
    c.execute("SELECT id, nome, processo_sei FROM bolsista")
    rows = c.fetchall()
    for r in rows:
        print(r)

    print("\n--- Edital SEI Data ---")
    c.execute("SELECT id, numero, processo_sei FROM edital")
    rows = c.fetchall()
    for r in rows:
        print(r)
        
    conn.close()
except Exception as e:
    print(e)
