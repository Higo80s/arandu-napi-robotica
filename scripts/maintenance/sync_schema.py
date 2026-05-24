import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv('DATABASE_URL')

def sync_schema():
    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cur = conn.cursor()

        # 1. Tabela 'editais'
        print("Checking 'editais' table...")
        cols_editais = [
            ('eixo', 'VARCHAR(100) DEFAULT \'Geral/Pendentes\''),
            ('orcamento_total', 'DOUBLE PRECISION DEFAULT 0.0'),
            ('proap_distribuicao_id', 'INTEGER'),
            ('numero_edital', 'VARCHAR(150)'),
            ('ano_edital', 'INTEGER'),
            ('empresa', 'VARCHAR(150)'),
            ('data_inicio', 'DATE'),
            ('data_fim', 'DATE'),
            ('prestacao_contas', 'BOOLEAN DEFAULT FALSE')
        ]
        
        for col_name, col_type in cols_editais:
            cur.execute(f"SELECT 1 FROM information_schema.columns WHERE table_name='editais' AND column_name='{col_name}'")
            if not cur.fetchone():
                print(f"  Adding column '{col_name}' ({col_type}) to 'editais'...")
                cur.execute(f"ALTER TABLE editais ADD COLUMN {col_name} {col_type};")

        # 2. Tabela 'bolsistas'
        print("Checking 'bolsistas' table...")
        cols_bolsistas = [
            ('is_pdse', 'BOOLEAN DEFAULT FALSE'),
            ('pais_destino', 'VARCHAR(100)'),
            ('devolucao_valores', 'BOOLEAN DEFAULT FALSE'),
            ('data_fim_bolsa_backup', 'DATE'),
            ('projeto_pesquisa', 'VARCHAR(255)'),
            ('recebe_bolsa', 'BOOLEAN'),
            ('agencia_fomento', 'VARCHAR(100)'),
            ('tem_adicional', 'BOOLEAN DEFAULT FALSE'),
            ('valor_adicional', 'DOUBLE PRECISION DEFAULT 0.0'),
            ('qtd_adicional', 'INTEGER DEFAULT 1'),
            ('relatorio_entregue', 'BOOLEAN DEFAULT FALSE'),
            ('matricula', 'VARCHAR(20)')
        ]

        for col_name, col_type in cols_bolsistas:
            cur.execute(f"SELECT 1 FROM information_schema.columns WHERE table_name='bolsistas' AND column_name='{col_name}'")
            if not cur.fetchone():
                print(f"  Adding column '{col_name}' ({col_type}) to 'bolsistas'...")
                cur.execute(f"ALTER TABLE bolsistas ADD COLUMN {col_name} {col_type};")

        # 3. Tabela 'residentes'
        print("Checking 'residentes' table...")
        cols_residentes = [
            ('tem_adicional', 'BOOLEAN DEFAULT FALSE'),
            ('valor_adicional', 'DOUBLE PRECISION DEFAULT 0.0'),
            ('qtd_adicional', 'INTEGER DEFAULT 1'),
            ('valor_bolsa', 'DOUBLE PRECISION'),
            ('numero_formulario', 'VARCHAR(50)')
        ]

        for col_name, col_type in cols_residentes:
            cur.execute(f"SELECT 1 FROM information_schema.columns WHERE table_name='residentes' AND column_name='{col_name}'")
            if not cur.fetchone():
                print(f"  Adding column '{col_name}' ({col_type}) to 'residentes'...")
                cur.execute(f"ALTER TABLE residentes ADD COLUMN {col_name} {col_type};")

        print("\n[SUCCESS] Schema synchronization completed.")
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"\n[ERROR] Failed to synchronize schema: {e}")
        return False

if __name__ == "__main__":
    sync_schema()
