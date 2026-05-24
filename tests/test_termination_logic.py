import unittest
import requests
import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app_test_termination import app, db, Bolsista, Edital, Modalidade

class TestTerminationLogic(unittest.TestCase):
    def setUp(self):
        try:
            app.config['TESTING'] = True
            app.config['WTF_CSRF_ENABLED'] = False 
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' 
            self.app = app.test_client()
            with app.app_context():
                db.drop_all() # Clean start
                db.create_all()
                # Create Prerequisites
                edital = Edital(numero="99/2026", agencia="TestAgency", descricao="Test", data_inicio=datetime.date(2026,1,1), data_fim=datetime.date(2026,12,31))
                db.session.add(edital)
                db.session.commit()
                
                mod = Modalidade(edital_id=edital.id, nivel="Mestrado", vagas=1, valor_mensal=1000, max_meses=24)
                db.session.add(mod)
                db.session.commit()
                
                # Create Active Bolsista
                b = Bolsista(
                    nome="John Doe", cpf="11122233344", 
                    edital_id=edital.id, modalidade_id=mod.id,
                    data_inicio_bolsa=datetime.date(2026, 1, 1),
                    meses_duracao=12,
                    data_fim_bolsa=datetime.date(2026, 12, 1) 
                )
                db.session.add(b)
                db.session.commit()
                self.bid = b.id
        except Exception as e:
            import traceback
            with open('setup_error.txt', 'w', encoding='utf-8') as f:
                f.write(str(e) + "\n" + traceback.format_exc())
            raise e

    def test_termination(self):
        try:
            with app.app_context():
                # 1. Verify Initial State
                b = Bolsista.query.get(self.bid)
                self.assertTrue(b.ativo)
                self.assertIsNone(b.data_desligamento)
                initial_end = b.data_fim_bolsa
                print(f"Initial End Date: {initial_end}")

                # 2. Simulate POST to Deactivate
                data = {
                    'nome': "John Doe", 'cpf': "11122233344", 'email': 'test@test.com',
                    'edital_id': b.edital_id, 'modalidade_id': b.modalidade_id,
                    'data_inicio_bolsa': '2026-01-01',
                    'meses_duracao': '12',
                    'data_inicio_curso': '2026-01-01', # Required
                    'banco': 'X', 'agencia': '1', 'conta': '1', 'tipo_conta': 'corrente',
                    'orientador': 'Dr. Test', 'email_orientador': 'prof@test.com', 
                    'previsao_defesa': '', # Required key
                    # 'ativo':_missing_ -> This triggers deactivation
                }
                
                resp = self.app.post(f'/bolsistas/{self.bid}/editar', data=data, follow_redirects=True)
                
                if resp.status_code != 200:
                    with open('test_debug_output.txt', 'w', encoding='utf-8') as f:
                        f.write(f"Status: {resp.status_code}\n")
                        f.write(f"Data: {resp.data.decode('utf-8')}\n")
                
                self.assertEqual(resp.status_code, 200)
                
                # 3. Verify Termination State
                # Refresh object
                db.session.expire_all()
                b = Bolsista.query.get(self.bid)
                
                if b.ativo:
                    print("FAIL: Bolsista still active")
                self.assertFalse(b.ativo)
                self.assertIsNotNone(b.data_desligamento)
                self.assertEqual(b.data_desligamento, datetime.date.today())
                self.assertEqual(b.data_fim_bolsa, datetime.date.today())
                print(f"Terminated End Date: {b.data_fim_bolsa} (Should be Today)")
                
                # 4. Reactivate
                data['ativo'] = 'on'
                resp = self.app.post(f'/bolsistas/{self.bid}/editar', data=data, follow_redirects=True)
                
                # 5. Verify Reactivation
                db.session.expire_all()
                b = Bolsista.query.get(self.bid)
                self.assertTrue(b.ativo)
                self.assertIsNone(b.data_desligamento)
                self.assertEqual(b.data_fim_bolsa, datetime.date(2026, 12, 1))
                print(f"Restored End Date: {b.data_fim_bolsa}")
                
        except Exception as e:
            import traceback
            with open('test_exception.txt', 'w', encoding='utf-8') as f:
                f.write(str(e) + "\n" + traceback.format_exc())
            raise e

if __name__ == '__main__':
    unittest.main()
