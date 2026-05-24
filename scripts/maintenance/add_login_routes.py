# Script para adicionar rotas de login/logout ao app.py

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Rotas de autenticação para adicionar após a rota index()
login_routes = '''

# === AUTENTICAÇÃO ===
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Tela e lógica de login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # TEMPORÁRIO: Autenticação básica (substituir por banco de dados)
        # Usuario padrão: admin / senha: admin123
        if username == 'admin' and password == 'admin123':
            session['logged_in'] = True
            session['username'] = username
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Usuário ou senha incorretos')
    
    # Se já estiver logado, redireciona para dashboard
    if session.get('logged_in'):
        return redirect(url_for('index'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout do sistema"""
    session.clear()
    flash('Você saiu do sistema', 'info')
    return redirect(url_for('login'))

'''

# Inserir antes da rota /editais (primeira rota após index)
marker = "# === EDITAIS ==="
if marker in content and '/login' not in content:
    content = content.replace(marker, login_routes + marker)
    print('✓ Rotas de login/logout adicionadas')
else:
    print('⚠️ Rotas já existem ou marcador não encontrado')

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ app.py atualizado!')
