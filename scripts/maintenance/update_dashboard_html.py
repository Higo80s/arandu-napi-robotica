# Script para adicionar Hero Section e Quick Actions ao dashboard.html

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

hero_section = '''<!-- HERO SECTION - Landing Page -->
<div class="hero-section">
    <div class="hero-content">
        <h1 class="hero-title fade-in-up">Sistema de Gestão de Editais</h1>
        <p class="hero-subtitle fade-in-up delay-1">
            UTFPR - Controle Inteligente de Bolsas e Programas de Pós-Graduação
        </p>
        
        <div class="hero-stats fade-in-up delay-2">
            <div class="hero-stat-card">
                <span class="stat-icon">📚</span>
                <div class="stat-number" data-target="{{ total_programas or 0 }}">0</div>
                <div class="stat-label">Programas</div>
            </div>
            <div class="hero-stat-card">
                <span class="stat-icon">👨‍🎓</span>
                <div class="stat-number" data-target="{{ total_discentes or 0 }}">0</div>
                <div class="stat-label">Discentes</div>
            </div>
            <div class="hero-stat-card">
                <span class="stat-icon">🏛️</span>
                <div class="stat-number" data-target="{{ total_campi or 0 }}">0</div>
                <div class="stat-label">Campi</div>
            </div>
        </div>
    </div>
</div>

<!-- QUICK ACTIONS -->
<section class="quick-actions fade-in-up delay-3">
    <h2>Acesso Rápido</h2>
    <div class="action-grid">
        <a href="{{ url_for('bolsistas_index') }}" class="action-card">
            <div class="card-icon">👨‍🎓</div>
            <h3>Discentes</h3>
            <p>Gerenciar bolsistas</p>
            <span class="card-badge">{{ total_discentes or 0 }} ativos</span>
        </a>
        
        <a href="{{ url_for('editais_index') }}" class="action-card">
            <div class="card-icon">📋</div>
            <h3>Editais</h3>
            <p>Controle de editais</p>
            <span class="card-badge">{{ total_editais or 0 }} vigentes</span>
        </a>
        
        <a href="{{ url_for('posdoc_index') }}" class="action-card">
            <div class="card-icon">🔬</div>
            <h3>Pós-Doc</h3>
            <p>Residentes e PDJ</p>
            <span class="card-badge">{{ total_posdoc or 0 }} ativos</span>
        </a>
        
        <a href="{{ url_for('relatorios_index') }}" class="action-card">
            <div class="card-icon">📊</div>
            <h3>Relatórios</h3>
            <p>Exportar dados</p>
            <span class="card-badge">Excel, PDF</span>
        </a>
    </div>
</section>

<hr style="border: 0; border-top: 1px solid var(--border-color); margin: 30px 0;">

'''

# Inserir após {% block content %}
if 'hero-section' not in content:
    content = content.replace(
        '{% block content %}',
        '{% block content %}\n' + hero_section
    )
    print('✓ Hero Section e Quick Actions adicionados')
    
    with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print('✅ dashboard.html atualizado!')
else:
    print('⚠️ Hero section já existe')
