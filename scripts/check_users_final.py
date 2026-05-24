import psycopg2

def check_users():
    try:
        conn = psycopg2.connect(dbname='arandu_napi_robotica', user='postgres', password='admin123', host='localhost')
        cur = conn.cursor()
        
        # Check columns
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'usuarios'")
        cols = [r[0] for r in cur.fetchall()]
        print(f"Colunas de usuarios: {cols}")
        
        # Check rows
        cur.execute("SELECT * FROM usuarios")
        rows = cur.fetchall()
        print(f"Total de usuarios: {len(rows)}")
        for r in rows:
            print(f" - {r}")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao verificar usuarios: {e}")

if __name__ == "__main__":
    check_users()
