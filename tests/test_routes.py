from app import app, db, Edital

def test_routes():
    client = app.test_client()
    
    # 1. Test Index
    response = client.get('/editais')
    print(f"GET /editais: {response.status_code}")
    assert response.status_code == 200
    
    # 2. Test New Form
    response = client.get('/editais/novo')
    print(f"GET /editais/novo: {response.status_code}")
    assert response.status_code == 200
    
    # 3. Test Create Action
    with app.app_context():
        # Clean up previous test data
        old = Edital.query.filter_by(numero="TEST-001").first()
        if old:
            db.session.delete(old)
            db.session.commit()

    response = client.post('/editais/novo', data={
        'numero': 'TEST-001',
        'descricao': 'Edital de Teste',
        'agencia': 'CNPq',
        'codigo_projeto': '',
        'descricao_projeto': ''
    }, follow_redirects=True)
    print(f"POST /editais/novo: {response.status_code}")
    assert response.status_code == 200
    assert b'Edital criado com sucesso' in response.data

    print("✓ All routes verified successfully!")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    test_routes()
