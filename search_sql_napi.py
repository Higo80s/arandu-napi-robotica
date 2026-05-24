import re

file_path = r'C:\Users\higosantos\Documents\gestao_editais\arandu-napi-robotica\backups\napi\rebirth_success.sql'

print(f"Buscando 'NAPI-ROBOTICA' e bolsistas no arquivo SQL...")

search_patterns = [
    re.compile(b'C-NAPI-ROBOTICA', re.IGNORECASE),
    re.compile(b'Higo Figueiredo', re.IGNORECASE),
    re.compile(b'Missae Yanase', re.IGNORECASE)
]

with open(file_path, 'rb') as f:
    for i, line in enumerate(f, 1):
        for pattern in search_patterns:
            if pattern.search(line):
                print(f"ACHADO na linha {i}: {line[:200].decode('utf-8', 'ignore').strip()}")

print("Busca concluída.")
