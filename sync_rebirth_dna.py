import psycopg2

def sync_rebirth_dna():
    try:
        conn = psycopg2.connect(
            host='localhost', 
            port='5432', 
            user='postgres', 
            password='admin123', 
            database='gestao_editais'
        )
        cur = conn.cursor()
        
        # 1. Add 'eixo' column to 'editais'
        print("Adding 'eixo' to 'editais'...")
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='editais' AND column_name='eixo'")
        if not cur.fetchone():
            cur.execute("ALTER TABLE editais ADD COLUMN eixo VARCHAR(100) DEFAULT 'Geral/Pendentes'")
        
        # 2. Create 'ui_state' table
        print("Creating 'ui_state' table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ui_state (
                id SERIAL PRIMARY KEY,
                element_key VARCHAR(255) UNIQUE NOT NULL,
                current_text TEXT NOT NULL,
                page_context VARCHAR(100),
                updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 3. Create 'ui_memento_history' table
        print("Creating 'ui_memento_history' table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ui_memento_history (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
                user_id INTEGER REFERENCES usuarios(id),
                description TEXT,
                ui_snapshot JSONB NOT NULL
            )
        """)
        
        # 4. Set 'master' role for Higo
        print("Upgrading 'Higo Santos' to MASTER role...")
        cur.execute("UPDATE usuarios SET role = 'master' WHERE email = 'higosantos@utfpr.edu.br'")
        
        conn.commit()
        print("DNA Sync Successful!")
        conn.close()
    except Exception as e:
        print(f"Error during DNA Sync: {e}")

if __name__ == "__main__":
    sync_rebirth_dna()
