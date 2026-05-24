# Script para remover tags img com twemoji

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
        
        # Remover tags <img> que contenham twemoji
        # Pattern: <img class="emoji" ...src="...twemoji...">
        pattern = r'<img[^>]*twemoji[^>]*>'
        content = re.sub(pattern, '', content)
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'✓ {filepath}')
        else:
            print(f'- {filepath} (sem alterações)')
    except Exception as e:
        print(f'⚠️ {filepath}: {e}')

print('✅ Twemoji removidos!')
