"""
TESTE TROCA DE SENHA OBRIGATÓRIA
================================
Verifica se o sistema força a mudança de senha no primeiro acesso.
"""

import unittest
from app import app, db
from models import User

class TestPasswordChange(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
        # Setup User for Test
        self.user_email = 'viewer@utfpr.edu.br'
        self.user_pass = '123'
        
        # Garantir estado inicial: Senha conhecida e Flag TRUE
        u = User.query.filter_by(email=self.user_email).first()
        if u:
            u.set_password(self.user_pass)
            u.must_change_password = True
            db.session.commit()
        else:
            self.fail(f"Usuário {self.user_email} não encontrado para teste.")

    def tearDown(self):
        # Resetar estado se necessário
        self.app_context.pop()

    def login(self, email, password):
        return self.client.post('/auth/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

    def test_force_redirect(self):
        """Teste: Usuário com flag ativa deve ser redirecionado"""
        print("\n🔒 Testando Redirecionamento Forçado...")
        
        # 1. Login
        self.login(self.user_email, self.user_pass)
        
        # 2. Tentar acessar Dashboard (Index)
        resp = self.client.get('/', follow_redirects=True)
        content = resp.data.decode('utf-8')
        
        # 3. Deve cair na tela de troca de senha
        if "Troca de Senha Obrigatória" in content:
            print("✅ Usuário redirecionado com sucesso para change-password.")
        else:
            self.fail("❌ Usuário NÃO foi redirecionado. Acesso indevido permitido.")
            
    def test_whitelist(self):
        """Teste: Usuário com flag ativa pode fazer Logout"""
        print("\n🚪 Testando Whitelist (Logout)...")
        self.login(self.user_email, self.user_pass)
        
        # Logout deve ser permitido
        resp = self.client.get('/auth/logout', follow_redirects=True)
        content = resp.data.decode('utf-8')
        
        if "Login" in content or "Entrar" in content:
             print("✅ Logout permitido.")
        else:
             self.fail("❌ Logout bloqueado ou falhou.")

    def test_change_password_flow(self):
        """Teste: Fluxo completo de troca de senha"""
        print("\n🔑 Testando Troca de Senha com Sucesso...")
        self.login(self.user_email, self.user_pass)
        
        new_pass = 'nova_senha_segura'
        
        # POST para mudar senha
        resp = self.client.post('/auth/change-password', data=dict(
            new_password=new_pass,
            confirm_password=new_pass
        ), follow_redirects=True)
        
        content = resp.data.decode('utf-8')
        
        # Sucesso -> Redireciona para Index e mostra mensagem
        if "Senha atualizada com sucesso" in content:
            print("✅ Senha atualizada e redirecionado.")
        else:
            print(f"DEBUG CONTENT: {content[:200]}")
            self.fail("❌ Falha na atualização de senha.")
            
        # Verificar no Banco
        u = User.query.filter_by(email=self.user_email).first()
        if u.must_change_password:
            self.fail("❌ Flag must_change_password ainda está TRUE.")
        else:
            print("✅ Flag atualizada para FALSE no banco.")
            
        if not u.check_password(new_pass):
            self.fail("❌ Nova senha não funciona.")
        else:
             print("✅ Nova senha verificada com sucesso.")

if __name__ == '__main__':
    unittest.main()
