import psycopg2
import os

databases_to_check = [
    'gestao_editais',
    'arandu_napi_robotica',
    'gestao_editais_db',
    'napi_robotica',
    'gestao_editais_new',
    'postgres'
]

user = 'postgres'
password = 'admin123'
host = 'localhost'

print("Iniciando busca profunda por dados do NAPI-Robótica...")

for db in databases_to_check:
    print(f"--- Verificando banco: {db} ---")
    try:
        conn = psycopg2.connect(dbname=db, user=user, password=password, host=host)
        cur = conn.cursor()
        
        # Buscar bolsistas específicos
        cur.execute("SELECT name FROM information_schema.tables WHERE table_name = 'bolsistas';")
        if cur.fetchone():
            cur.execute("SELECT id, nome, email FROM bolsistas WHERE nome ILIKE '%Higo Figueiredo%' OR nome ILIKE '%Leticia Missae%';")
            results = cur.fetchall()
            if results:
                print(f"  [ACHADO!] Bolsistas encontrados no banco {db}:")
                for r in results:
                    print(f"    - ID: {r[0]}, Nome: {r[1]}, Email: {r[2]}")
                    
                # Verificando editais também
                cur.execute("SELECT id, numero, descricao FROM editais WHERE numero ILIKE '%C-NAPI-ROBOTICA%' OR descricao ILIKE '%NAPI-ROBOTICA%';")
                editais = cur.fetchall()
                if editais:
                    print(f"  [ACHADO!] Editais encontrados no banco {db}:")
                    for e in editais:
                        print(f"    - ID: {e[0]}, Numero: {e[1]}, Descrição: {e[2]}")
            else:
                print(f"  Tabela 'bolsistas' existe, mas os nomes específicos não foram encontrados.")
        else:
            print(f"  Tabela 'bolsistas' não encontrada.")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"  Erro ao conectar no banco {db}: {e}")

print("\nBusca concluída.")
