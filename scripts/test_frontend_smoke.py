
import requests

BASE_URL = "http://127.0.0.1:5000"

ROUTES = [
    "/",
    "/bolsistas/",
    "/bolsistas/novo",
    "/posdoc",
    "/relatorios/"
]

def check_routes():
    print("Checking Frontend Routes...")
    all_ok = True
    for route in ROUTES:
        url = BASE_URL + route
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                print(f"[OK] {route} - 200 OK")
            else:
                print(f"[FAIL] {route} - Status {resp.status_code}")
                all_ok = False
        except Exception as e:
            print(f"[FAIL] {route} - Connectivity Error: {e}")
            all_ok = False
            
    if all_ok:
        print("\nSUCCESS: All critical routes accessible.")
    else:
        print("\nFAILURE: Some routes failed.")

if __name__ == "__main__":
    check_routes()
