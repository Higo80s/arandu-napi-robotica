# Script para expandir Lucide Icons no base.html

with open('templates/base.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Mapeamento emoji → Lucide
replacements = {
    '📄': 'file-text',
    '⚠️': 'alert-circle',
    '🎓': 'graduation-cap',
    '🔬': 'microscope',
    '📉': 'trending-down',
    '📊': 'bar-chart',
    '❓': 'help-circle',
    '📘': 'book',
    '📙': 'file-code',
    '💾': 'database'
}

# Adicionar import do macro no início do body (se não existir)
if "{% from 'macros/icons.html' import icon %}" not in content:
    content = content.replace(
        '<body>',
        '<body>\n{% from \'macros/icons.html\' import icon %}'
    )
    print('✓ Import macro adicionado')

# Substituir emojis por Lucide
for emoji, lucide_name in replacements.items():
    # Padrão: <span class="icon">📄</span> Editais
    pattern = f'<span class="icon">{emoji}</span> '
    replacement = f'{{{{ icon(\'{lucide_name}\', size=20, class=\'mr-2\') }}}} '
    
    if pattern in content:
        content = content.replace(pattern, replacement)
        print(f'✓ {emoji} → {lucide_name}')

# Salvar
with open('templates/base.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ base.html atualizado com Lucide Icons!')
