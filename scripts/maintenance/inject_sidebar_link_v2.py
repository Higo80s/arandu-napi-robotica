
# Script para inserir link do Consolidado V2 abaixo de Programas V2

target_line_part = "Programas (Novo)"
html_to_insert = """    <li>
        <a href="{{ url_for('admin_consolidado_v2') }}" class="nav-link" style="color: var(--primary-color);">
            {{ icon('pie-chart', size=20, class='mr-2') }} Consolidado (Novo)
        </a>
    </li>
"""

file_path = 'templates/base.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

if "Consolidado (Novo)" in content:
    print("✅ Link já existe!")
else:
    # Procurar o fechamento do LI do programa v2
    # O user link tem "Programas (Novo)"
    idx = content.find(target_line_part)
    if idx != -1:
        # Achar o </li> depois disso
        end_li_idx = content.find("</li>", idx)
        if end_li_idx != -1:
            end_li_idx += 5 # pular </li>
            
            new_content = content[:end_li_idx] + "\n" + html_to_insert + content[end_li_idx:]
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("✅ Inserido com sucesso!")
        else:
            print("❌ Não achei o fechamento do LI")
    else:
        print("❌ Não achei o link Programas V2")
