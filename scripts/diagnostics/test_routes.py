from app_flask import app

print("--- REGISTERED ROUTES ---")
for rule in app.url_map.iter_rules():
    print(f"{rule.endpoint}: {rule}")
print("--- END ROUTES ---")
