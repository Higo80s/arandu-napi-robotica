import sys
import os

# Adicionar o diretório raiz ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from extensions import db
from models import UIState

def init_ui():
    with app.app_context():
        # Novos Rótulos NAPI-Robótica / FUNTEF
        labels = {
            # Navegação
            'nav_bolsistas': 'Bolsistas',
            'nav_proap': 'Recursos',
            'brand_name': 'Arandú Napi-Robótica',
            
            # Títulos de Páginas e Botões
            'page_title_bolsistas': 'Bolsistas',
            'btn_new_bolsista': 'Novo(a) Bolsista',
            
            # Alertas e Mensagens Corporativas
            'alert_title_cancellation': '🔴 Ação Requerida: Cancelamentos Pendentes',
            'alert_msg_cancellation': 'Bolsistas ativos(as) cuja previsão de defesa já está vencida — o pagamento continua sendo debitado indevidamente. Verifique cada caso nos sistemas e encerre a cota.',
            'alert_msg_cpf_conflict': 'CPFs duplicados ou matrículas divergentes entre o sistema acadêmico e a base FUNTEF/CONVENIAR. Use Mesclar ou Manter para resolver cada conflito.',
            
            # Identificação de Projetos (Relatórios)
            'report_header_project': 'NAPI-Robótica / UTFPR',
            'report_header_agency': 'FUNTEF / CONVENIAR',
            'report_title_finance': 'Relatório de Bolsistas - NAPI-Robótica / FUNTEF'
        }
        
        print("Sincronizando rótulos NAPI-Robótica...")
        for key, value in labels.items():
            state = UIState.query.filter_by(element_key=key).first()
            if not state:
                state = UIState(element_key=key, current_text=value, page_context="napi_rebranding")
                db.session.add(state)
                print(f" [+] Criado: {key} -> {value}")
            else:
                state.current_text = value
                print(f" [*] Atualizado: {key} -> {value}")
        
        db.session.commit()
        print("Sincronização concluída com sucesso!")

if __name__ == "__main__":
    init_ui()
