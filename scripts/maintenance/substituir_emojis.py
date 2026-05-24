# Script para substituir emojis por Lucide Icons

import re

emoji_to_lucide = {
    '📊': "{{ icon('bar-chart', size=20) }}",
    '🎓': "{{ icon('graduation-cap', size=20) }}",
    '☀️': "{{ icon('sun', size=20) }}",
    '👤': "{{ icon('user', size=20) }}",
    '✅': "{{ icon('check-circle', size=20) }}",
    '⚠️': "{{ icon('alert-circle', size=20) }}",
    '📧': "{{ icon('mail', size=18) }}",
    '🔬': "{{ icon('microscope', size=20) }}",
    '⚙️': "{{ icon('settings', size=20) }}",
    '📋': "{{ icon('clipboard', size=20) }}",
    '📚': "{{ icon('book-open', size=20) }}"
}

files_to_update = [
    'templates/capes/dashboard.html',
    'templates/base.html',
    'templates/tutorial.html',
    'templates/sobre_simbolo.html',
    'templates/alertas/index.html',
    'templates/editais/index.html',
    'templates/editais/modalidades.html',
    'templates/posdoc/index.html',
    'templates/posdoc/form.html',
    'templates/bolsistas/form.html'
]

total_replaced = 0

for filepath in files_to_update:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        for emoji, lucide in emoji_to_lucide.items():
            content = content.replace(emoji, lucide)
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            total_replaced += 1
            print(f'✓ {filepath}')
    except Exception as e:
        print(f'⚠️ {filepath}: {e}')

print(f'\n✅ {total_replaced} arquivos atualizados!')
