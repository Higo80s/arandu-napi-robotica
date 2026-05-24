# Script para adicionar links CSS faltantes ao base.html

with open('templates/base.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Adicionar CSS logout e tema Jegua
if 'logout.css' not in content:
    # Procurar onde adicionar (depois de landing.css)
    landing_pos = content.find('landing.css')
    if landing_pos != -1:
        line_end = content.find('\n', landing_pos)
        if line_end != -1:
            css_links = '\n    <link rel="stylesheet" href="{{ url_for(\'static\', filename=\'css/logout.css\') }}">\n    <link rel="stylesheet" href="{{ url_for(\'static\', filename=\'css/theme-jegua.css\') }}">'
            content = content[:line_end+1] + css_links + content[line_end+1:]
            print('✓ CSS logout e tema-jegua adicionados')
    
    with open('templates/base.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ base.html atualizado!')
else:
    print('⚠️ CSS já adicionados')
