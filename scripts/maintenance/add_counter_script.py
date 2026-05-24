# Script para adicionar script de contadores e CSS inline-icons ao base.html

with open('templates/base.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Adicionar script counter antes do fechamento </body>
if 'counter-animation.js' not in content:
    counter_script = '\n    <script src="{{ url_for(\'static\', filename=\'css/counter-animation.js\') }}"></script>'
    content = content.replace('</body>', counter_script + '\n</body>')
    print('✓ counter-animation.js adicionado')

# Adicionar CSS inline-icons
if 'inline-icons.css' not in content:
    # Procurar theme-jegua.css e adicionar depois
    jegua_pos = content.find('theme-jegua.css')
    if jegua_pos != -1:
        line_end = content.find('\n', jegua_pos)
        if line_end != -1:
            inline_css = '\n    <link rel="stylesheet" href="{{ url_for(\'static\', filename=\'css/inline-icons.css\') }}">'
            content = content[:line_end+1] + inline_css + content[line_end+1:]
            print('✓ inline-icons.css adicionado')

with open('templates/base.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ base.html atualizado!')
