import requests
import datetime

def test_create_bolsista():
    base_url = "http://127.0.0.1:5003"
    
    # 1. Get Edital & Modalidade to use
    print("Fetching Editais...")
    # Since we can't easily parse HTML without BS4, let's just assume some defaults or try to use models directly?
    # No, let's use the app context to get IDs, then Requests for the HTTP test against running server
    # Actually, simpler: Use 'app_flask' context to get IDs, then requests.post
    
    from app import app
    from models import Edital, Modalidade
    
    with app.app_context():
        edital = Edital.query.first()
        if not edital:
            print("No editais found. Creating one for test...")
            # We need to create data to test
            from models import db
            e = Edital(numero="99/2025", agencia="Test", descricao="Test")
            db.session.add(e)
            db.session.commit()
            
            m = Modalidade(edital_id=e.id, nivel="Mestrado", vagas=1, valor_mensal=1500, max_meses=12)
            db.session.add(m)
            db.session.commit()
            edital_id = e.id
            modalidade_id = m.id
        else:
            edital_id = edital.id
            if not edital.modalidades:
                print("Edital has no modalidades. Creating...")
                m = Modalidade(edital_id=edital.id, nivel="Mestrado", vagas=1, valor_mensal=1500, max_meses=12)
                db.session.add(m)
                db.session.commit()
                modalidade_id = m.id
            else:
                modalidade_id = edital.modalidades[0].id
                
        print(f"Using Edital {edital_id}, Modalidade {modalidade_id}")

    # 2. Prepare Payload
    payload = {
        'modalidade_id': modalidade_id,
        'nome': 'Teste Auto',
        'cpf': '000.000.000-00',
        'email': 'teste@example.com',
        'orientador': 'Prof Teste',
        'email_orientador': 'orientador@example.com',
        'campus': 'Curitiba',
        'programa': 'PPG Teste',
        'data_inicio_curso': '2025-01-01',
        'previsao_defesa': '2027-01-01',
        'data_inicio_bolsa': '2025-03-01',
        'meses_duracao': '12',
        'data_fim_bolsa': '2026-02-28', # Valid end date
        'banco': 'BB',
        'agencia': '1234',
        'conta': '5678',
        'tipo_conta': 'corrente',
        'processo_sei': '',
        'comentarios': ''
    }
    
    print("Sending POST to /bolsistas/novo...")
    try:
        resp = requests.post(f"{base_url}/bolsistas/novo", data=payload)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 500:
            print("!!! INTERNAL SERVER ERROR ON POST !!!")
        else:
            print("Success (or redirect)")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_create_bolsista()
