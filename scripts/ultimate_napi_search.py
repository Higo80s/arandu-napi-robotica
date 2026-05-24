import psycopg2

def deep_search():
    print("Iniciando Busca Profunda por Dados do NAPI-Robótica...")
    
    # 1. Obter lista de todos os bancos de dados
    try:
        conn_master = psycopg2.connect(dbname='postgres', user='postgres', password='admin123', host='localhost')
        cur_master = conn_master.cursor()
        cur_master.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
        all_dbs = [row[0] for row in cur_master.fetchall()]
        cur_master.close()
        conn_master.close()
    except Exception as e:
        print(f"Erro ao listar bancos de dados: {e}")
        return

    targets = [
        ("%Figueiredo%", "bolsistas", "nome"),
        ("%Missae%", "bolsistas", "nome"),
        ("%NAPI-ROBOTICA%", "editais", "numero"),
        ("%NAPI-ROBOTICA%", "editais", "descricao")
    ]

    for dbname in all_dbs:
        print(f"--- Verificando banco: {dbname} ---")
        try:
            conn = psycopg2.connect(dbname=dbname, user='postgres', password='admin123', host='localhost')
            cur = conn.cursor()
            
            # Verificar se tabelas existem
            cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            tables = [row[0] for row in cur.fetchall()]
            
            for pattern, table, col in targets:
                if table in tables:
                    cur.execute(f"SELECT count(*) FROM {table} WHERE {col} ILIKE %s", (pattern,))
                    count = cur.fetchone()[0]
                    if count > 0:
                        print(f"  [ACHADO!] {count} registros encontrados em '{table}.{col}' com o padrão '{pattern}'")
                        cur.execute(f"SELECT id, {col} FROM {table} WHERE {col} ILIKE %s LIMIT 5", (pattern,))
                        for pk, val in cur.fetchall():
                            print(f"    - ID {pk}: {val}")
                        
            cur.close()
            conn.close()
        except Exception as e:
            print(f"  Pulei o banco {dbname}: {e}")

if __name__ == "__main__":
    deep_search()
