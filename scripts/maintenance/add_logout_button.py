# Script para adicionar botão de logout no topbar

with open('templates/base.html', 'r', encoding='utf-8') as f:
    content = f.read()

logout_button = '''
                    <!-- Botão Logout -->
                    <a href="{{ url_for('logout') }}" class="btn-logout" title="Sair do Sistema">
                        {{ icon('log-out', size=18) }}
                        <span class="logout-text">Sair</span>
                    </a>'''

# Adicionar antes do fechamento da topbar
if 'btn-logout' not in content:
    # Procurar o themeBtn e adicionar depois
    theme_btn_pos = content.find('id="themeBtn"')
    if theme_btn_pos != -1:
        # Encontrar o final do botão
        button_end = content.find('</button>', theme_btn_pos)
        if button_end != -1:
            content = content[:button_end+9] + logout_button + content[button_end+9:]
            print('✓ Botão de logout adicionado')
    
    with open('templates/base.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ base.html atualizado!')
else:
    print('⚠️ Botão já existe')
