from app import app
from models import Bolsista

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gestao_editais.db'

def test():
    with app.app_context():
        # Just pick ID 1 or first
        b = Bolsista.query.first()
        bid = b.id if b else 1
        print(f"Testing ID {bid}")
        c = app.test_client()
        r = c.get(f'/bolsistas/{bid}/editar')
        print(f"Status: {r.status_code}")

if __name__ == "__main__":
    test()
