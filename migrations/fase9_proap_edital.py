import sqlite3

def migrate():
    print("Iniciando migração FASE 9: Vínculo Edital -> PROAP...")
    
    conn = sqlite3.connect('instance/gestao_editais_new.db')
    cursor = conn.cursor()
    
    try:
        # 1. Adicionar coluna proap_distribuicao_id na tabela editais
        print("Adicionando coluna proap_distribuicao_id...")
        cursor.execute("ALTER TABLE editais ADD COLUMN proap_distribuicao_id INTEGER REFERENCES proap_distribuicoes(id)")
        
        # 2. Criar índice para performance
        print("Criando índice...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_edital_proap_distribuicao ON editais(proap_distribuicao_id)")
        
        conn.commit()
        print("✅ Migração concluída com sucesso!")
        
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("⚠️ Coluna já existe. Ignorando.")
        else:
            print(f"❌ Erro operacional: {e}")
            conn.rollback()
    except Exception as e:
        print(f"❌ Erro na migração: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
