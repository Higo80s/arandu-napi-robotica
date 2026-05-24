import psycopg2
import sqlite3
import os

# 1. Configurar bancos de dados prováveis (PostgreSQL)
pg_dbs = ['gestao_editais', 'arandu_napi_robotica', 'gestao_editais_db', 'napi_robotica', 'napi', 'postgres']
pg_user = 'postgres'
pg_pass = 'admin123'
pg_host = 'localhost'

# 2. Configurar arquivos SQLite prováveis
# Vamos buscar recursivamente na pasta Documents
sqlite_files = []
base_path = r'C:\Users\higosantos\Documents\gestao_editais'
for root, dirs, files in os.walk(base_path):
    for file in files:
        if file.endswith('.db') or file.endswith('.sqlite'):
            sqlite_files.append(os.path.join(root, file))

print(f"Iniciando busca profunda... ({len(sqlite_files)} arquivos SQLite encontrados)")

# Busca no PostgreSQL
for db in pg_dbs:
    try:
        conn = psycopg2.connect(dbname=db, user=pg_user, password=pg_pass, host=pg_host)
        cur = conn.cursor()
        
        # Verificar se as tabelas existem (usando query robusta)
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_name='bolsistas';")
        if cur.fetchone():
            cur.execute("SELECT nome FROM bolsistas WHERE nome ILIKE '%Higo%' OR nome ILIKE '%Leticia%';")
            rows = cur.fetchall()
            if rows:
                print(f"[PG: {db}] ACHADO! Nomes encontrados: {[r[0] for r in rows]}")
                cur.execute("SELECT numero FROM editais WHERE numero ILIKE '%NAPI%';")
                edits = [e[0] for e in cur.fetchall()]
                print(f"      Editais NAPI nesse banco: {edits}")
        
        cur.close()
        conn.close()
    except:
        pass

# Busca no SQLite
for db_path in sqlite_files:
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        # Verificar se a tabela bolsistas existe
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bolsistas';")
        if cur.fetchone():
            cur.execute("SELECT nome FROM bolsistas WHERE nome LIKE '%Higo%' OR nome LIKE '%Leticia%';")
            rows = cur.fetchall()
            if rows:
                print(f"[SQLITE: {db_path}] ACHADO! Nomes encontrados: {[r[0] for r in rows]}")
                cur.execute("SELECT numero FROM editais WHERE numero LIKE '%NAPI%';")
                edits = [e[0] for e in cur.fetchall()]
                print(f"         Editais NAPI nesse arquivo: {edits}")
                
        conn.close()
    except:
        pass

print("Busca encerrada.")
