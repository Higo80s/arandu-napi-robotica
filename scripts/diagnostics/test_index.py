from app import app

app.config['TESTING'] = True
app.config['PROPAGATE_EXCEPTIONS'] = True

def test_index():
    print("Testing index route...")
    with app.test_client() as client:
        try:
            response = client.get('/')
            print(f"Status: {response.status_code}")
            if response.status_code == 500:
                print("ERROR: 500 on index")
        except Exception as e:
            print(f"Exception: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_index()
