# Script para adicionar rota sobre_simbolo

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Rota para página sobre o símbolo
simbolo_route = '''
@app.route('/sobre-simbolo')
def sobre_simbolo():
    """Página sobre o símbolo do sistema"""
    return render_template('sobre_simbolo.html')

'''

# Inserir após a rota de logout
marker = "@app.route('/logout')"
if marker in content and '/sobre-simbolo' not in content:
    # Encontrar o final da função logout
    logout_func_end = content.find('\n@app.route', content.find(marker) + 1)
    if logout_func_end != -1:
        content = content[:logout_func_end] + '\n' + simbolo_route + content[logout_func_end:]
        print('✓ Rota /sobre-simbolo adicionada')
    else:
        print('⚠️ Marcador não encontrado')
else:
    print('⚠️ Rota já existe ou marcador não encontrado')

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ app.py atualizado!')
