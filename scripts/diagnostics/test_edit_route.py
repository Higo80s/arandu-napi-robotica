from app import app
from models import Bolsista

def test_edit():
    with app.app_context():
        b = Bolsista.query.first()
        if not b:
            print("No bolsista found.")
            return

        print(f"Testing Edit Route for Bolsista {b.id}...")
        client = app.test_client()
        try:
            resp = client.get(f'/bolsistas/{b.id}/editar')
            print(f"Status: {resp.status_code}")
            if resp.status_code == 200:
                print("Render OK")
            else:
                print("Render FAILED")
                # print(resp.data.decode('utf-8')) # Too large, don't print
        except Exception as e:
            print(f"Exception: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_edit()
