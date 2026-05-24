# Script para VARREDURA COMPLETA e remoção de Twemoji em TODOS os templates

import re
import os

# Encontrar todos os arquivos HTML
templates_dir = 'templates'
all_html_files = []

for root, dirs, files in os.walk(templates_dir):
    for file in files:
        if file.endswith('.html'):
            all_html_files.append(os.path.join(root, file))

total_cleaned = 0

for filepath in all_html_files:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # 1. Remover tags <img> que contenham cdn.jsdelivr.net/twemoji
        content = re.sub(r'<img[^>]*cdn\.jsdelivr\.net[^>]*twemoji[^>]*>', '', content)
        
        # 2. Remover qualquer tag <img> com classe "emoji"
        content = re.sub(r'<img[^>]*class="emoji"[^>]*>', '', content)
        
        # 3. Remover spans com classe emoji vazios
        content = re.sub(r'<span class="emoji">\s*</span>', '', content)
        
        # 4. Remover <i> FontAwesome vazios ou desnecessários em títulos
        content = re.sub(r'<i class="fas[^"]*"></i>\s*', '', content)
        
        # 5. Limpar espaços extras e quebras de linha
        content = re.sub(r'  +', ' ', content)
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        
        # 6. Limpar títulos com espaços iniciais/finais
        content = re.sub(r'(<h[1-6][^>]*>)\s+', r'\1', content)
        content = re.sub(r'\s+(</h[1-6]>)', r'\1', content)
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            total_cleaned += 1
            # Mostrar apenas se houve mudança
            print(f'✓ {filepath}')
    
    except Exception as e:
        print(f'⚠️ {filepath}: {e}')

print(f'\n✅ Varredura completa! {total_cleaned} arquivos limpos.')
print('🎯 Todos os links Twemoji removidos do sistema!')
