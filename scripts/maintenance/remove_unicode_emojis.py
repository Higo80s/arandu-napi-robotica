# Script para remover emojis Unicode específicos

import re

files = {
    'templates/tutorial.html': ['🚀', '🤓', '🐛', '🐙'],
    'templates/alertas/index.html': ['⏳', '🚨']
}

for filepath, emojis in files.items():
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # Remover cada emoji
        for emoji in emojis:
            content = content.replace(emoji, '')
        
        # Limpar espaços duplos resultantes
        content = re.sub(r'  +', ' ', content)
        
        # Limpar tags que ficaram com só espaço
        content = re.sub(r'>(\s+)<', '><', content)
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'✓ {filepath} - {len(emojis)} emojis removidos')
        else:
            print(f'- {filepath} - Sem alterações')
    
    except Exception as e:
        print(f'⚠️ {filepath}: {e}')

print('\n✅ Emojis Unicode removidos!')
