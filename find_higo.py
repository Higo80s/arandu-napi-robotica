import psycopg2

def find_higo():
    try:
        conn = psycopg2.connect(
            host='localhost', 
            port='5432', 
            user='postgres', 
            password='admin123', 
            database='gestao_editais'
        )
        cur = conn.cursor()
        cur.execute("SELECT email, nome, role FROM usuarios WHERE nome ILIKE '%Higo%'")
        users = cur.fetchall()
        for u in users:
            print(f"Email: {u[0]} | Nome: {u[1]} | Current Role: {u[2]}")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_higo()
