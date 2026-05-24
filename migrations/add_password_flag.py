"""
MIGRATION: Adicionar campo 'must_change_password' na tabela User
================================================================
Data: 30/01/2026
Fase: 2.3 - Segurança (Troca de Senha)

Objetivo: 
- Adicionar coluna 'must_change_password' (Boolean) na tabela 'usuarios'
- Default: False (para não bloquear admin atual)
- Update manual: Setar True para usuários de teste.
"""

import sys
import os

from dotenv import load_dotenv
load_dotenv()

# Fix path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
from models import db
from sqlalchemy import text
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def run_migration():
    print("=" * 80)
    print("🔄 MIGRATION: Adicionar flag 'must_change_password'")
    print("=" * 80)
    
    with app.app_context():
        try:
            # 1. Verificar existência
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='usuarios' AND column_name='must_change_password'
            """))
            
            if result.fetchone():
                print("⚠️  Coluna 'must_change_password' já existe.")
            else:
                # 2. Adicionar coluna
                print("📝 Adicionando coluna...")
                db.session.execute(text("""
                    ALTER TABLE usuarios 
                    ADD COLUMN must_change_password BOOLEAN DEFAULT FALSE
                """))
                db.session.commit()
                print("✅ Coluna adicionada com sucesso.")
            
            # 3. Marcar usuários de teste para troca obrigatória
            print("\n🔧 Configurando usuários de teste para troca obrigatória...")
            test_emails = ['coordenador@utfpr.edu.br', 'viewer@utfpr.edu.br']
            
            for email in test_emails:
                res = db.session.execute(text("""
                    UPDATE usuarios 
                    SET must_change_password = TRUE 
                    WHERE email = :email
                """), {'email': email})
                if res.rowcount > 0:
                    print(f"   -> {email}: FLAG ATIVADA ✅")
                else:
                    print(f"   -> {email}: Usuário não encontrado ⚠️")
            
            db.session.commit()
            return True
            
        except Exception as e:
            print(f"\n❌ ERRO FATAL: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    run_migration()
