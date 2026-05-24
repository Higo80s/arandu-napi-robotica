import os

search_paths = [
    r'C:\Users\higosantos\Documents\gestao_editais\arandu-napi-robotica',
    r'C:\Users\higosantos\Documents\gestao_editais\gestao_editais_novo'
]

targets = [b'Missae', b'Figueiredo', b'C-NAPI-ROBOTICA']

print("Buscando dados NAPI em arquivos SQL, DB, TXT, PY...")

for base_path in search_paths:
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if any(file.endswith(ext) for ext in ['.sql', '.db', '.py', '.txt', '.md', '.csv', '.dump']):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'rb') as f:
                        content = f.read()
                        for target in targets:
                            if target in content:
                                print(f"[ACHADO] '{target.decode()}' no arquivo: {file_path}")
                                break
                except:
                    pass

print("Busca concluída.")
