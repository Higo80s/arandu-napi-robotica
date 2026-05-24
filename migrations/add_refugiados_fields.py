"""
MIGRAÇÃO: Adicionar Campos de Refugiados e Dados Humanitários
==============================================================
Data: 09/02/2026
Referência: PLANEJAMENTO_FUTURO_2026.md - Item 2 (Internacionalização e Refugiados)

Descrição:
-----------
Este script adiciona 5 novos campos à tabela 'dados_sociais' para armazenar
informações específicas de bolsistas em situação de refúgio ou proteção humanitária.

Campos adicionados:
- is_refugiado: Boolean (indica se é refugiado ou solicitante)
- pais_origem_refugio: String(100) (país de origem para mapeamento geopolítico)
- status_legal_refugio: String(50) (Solicitante/Reconhecido/Visto Humanitário)
- idioma_materno: String(100) (idioma nativo para apoio linguístico)
- necessidades_especificas: Text (apoio psicológico, moradia, validação de diploma)

Compatibilidade:
- SQLite (desenvolvimento)
- PostgreSQL (produção)

Como executar:
--------------
python migrations/add_refugiados_fields.py
"""

import sys
import os

# Adiciona o diretório raiz ao path para importar corretamente
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from sqlalchemy import text

def upgrade():
    """
    Adiciona os novos campos à tabela dados_sociais.
    """
    print("🚀 Iniciando migração: Campos de Refugiados...")
    
    with app.app_context():
        # Detecta qual banco está sendo usado
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        is_sqlite = 'sqlite' in db_uri
        
        print(f"📊 Banco de dados detectado: {'SQLite' if is_sqlite else 'PostgreSQL'}")
        
        try:
            # Lista de colunas a adicionar
            columns_to_add = [
                ("is_refugiado", "BOOLEAN DEFAULT 0" if is_sqlite else "BOOLEAN DEFAULT FALSE"),
                ("pais_origem_refugio", "VARCHAR(100)"),
                ("status_legal_refugio", "VARCHAR(50)"),
                ("idioma_materno", "VARCHAR(100)"),
                ("necessidades_especificas", "TEXT")
            ]
            
            # Verifica quais colunas já existem
            inspector = db.inspect(db.engine)
            existing_columns = [col['name'] for col in inspector.get_columns('dados_sociais')]
            
            print(f"✅ Colunas existentes na tabela: {len(existing_columns)}")
            
            # Adiciona cada coluna se ela não existir
            for col_name, col_type in columns_to_add:
                if col_name in existing_columns:
                    print(f"⏭️  Coluna '{col_name}' já existe, pulando...")
                else:
                    sql = f"ALTER TABLE dados_sociais ADD COLUMN {col_name} {col_type}"
                    db.session.execute(text(sql))
                    print(f"✅ Coluna '{col_name}' adicionada com sucesso!")
            
            # Commit das alterações
            db.session.commit()
            print("\n🎉 Migração concluída com sucesso!")
            print("\n📋 Próximos passos:")
            print("   1. Atualizar o formulário de Dados Sociais (templates/bolsistas/dados_sociais.html)")
            print("   2. Atualizar a rota de salvamento (app.py)")
            print("   3. Criar relatório específico para Pró-Reitoria de Relações Internacionais")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Erro durante a migração: {e}")
            print("💡 Dica: Verifique se a tabela 'dados_sociais' existe no banco de dados.")
            raise

def downgrade():
    """
    Remove os campos de refugiados (rollback).
    """
    print("⏪ Revertendo migração: Campos de Refugiados...")
    
    with app.app_context():
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        is_sqlite = 'sqlite' in db_uri
        
        try:
            columns_to_remove = [
                "is_refugiado",
                "pais_origem_refugio", 
                "status_legal_refugio",
                "idioma_materno",
                "necessidades_especificas"
            ]
            
            if is_sqlite:
                print("⚠️  SQLite não suporta DROP COLUMN nativamente.")
                print("    É necessário recriar a tabela manualmente ou usar Flask-Migrate.")
            else:
                # PostgreSQL suporta DROP COLUMN
                for col_name in columns_to_remove:
                    sql = f"ALTER TABLE dados_sociais DROP COLUMN IF EXISTS {col_name}"
                    db.session.execute(text(sql))
                    print(f"✅ Coluna '{col_name}' removida.")
                
                db.session.commit()
                print("🎉 Rollback concluído!")
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erro durante o rollback: {e}")
            raise

if __name__ == '__main__':
    # Permite executar upgrade ou downgrade via argumento
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'downgrade':
        downgrade()
    else:
        upgrade()
