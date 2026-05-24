
import json
import os

files = [f for f in os.listdir('.') if f.startswith('universal_dump') and f.endswith('.json')]
latest_file = sorted(files)[-1]
with open(latest_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

for e in data.get('editais', []):
    if 'Renault' in (e.get('descricao') or '') or 'Renault' in (e.get('descricao_projeto') or ''):
        print("--- REGISTRO ENCONTRADO ---")
        for k, v in e.items():
            print(f"{k} ({type(v).__name__}): {v}")
