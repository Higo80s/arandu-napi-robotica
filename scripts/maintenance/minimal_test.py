
import json
import os

try:
    files = [f for f in os.listdir('.') if f.startswith('universal_dump') and f.endswith('.json')]
    if not files:
        print("Sem arquivo")
        exit()
        
    latest_file = sorted(files)[-1]
    print(f"Lendo {latest_file}...")
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    print(f"SUCESSO! Li {len(data.keys())} chaves.")
    
except Exception as e:
    print(f"ERRO: {e}")
