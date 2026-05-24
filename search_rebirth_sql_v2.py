import os

file_path = r'C:\Users\higosantos\Documents\gestao_editais\arandu-napi-robotica\backups\napi\rebirth_success.sql'

print(f"Lendo {file_path} em busca de NAPI-ROBOTICA...")

targets = [b'C-NAPI-ROBOTICA', b'Missae', b'Figueiredo']

try:
    with open(file_path, 'rb') as f:
        content = f.read()
        for target in targets:
            if target in content:
                print(f"  [ACHADO!] '{target.decode()}' está no arquivo SQL!")
            else:
                print(f"  [X] '{target.decode()}' NÃO encontrado.")
except Exception as e:
    print(f"Erro ao ler: {e}")
