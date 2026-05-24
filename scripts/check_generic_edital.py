import sqlite3
import os

# Connect to the correct absolute path
db_path = r'c:\Users\higosantos\Documents\gestao_editais\gestao_editais_novo\gestao_editais_final.db'

def check_or_create_generic_edital():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Check if exists
    cur.execute("SELECT id, numero, agencia FROM editais WHERE numero LIKE 'Edital Geral - Análise Posterior%'")
    row = cur.fetchone()
    if row:
        print(f"Generic Edital already exists: ID={row[0]}, Numero='{row[1]}', Agencia='{row[2]}'")
    else:
        print("Generic Edital not found. Creating one...")
        cur.execute("""
            INSERT INTO editais (numero, descricao, agencia) 
            VALUES ('Edital Geral - Análise Posterior', 'Edital genérico para alocação temporária de bolsistas não encontrados nas planilhas recentes.', 'Fundação Araucária')
        """)
        new_id = cur.lastrowid
        conn.commit()
        print(f"Created Generic Edital with ID={new_id}")
    
    conn.close()

if __name__ == "__main__":
    check_or_create_generic_edital()
