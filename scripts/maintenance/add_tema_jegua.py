# Script para adicionar tema Jegua ao JavaScript

with open('static/js/theme.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Adicionar tema Jegua ao objeto themes
jegua_theme = """
    'jegua': {
        name: 'Jegua (Amazônia)',
        icon: '🌿',
        description: 'Tema inspirado na floresta amazônica'
    },"""

if 'jegua' not in content:
    # Procurar onde adicionar (depois de 'utfpr')
    utfpr_pos = content.find("'utfpr': {")
    if utfpr_pos != -1:
        # Encontrar o final do objeto utfpr
        bracket_count = 0
        i = utfpr_pos
        while i < len(content):
            if content[i] == '{':
                bracket_count += 1
            elif content[i] == '}':
                bracket_count -= 1
                if bracket_count == 0:
                    # Encontrou o fim do utfpr
                    # Procurar a vírgula após }
                    comma_pos = content.find(',', i)
                    if comma_pos != -1:
                        content = content[:comma_pos+1] + jegua_theme + content[comma_pos+1:]
                        print('✓ Tema Jegua adicionado ao theme.js')
                        break
            i += 1
    
    # Atualizar ordem de ciclo dos temas
    if "'light', 'dark', 'utfpr'" in content:
        content = content.replace("'light', 'dark', 'utfpr'", "'light', 'dark', 'utfpr', 'jegua'")
        print('✓ Jegua adicionado ao ciclo de temas')
    
    with open('static/js/theme.js', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ theme.js atualizado!')
else:
    print('⚠️ Tema Jegua já existe')
