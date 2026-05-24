"""
MIGRATION: Adicionar campo 'role' na tabela User
================================================
Data: 30/01/2026
Fase: 2.2 - Sistema de Permissões

Objetivo: 
- Adicionar coluna 'role' VARCHAR(20) na tabela 'usuarios'
- Valores permitidos: 'admin', 'coordenador', 'visualizador'
- Valor padrão: 'visualizador' (princípio de menor privilégio)
- Atualizar usuário existente (higosantos@utfpr.edu.br) para 'admin'
"""

# Adicionar diretório pai ao path
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
from models import db
from sqlalchemy import text

app = Flask(__name__)

# Conexão PostgreSQL
import os
from dotenv import load_dotenv
load_dotenv()

db_url = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def run_migration():
    """Executa a migration"""
    print("=" * 80)
    print("🔄 MIGRATION: Adicionar campo 'role' em User")
    print("=" * 80)
    print()
    
    with app.app_context():
        try:
            # 1. Verificar se coluna já existe
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='usuarios' AND column_name='role'
            """))
            
            if result.fetchone():
                print("⚠️  Coluna 'role' já existe. Pulando criação.")
            else:
                # 2. Adicionar coluna
                print("📝 Adicionando coluna 'role'...")
                db.session.execute(text("""
                    ALTER TABLE usuarios 
                    ADD COLUMN role VARCHAR(20) DEFAULT 'visualizador'
                """))
                db.session.commit()
                print("✅ Coluna 'role' adicionada")
            
            # 3. Atualizar usuário admin (higosantos@utfpr.edu.br)
            print()
            print("👑 Promovendo usuário higosantos@utfpr.edu.br para ADMIN...")
            
            result = db.session.execute(text("""
                UPDATE usuarios 
                SET role = 'admin' 
                WHERE email = 'higosantos@utfpr.edu.br'
            """))
            db.session.commit()
            
            print(f"✅ {result.rowcount} usuário(s) atualizado(s)")
            
            # 4. Garantir que outros usuários tenham role padrão
            print()
            print("🔧 Atualizando roles NULL para 'visualizador'...")
            
            result = db.session.execute(text("""
                UPDATE usuarios 
                SET role = 'visualizador' 
                WHERE role IS NULL
            """))
            db.session.commit()
            
            print(f"✅ {result.rowcount} usuário(s) atualizado(s)")
            
            # 5. Verificação final
            print()
            print("📊 RESUMO DOS USUÁRIOS:")
            print("-" * 80)
            
            result = db.session.execute(text("""
                SELECT email, role 
                FROM usuarios 
                ORDER BY role, email
            """))
            
            for row in result:
                role_emoji = {
                    'admin': '👑',
                    'coordenador': '👔',
                    'visualizador': '👁️'
                }.get(row[1], '❓')
                
                print(f"  {role_emoji} {row[0]:40} → {row[1]}")
            
            print()
            print("=" * 80)
            print("✅ MIGRATION CONCLUÍDA COM SUCESSO")
            print("=" * 80)
            
            return True
            
        except Exception as e:
            print()
            print(f"❌ ERRO na migration: {str(e)}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    import sys
    success = run_migration()
    sys.exit(0 if success else 1)
