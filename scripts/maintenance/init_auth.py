
from app import app, db
from models import User

def init_auth():
    print("Iniciando configuração de autenticação...")
    with app.app_context():
        # Cria apenas as tabelas que ainda não existem (no caso, 'usuarios')
        db.create_all()
        print("Tabelas verificadas/criadas.")
        
        # Verifica se já existe admin
        admin = User.query.filter_by(email='admin@utfpr.edu.br').first()
        if not admin:
            # Cria superusuário padrão
            print("Criando usuário admin padrão...")
            admin = User(
                email='admin@utfpr.edu.br',
                nome='Administrador do Sistema',
                role='admin',
                ativo=True
            )
            admin.set_password('admin123') # Senha inicial provisória
            db.session.add(admin)
            db.session.commit()
            print("Usuário 'admin@utfpr.edu.br' criado com senha 'admin123'.")
        else:
            print("Usuário admin já existe.")

if __name__ == "__main__":
    init_auth()
