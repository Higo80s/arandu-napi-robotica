
import sys
import os
from datetime import date

# Adicionar o diretório raiz ao path para importar os módulos do app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from extensions import db
from models import Bolsista, Modalidade
from services.bolsista_service import BolsistaService

def test_sparkx_trigger():
    app = create_app()
    with app.app_context():
        print("--- Iniciando Teste de Trigger SPARKx ---")
        
        # 1. Teste: Bolsista Sem E-mail de Orientador (Deve Falhar)
        b1 = Bolsista(nome="Teste Sem Orientador", email="bolsista@teste.com", orientador="Dr. Teste")
        success, msg = BolsistaService.trigger_sparkx_onboarding(b1)
        print(f"Bolsista sem e-mail orientador: {success} - {msg}")
        
        # 2. Teste: Bolsista Com Orientador (Deve Passar - Simulado)
        b2 = Bolsista(nome="Higo Santos", email="higo@napi.com", orientador="Dr. Robotica", email_orientador="orientador@napi.com")
        # Simular modalidade para evitar erro de nivel
        m = Modalidade(nivel="Mestrado", valor_mensal=2100.0)
        b2.modalidade = m
        b2.data_inicio_bolsa = date(2026, 1, 1)
        
        success, msg = BolsistaService.trigger_sparkx_onboarding(b2)
        print(f"Bolsista com e-mail orientador: {success} - {msg}")
        
        print("\n--- Teste de Cálculo de Parcela X/Y ---")
        hoje = date.today()
        # Se começou em Jan/2026 e hoje é Março/2026 -> Parcela 3/12
        p_atual = BolsistaService.calculate_current_installment(b2)
        print(f"Início: Jan/2026. Hoje: {hoje.strftime('%m/%Y')}. Parcela calculada: {p_atual}")
        
        print("\n--- Teste de 5º Dia Útil ---")
        abril_5du = BolsistaService.get_5th_business_day(2026, 4)
        print(f"5º Dia Útil de Abril/2026: {abril_5du.strftime('%d/%m/%Y')} (Esperado: 08/04/2026 - Abril/2026 começa na quarta, feriado sexta 03/04 Paixão?)")
        # 01/04 Qua (1), 02/04 Qui (2). 03/04 Sex (Feriado), 04/04 Sab, 05/04 Dom. 06/04 Seg (3), 07/04 Ter (4), 08/04 Qua (5).
        
        print("\n--- Fim dos Testes ---")

if __name__ == "__main__":
    test_sparkx_trigger()
