import sys
import os

# Force current directory first
sys.path.insert(0, os.getcwd())

print("Python version:", sys.version)
print("CWD:", os.getcwd())
print("sys.path:", sys.path[:3])

print("\n--- Testing Import ---")
from app import app, db

print(f"App: {app}")
print(f"DB: {db}")
print(f"App name: {app.name}")
print(f"Number of routes: {len(list(app.url_map._rules))}")

print("\n--- First 15 Routes ---")
for i, rule in enumerate(list(app.url_map._rules)[:15]):
    print(f"{i+1}. {rule.rule} -> {rule.endpoint}")

print("\n--- Testing Index Route ---")
with app.test_client() as client:
    r = client.get('/')
    print(f"Status: {r.status_code}")
   
print("\n--- API Dashboard Data Route ---")
with app.test_client() as client:
    r = client.get('/api/dashboard-data')
    print(f"Status: {r.status_code}")
