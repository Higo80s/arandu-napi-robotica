# Script para adicionar CDNs e inicialização de Lucide/Twemoji no base.html

with open('templates/base.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Adicionar Lucide CDN no <head> se não existir
if 'lucide' not in content:
    head_injection = '''    <!-- Lucide Icons CDN -->
    <script src="https://unpkg.com/lucide@latest"></script>
    
    <!-- Twemoji CDN -->
    <script src="https://cdn.jsdelivr.net/npm/@twemoji/api@latest/dist/twemoji.min.js" crossorigin="anonymous"></script>
    
'''
    content = content.replace('</head>', head_injection + '</head>')
    print('✓ CDNs Lucide + Twemoji adicionados')

# Adicionar inicialização antes de </body> se não existir
if 'lucide.createIcons()' not in content:
    init_script = '''    
    <script>
        // Initialize Lucide Icons
        lucide.createIcons();
        
        // Parse Twemoji
        twemoji.parse(document.body, {
            folder: 'svg',
            ext: '.svg'
        });
    </script>
'''
    content = content.replace('</body>', init_script + '\n</body>')
    print('✓ Scripts de inicialização adicionados')

# Salvar
with open('templates/base.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ CDNs e inicialização configurados!')
