# Script para adicionar favicon e marca d'água ao base.html

with open('templates/base.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Adicionar favicon no <head>
if 'simbolo_marangatu' not in content:
    # Procurar </title> e adicionar depois
    title_end = content.find('</title>')
    if title_end != -1:
        favicon_tag = '\n    \n    <!-- Favicon - Símbolo Marangatu -->\n    <link rel="icon" type="image/png" href="{{ url_for(\'static\', filename=\'images/simbolo_marangatu.png\') }}">\n    '
        content = content[:title_end+8] + favicon_tag + content[title_end+8:]
        print('✓ Favicon adicionado')

# 2. Adicionar CSS marca d'água
if 'marca_dagua.css' not in content:
    # Procurar responsive.css e adicionar depois
    responsive_pos = content.find('responsive.css')
    if responsive_pos != -1:
        # Encontrar o final da linha
        line_end = content.find('\n', responsive_pos)
        if line_end != -1:
            marca_css = '    <link rel="stylesheet" href="{{ url_for(\'static\', filename=\'css/marca_dagua.css\') }}">\n'
            content = content[:line_end+1] + marca_css + content[line_end+1:]
            print('✓ marca_dagua.css adicionado')

# Salvar
with open('templates/base.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ base.html atualizado!')
