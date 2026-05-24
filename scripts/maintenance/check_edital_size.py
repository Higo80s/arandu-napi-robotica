
import json
import os

files = [f for f in os.listdir('.') if f.startswith('universal_dump') and f.endswith('.json')]
latest_file = sorted(files)[-1]

with open(latest_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

editais = data.get('editais', [])
print(f"Analisando {len(editais)} editais...")

max_agencia = 0
max_cod = 0
max_sei = 0

for e in editais:
    # Checar tamanhos
    agencia = len(e.get('agencia', '') or '')
    codigo_projeto = len(e.get('codigo_projeto', '') or '')
    processo_sei = len(e.get('processo_sei', '') or '')
    
    if agencia > max_agencia: max_agencia = agencia
    if codigo_projeto > max_cod: max_cod = codigo_projeto
    if processo_sei > max_sei: max_sei = processo_sei

print(f"MAX AGENCIA: {max_agencia}")
print(f"MAX COD PROJETO: {max_cod}")
print(f"MAX SEI: {max_sei}")
