import re

# Ler app.py
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Substituir a função index
old_pattern = r'@app\.route\(\'/\'\)\s+def index\(\):\s+return render_template\(\'dashboard\.html\'\)'

new_code = '''@app.route('/')
def index():
    """Landing Page com estatísticas gerais"""
    # Estatísticas para Hero Section  
    stats = {
        'total_programas': ProgramaAcademico.query.count(),
        'total_discentes': Bolsista.query.filter_by(ativo=True).count(),
        'total_campi': Campus.query.count(),
        'total_editais': Edital.query.filter(Edital.data_fim >= date.today()).count(),
        'total_posdoc': Residente.query.filter_by(ativo=True).count()
    }
    return render_template('dashboard.html', **stats)'''

content = re.sub(old_pattern, new_code, content, flags=re.DOTALL)

# Salvar
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✓ app.py atualizado com estatísticas para landing page')
