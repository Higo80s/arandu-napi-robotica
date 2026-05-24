# Script para atualizar CSS do login com fundo Amazônia

css_amazonia = '''/* Fundo inspirado na Amazônia - tons escuros de verde */
body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: 
        /* Padrões sutis de folhagem */
        repeating-linear-gradient(45deg, transparent, transparent 40px, rgba(34, 139, 34, 0.02) 40px, rgba(34, 139, 34, 0.02) 80px),
        repeating-linear-gradient(-45deg, transparent, transparent 40px, rgba(46, 125, 50, 0.02) 40px, rgba(46, 125, 50, 0.02) 80px),
        /* Gradiente Amazônia: verde escuro a azul petróleo */
        linear-gradient(135deg, 
            #0d3b2e 0%,      /* Verde floresta profundo */
            #1a5c4a 25%,     /* Verde Amazônia */
            #1e4d3e 50%,     /* Verde musgo escuro */
            #1a3d3d 75%,     /* Azul-verde petróleo */
            #16423c 100%     /* Petróleo profundo */
        );
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1rem;
    position: relative;
    overflow: hidden;
}

/* Marca d'água do símbolo (cantos) */
body::before {
    content: '';
    position: fixed;
    top: -50px;
    left: -50px;
    width: 200px;
    height: 200px;
    background-image: url('/static/images/simbolo_marangatu.png');
    background-size: contain;
    background-repeat: no-repeat;
    opacity: 0.03;
    z-index: 0;
}

body::after {
    content: '';
    position: fixed;
    bottom: -50px;
    right: -50px;
    width: 200px;
    height: 200px;
    background-image: url('/static/images/simbolo_marangatu.png');
    background-size: contain;
    background-repeat: no-repeat;
    opacity: 0.03;
    z-index: 0;
    transform: rotate(180deg);
}
'''

# Ler o arquivo atual
with open('static/css/login.css', 'r', encoding='utf-8') as f:
    content = f.read()

# Procurar e substituir a seção body
import re
pattern = r'body \{[^}]+background:[^;]+linear-gradient\([^)]+\)[^}]+\}'
# Substituir toda a seção body até o final do primeiro }
start = content.find('body {')
if start != -1:
    # Encontrar o fechamento do body (considerando os pseudoelementos)
    first_brace = content.find('}', start)
    # Encontrar onde termina body::after
    after_end = content.find('}', content.rfind('body::after'))
    
    if first_brace != -1 and after_end != -1:
        # Substituir todo o bloco
        new_content = content[:start] + css_amazonia + '\n' + content[after_end+1:]
        
        with open('static/css/login.css', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print('✅ CSS atualizado com fundo Amazônia!')
    else:
        print('⚠️ Estrutura CSS não encontrada')
else:
    print('⚠️ body { não encontrado')
