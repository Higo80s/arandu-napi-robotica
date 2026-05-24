# Script para atualizar Quick Actions com Lucide Icons

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Substituir ícones nos quick actions
quickactions_replacements = {
    '<div class="card-icon">👨‍🎓</div>': '{{ icon(\'users\', size=48, class=\'card-icon-lucide\') }}',
    '<div class="card-icon">📋</div>': '{{ icon(\'clipboard-list\', size=48, class=\'card-icon-lucide\') }}',
    '<div class="card-icon">🔬</div>': '{{ icon(\'flask\', size=48, class=\'card-icon-lucide\') }}',
    '<div class="card-icon">📊</div>': '{{ icon(\'file-bar-chart\', size=48, class=\'card-icon-lucide\') }}'
}

for old, new in quickactions_replacements.items():
    if old in content:
        content = content.replace(old, new)
        print(f'✓ Quick Action atualizado: {old[:30]}...')

# Substituir ícones no hero stats
herostats_replacements = {
    '<span class="stat-icon">📚</span>': '{{ icon(\'book-open\', size=48, color=\'white\', class=\'stat-icon-lucide\') }}',
    '<span class="stat-icon">👨‍🎓</span>': '{{ icon(\'users\', size=48, color=\'white\', class=\'stat-icon-lucide\') }}',
    '<span class="stat-icon">🏛️</span>': '{{ icon(\'building\', size=48, color=\'white\', class=\'stat-icon-lucide\') }}'
}

for old, new in herostats_replacements.items():
    if old in content:
        content = content.replace(old, new)
        print(f'✓ Hero Stat atualizado: {old[:30]}...')

# Salvar
with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ dashboard.html atualizado!')
