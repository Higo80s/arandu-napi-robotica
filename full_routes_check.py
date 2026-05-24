from app import app
with app.app_context():
    print("ALL RULES:")
    for rule in app.url_map.iter_rules():
        print(f"RULE: {rule.rule} -> ENDPOINT: {rule.endpoint}")
