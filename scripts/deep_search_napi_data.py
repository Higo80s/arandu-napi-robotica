import os

search_paths = [
    r'C:\Users\higosantos\Documents\gestao_editais\arandu-napi-robotica',
    r'C:\Users\higosantos\Documents\gestao_editais\gestao_editais_novo'
]

target_names = [b'Missae', b'Figueiredo', b'ROBOTICA']

print("Buscando dados NAPI nos arquivos de backup e scripts...")

for base in search_paths:
    for root, dirs, files in os.walk(base):
        for file in files:
            if file.endswith(('.db', '.sql', '.py', '.txt', '.md', '.csv', '.zip')):
                path = os.path.join(root, file)
                try:
                    with open(path, 'rb') as f:
                        content = f.read()
                        for target in target_names:
                            if target in content:
                                print(f"[ACHADO] '{target.decode()}' no arquivo: {path}")
                                # Se for um ZIP, não conseguiremos ver o conteúdo interno facilmente aqui,
                                # mas o nome do arquivo já é uma pista.
                                break
                except:
                    pass

print("Busca encerrada.")
