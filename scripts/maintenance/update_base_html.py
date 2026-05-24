# Script para adicionar landing.css e landing.js ao base.html

with open('templates/base.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Adicionar landing.css após styles.css
if 'landing.css' not in content:
    content = content.replace(
        '<link rel="stylesheet" href="{{ url_for(\'static\', filename=\'css/styles.css\') }}">',
        '<link rel="stylesheet" href="{{ url_for(\'static\', filename=\'css/styles.css\') }}">\n    <link rel="stylesheet" href="{{ url_for(\'static\', filename=\'css/landing.css\') }}">'
    )
    print('✓ landing.css adicionado')

# Adicionar landing.js antes de </body>
if 'landing.js' not in content:
    content = content.replace(
        '</body>',
        '    <script src="{{ url_for(\'static\', filename=\'js/landing.js\') }}"></script>\n</body>'
    )
    print('✓ landing.js adicionado')

with open('templates/base.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ base.html atualizado!')
