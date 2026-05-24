# Script para injetar o menu Admin no base.html

html_content = """
    <!-- Seção Admin (Injetado) -->
    <li style="margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px solid rgba(255,255,255,0.1);">
        <small style="display: block; padding: 0 1rem; color: var(--text-muted); font-size: 0.7rem; text-transform: uppercase;">Administração</small>
    </li>
    <li>
        <a href="{{ url_for('admin_consolidado') }}" class="nav-link">
            {{ icon('pie-chart', size=20, class='mr-2') }} Painel Consolidado
        </a>
    </li>
    <li>
        <a href="{{ url_for('admin_programas_lista') }}" class="nav-link">
            {{ icon('settings', size=20, class='mr-2') }} Gestão de Programas
        </a>
    </li>
"""

with open('templates/base.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
inserted = False

for line in lines:
    # Procurar o divisor da seção downloads para inserir ANTES dele
    if "text-transform: uppercase;\">Downloads</small>" in line and not inserted:
        # Voltar um pouco para pegar o início do LI ou UL se necessário
        # Mas aqui, como é um LI separado, podemos inserir antes
        # O divisor original começa com <li style="margin-top...
        
        # Vamos inserir antes do LI que contem "Downloads"
        # Mas o LI começa umas linhas antes.
        
        # Abordagem melhor: Procurar o 'Painel CAPES' e inserir DEPOIS dele, se Downloads falhar
        # Ou procurar a linha exata.
        pass
    
    new_lines.append(line)

# Abordagem 2: Ler tudo como string
with open('templates/base.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Verifica se já existe
if "Gestão de Programas" in content:
    print("✅ Link já existe!")
    exit()

# Alvo: tutorial online (último item antes de downloads)
target_tutorial = "{{ icon('help-circle', size=20, class='mr-2') }} Tutorial Online"

if target_tutorial in content:
    # Encontrar o fechamento do LI do tutorial
    split_point = content.find(target_tutorial)
    # Avançar até o próximo </li>
    end_li = content.find("</li>", split_point) + 5
    
    final_content = content[:end_li] + "\n" + html_content + "\n" + content[end_li:]
    
    with open('templates/base.html', 'w', encoding='utf-8') as f:
        f.write(final_content)
    print("✅ Menu inserido com sucesso após Tutorial Online!")
else:
    print("⚠️ Não foi possível encontrar ponto de inserção seguro (Tutorial Online).")
