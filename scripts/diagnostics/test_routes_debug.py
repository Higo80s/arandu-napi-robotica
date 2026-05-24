from app import app
import sys

def test_routes():
    print("Initializing test client...")
    client = app.test_client()
    
    routes = [
        '/',
        '/editais',
        '/bolsistas',
        '/relatorios'
    ]
    
    with app.app_context():
        for route in routes:
            print(f"Testing route: {route}...")
            try:
                response = client.get(route)
                print(f"   Status Code: {response.status_code}")
                if response.status_code == 500:
                    print(f"   !!! INTERNAL SERVER ERROR ON {route} !!!")
                    # Determining if we can extract more info
            except Exception as e:
                print(f"   EXCEPTION on {route}: {e}")
                import traceback
                traceback.print_exc()

if __name__ == "__main__":
    test_routes()
