import sys

file_path = r'C:\Users\higosantos\Documents\gestao_editais\arandu-napi-robotica\backups\napi\rebirth_success.sql'

print(f"Lendo {file_path} em busca de NAPI-ROBOTICA...")

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if "NAPI-ROBOTICA" in line.upper():
                print(f"Linha {i}: {line.strip()[:200]}")
except Exception as e:
    print(f"Erro ao ler: {e}")
