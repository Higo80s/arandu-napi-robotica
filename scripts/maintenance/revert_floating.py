# Script para reverter imagem flutuante do login

import os

# 1. Remover div flutuante do login.html
with open('templates/login.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Remover bloco da imagem flutuante
start_marker = '<!-- Imagem Flutuante Interativa -->'
end_marker = '</div>\n\n <div class="login-container">'

if start_marker in content:
    start_idx = content.find(start_marker)
    end_idx = content.find('</div>', start_idx) + len('</div>\n\n')
    
    # Remover bloco completo
    content = content[:start_idx] + content[end_idx:]
    
    # Remover links CSS e JS
    content = content.replace('\n  <link rel="stylesheet" href="{{ url_for(\'static\', filename=\'css/floating-symbol.css\') }}">', '')
    content = content.replace('\n  <script src="{{ url_for(\'static\', filename=\'js/floating-drag.js\') }}"></script>', '')
    
    with open('templates/login.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✓ login.html restaurado')

# 2. Deletar arquivos criados
files_to_delete = [
    'static/css/floating-symbol.css',
    'static/js/floating-drag.js',
    'static/images/simbolo_flutuante.png',
    'add_floating_to_login.py'
]

for filepath in files_to_delete:
    if os.path.exists(filepath):
        os.remove(filepath)
        print(f'✓ {filepath} removido')

print('\n✅ Animação flutuante removida! Sistema restaurado.')
