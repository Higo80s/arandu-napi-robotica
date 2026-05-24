"""
SCRIPT DE MIGRAÇÃO - ÍNDICES DE PERFORMANCE
==========================================
Adiciona índices na tabela 'bolsistas' para acelerar consultas.
Compatível com SQLite e PostgreSQL.

Uso:
    python migrations/add_indices_bolsistas.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db

def add_indices():
    """
    Cria índices diretamente via SQL Raw.
    SQLAlchemy cria automaticamente em db.create_all(), mas este script
    garante que índices sejam adicionados em bancos existentes.
    """
    with app.app_context():
        connection = db.engine.connect()
        
        # Lista de índices a criar
        indices = [
            "CREATE INDEX IF NOT EXISTS idx_bolsistas_ativo ON bolsistas(ativo);",
            "CREATE INDEX IF NOT EXISTS idx_bolsistas_edital ON bolsistas(edital_id);",
            "CREATE INDEX IF NOT EXISTS idx_bolsistas_programa ON bolsistas(programa_id);"
        ]
        
        print("🔧 Criando índices de performance...")
        
        for sql in indices:
            try:
                connection.execute(db.text(sql))
                index_name = sql.split("idx_")[1].split(" ")[0]
                print(f"   ✅ Índice 'idx_{index_name}' criado com sucesso")
            except Exception as e:
                print(f"   ⚠️  Erro ao criar índice: {e}")
        
        connection.close()
        print("\n✨ Migração concluída!")

if __name__ == '__main__':
    add_indices()
