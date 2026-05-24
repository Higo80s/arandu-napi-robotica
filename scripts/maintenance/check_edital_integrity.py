
import json
import os

files = [f for f in os.listdir('.') if f.startswith('universal_dump') and f.endswith('.json')]
latest_file = sorted(files)[-1]
with open(latest_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

editais = data.get('editais', [])
print(f"Checando integridade de {len(editais)} editais...")

for e in editais:
    eid = e.get('id')
    num = e.get('numero')
    agencia = e.get('agencia')
    
    if num is None:
        print(f"ERRO: Edital {eid} tem numero NULL")
    if agencia is None:
        print(f"ERRO: Edital {eid} tem agencia NULL")

print("Fim.")
