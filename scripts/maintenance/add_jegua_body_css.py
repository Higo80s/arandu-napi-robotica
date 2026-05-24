# Script para adicionar CSS tema Jegua body ao base.html

with open('templates/base.html', 'r', encoding='utf-8') as f:
    content = f.read()

if 'theme-jegua-body.css' not in content:
    # Procurar theme-jegua.css e adicionar depois
    jegua_pos = content.find('theme-jegua.css')
    if jegua_pos != -1:
        line_end = content.find('\n', jegua_pos)
        if line_end != -1:
            body_css = '\n    <link rel="stylesheet" href="{{ url_for(\'static\', filename=\'css/theme-jegua-body.css\') }}">'
            content = content[:line_end+1] + body_css + content[line_end+1:]
            print('✓ theme-jegua-body.css adicionado')
    
    with open('templates/base.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ base.html atualizado!')
else:
    print('⚠️ CSS já existe')
