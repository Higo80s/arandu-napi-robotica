# Script para LIMPAR TODOS os emojis/ícones de alertas, tutorial e relatórios

import re

files_to_clean = [
    'templates/alertas/index.html',
    'templates/tutorial.html',
    'templates/relatorios/index.html'
]

for filepath in files_to_clean:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # 1. Remover TODAS as tags <img>
        content = re.sub(r'<img[^>]*>', '', content)
        
        # 2. Remover macros {{ icon(...) }}
        content = re.sub(r'\{\{\s*icon\([^)]+\)\s*\}\}', '', content)
        
        # 3. Remover entidades HTML de emojis comuns
        emoji_entities = [
            '&#128194;',  # 📁
            '&amp;#128194;',
            '⚠️', '✅', '🎓', '📊', '📧', '📁', '👤',
            '📄', '🔬', '📉', '❓', '📘', '💾', '🏛️', '📚', '📋'
        ]
        
        for emoji in emoji_entities:
            content = content.replace(emoji, '')
        
        # 4. Remover spans com classe emoji
        content = re.sub(r'<span class="emoji"[^>]*>.*?</span>', '', content)
        
        # 5. Remover ícones FontAwesome <i class="fas...">
        content = re.sub(r'<i class="fas[^"]*"[^>]*></i>', '', content)
        
        # 6. Limpar espaços extras
        content = re.sub(r'  +', ' ', content)
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        
        # 7. Limpar títulos com espaços no início
        content = re.sub(r'<h([1-6])>\s+', r'<h\1>', content)
        content = re.sub(r'<div class="card-title[^"]*">\s+', r'<div class="card-title">', content)
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'✓ {filepath}')
        else:
            print(f'- {filepath} (sem alterações)')
            
    except Exception as e:
        print(f'⚠️ {filepath}: {e}')

print('\n✅ Limpeza completa realizada!')
