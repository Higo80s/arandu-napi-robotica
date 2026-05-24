# Script para remover TODAS as imagens/ícones de alertas e tutorial

import re

files = [
    'templates/alertas/index.html',
    'templates/tutorial.html'
]

for filepath in files:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # 1. Remover tags <img> (qualquer tipo)
        content = re.sub(r'<img[^>]*>', '', content)
        
        # 2. Remover macros {{ icon(...) }}
        content = re.sub(r'\{\{\s*icon\([^)]+\)\s*\}\}', '', content)
        
        # 3. Remover espaços duplos resultantes
        content = re.sub(r'  +', ' ', content)
        
        # 4. Limpar linhas vazias consecutivas
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'✓ {filepath} - Imagens removidas')
        else:
            print(f'- {filepath} - Sem alterações')
    except Exception as e:
        print(f'⚠️ {filepath}: {e}')

print('\n✅ Todas as imagens/ícones removidos de alertas e tutorial!')
