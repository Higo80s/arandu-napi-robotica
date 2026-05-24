
import urllib.request
import urllib.parse
from app import app
from models import db, Bolsista

# Ensure we can use DB
with app.app_context():
    b = Bolsista.query.first()
    if not b:
        print("No bolsista found to test.")
        exit()
    
    bid = b.id
    print(f"Testing with Bolsista ID: {bid}")
    
    url = f"http://127.0.0.1:5002/bolsistas/{bid}/afastamento/novo"
    data = {
        'tipo': 'saude',
        'data_inicio': '2025-01-01',
        'duracao_meses': '1',
        'observacao': 'Teste Debug'
    }
    
    data_encoded = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=data_encoded, method='POST')
    
    try:
        with urllib.request.urlopen(req) as response:
            print(f"Status Code: {response.status}")
            print(f"Response: {response.read().decode()[:500]}")
    except urllib.error.HTTPError as e:
        print(f"Expected Error Caught: {e.code} {e.reason}")
        print(f"Error Body: {e.read().decode()[:500]}")
    except Exception as e:
        print(f"Request failed: {e}")
