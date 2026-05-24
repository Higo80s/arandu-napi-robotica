# Script para remover Twemoji de base.html e login.html

files = ['templates/base.html', 'templates/login.html']

for file_path in files:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        new_lines = []
        skip = False
        
        for line in lines:
            # Remover CDN
            if 'twemoji.min.js' in line or 'Twemoji CDN' in line:
                continue
            
            # Remover bloco de init
            if 'twemoji.parse(document.body' in line:
                skip = True
                continue
            
            if skip:
                if '});' in line:
                    skip = False
                continue
            
            new_lines.append(line)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
            
        print(f"✅ Twemoji removido de {file_path}")
        
    except FileNotFoundError:
        print(f"⚠️ Arquivo não encontrado: {file_path}")

print("Limpeza concluída!")
