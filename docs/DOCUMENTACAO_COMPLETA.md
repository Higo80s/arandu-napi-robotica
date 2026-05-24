# Documentação - Sistema de Gestão de Editais (V6.2)

## 📚 Índice

1. [Instalação](#instalação)
2. [Uso Básico](#uso-básico)
3. [Deploy PythonAnywhere](#deploy-pythonanywhere)
4. [Solução de Problemas](#solução-de-problemas)
5. [Desenvolvimento](#desenvolvimento)

---

## 📦 Instalação

### Requisitos
- Python 3.11+
- Git

### Passos

```bash
# Clonar repositório
git clone https://github.com/Higo80s/gestao_editais.git
cd gestao_editais

# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente (Windows)
.venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
python production.py
```

Acesse: http://127.0.0.1:5000

---

## 🎯 Uso Básico

### Dashboard
Visualize métricas consolidadas: editais ativos, bolsistas ativos e investimento mensal total.

### Gestão de Editais

**Criar Edital:**
1. Menu "Editais" → "Novo Edital"
2. Preencher: número, agência, código projeto, processo SEI
3. Salvar

**Adicionar Modalidades:**
1. Editar edital
2. Clicar "Gerenciar Modalidades"
3. Adicionar: nível (Mestrado/Doutorado), vagas, valor mensal, duração máxima
4. Editar ou excluir modalidades conforme necessário

### Gestão de Bolsistas

**Cadastrar Bolsista:**
1. Menu "Bolsistas" → "Novo Bolsista"
2. Selecionar edital (modalidades carregam automaticamente)
3. Preencher dados:
   - Pessoais: nome, CPF, email
   - Acadêmicos: orientador, campus, programa, datas
   - Bancários: banco, agência, conta
   - Bolsa: datas (cálculo automático de fim)
4. Salvar

**Dicas:**
- Data fim é calculada automaticamente
- Sistema valida duração vs limite da modalidade
- CPF deve ser único
- **Pós-Doutorado:** Módulo exclusivo (veja seção abaixo).

### Gestão de Pós-Doutorado e Residência (Novo V7.0)
Arquitetura dedicada para Pesquisadores de Pós-Doutorado, separada dos discentes.

**Principais Recursos:**
1.  **Menu "Pós-Doutorado":** Acesso direto na barra lateral.
2.  **Cadastro Específico:**
    *   *Supervisor*: Docente responsável.
    *   *Projeto de Pesquisa*: Título e detalhes.
    *   *Fomento*: Agência financiadora (ex: Fundação Araucária).
3.  **Importação:** Ferramenta dedicada para planilhas de Pós-Doc.
4.  **Certificados:** Geração de declarações com terminologia correta ("Supervisor", "Residência").


### 3.4 Geração de Certificados (Novo V6.2)
Permite gerar declarações de vigência automaticamente.

1.  **Acesse a lista de Bolsistas.**
2.  **Clique no botão "📜 Gerar Certificados".**
3.  **Selecione o Bolsista:** Use a barra de busca para encontrar o nome.
4.  **Clique em "Gerar Texto":** O sistema preenche o modelo padrão.
    *   *Nota:* O texto adapta-se automaticamente para "Bolsistas" ou "Pós-Doutorandos" conforme a modalidade.
5.  **Copie:** Botão "Copiar" transfere para a área de transferência.

### Relatórios & Alertas (Novo V11.4)

**Relatório de Ações Pendentes:**
Acesse o novo menu **"⚠️ Ações Pendentes"** na barra lateral. O sistema alerta automaticamente sobre:
1.  **Editais Terminando:** Vigência encerrando nos próximos 30 dias.
2.  **Prestação de Contas:** Editais vencidos sem registro de prestação de contas.
3.  **Bolsas Ativas Vencendo:** Bolsistas cuja vigência termina no mês atual.

**Gerar Relatório Mensal:**
1. Menu "Relatórios"
2. Selecionar mês (formato YYYY-MM)
3. Escolher formato (Excel ou PDF)
4. Download automático

**Conteúdo do Relatório:**
- Lista de bolsistas ativos
- Dados bancários
- Valores mensais
- Parcelas e requisições
- **Totalizador Financeiro** por modalidade.

---

## 🌐 Deploy PythonAnywhere

### Guia Rápido (10 minutos)

**1. Criar conta:** https://www.pythonanywhere.com (plano gratuito)

**2. Console Bash:**
```bash
cd ~
git clone https://github.com/Higo80s/gestao_editais.git
cd gestao_editais
mkvirtualenv --python=/usr/bin/python3.10 gestao-editais
pip install -r requirements.txt
```

**3. Web App:**
- Aba "Web" → "Add a new web app"
- Manual configuration → Python 3.10

**4. WSGI (substituir conteúdo):**
```python
import sys, os
project_home = '/home/SEU_USERNAME/gestao_editais'
sys.path.insert(0, project_home)
os.environ['FLASK_ENV'] = 'production'
from app import app as application
with application.app_context():
    from models import db
    db.create_all()
```

**5. Virtualenv:** `/home/SEU_USERNAME/.virtualenvs/gestao-editais`

**6. Static files:** 
- URL: `/static/`
- Directory: `/home/SEU_USERNAME/gestao_editais/static/`

**7. Reload** e acesse: `https://SEU_USERNAME.pythonanywhere.com`

### Atualizar Aplicação
```bash
cd ~/gestao_editais
git pull origin main
workon gestao-editais
pip install -r requirements.txt
```
Depois: clicar "Reload" na aba Web

---

## 🐛 Solução de Problemas

### Erro 500 - Internal Server Error

**Causa:** Erro no código ou configuração WSGI incorreta

**Solução:**
```bash
# Ver logs (PythonAnywhere)
cat /var/log/SEU_USERNAME.pythonanywhere.com.error.log

# Verificar WSGI
# Confirme que project_home está correto
# Verifique importações
```

### Erro: "no such column"

**Causa:** Banco de dados desatualizado

**Solução:**
```bash
python migrate_v2.py
```

### CSS não carrega

**Solução:**
1. Verificar seção "Static files" no PythonAnywhere
2. Confirmar path correto
3. Fazer Reload

### Console fica visível (Windows)

**Solução:** Use `Gestao_Editais.bat` em vez de executar `app.py` diretamente

### Banco de dados corrompido

**Solução:**
```bash
# Backup primeiro!
# Depois deletar banco e recriar
rm instance/gestao_editais_new.db
python production.py  # Recria automaticamente
```

---

## 💻 Desenvolvimento

### Estrutura do Projeto

```
gestao_editais/
├── app.py              # Aplicação Flask
├── models.py           # Modelos SQLAlchemy
├── reports.py          # Geração de relatórios
├── production.py       # Servidor produção
├── wsgi.py            # Config WSGI
├── requirements.txt    # Dependências
├── static/            # CSS, JS
├── templates/         # HTML
├── instance/          # Banco de dados
└── docs/              # Documentação
```

### Adicionar Nova Feature

1. **Model:** Adicionar em `models.py`
```python
class NovaTabela(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # campos...
```

2. **Rota:** Adicionar em `app.py`
```python
@app.route('/nova-rota')
def nova_rota():
    return render_template('nova_rota.html')
```

3. **Template:** Criar em `templates/`
```html
{% extends "base.html" %}
{% block content %}
<!-- conteúdo -->
{% endblock %}
```

4. **Migração:** Se alterou modelos
```bash
# Criar script de migração
python migrate_vX.py
```

### Executar em Modo Debug

```bash
# Em app.py, alterar:
app.run(debug=True)

# Executar
python app.py
```

### Testes

```bash
# Executar testes (se implementados)
pytest tests/
```

### Boas Práticas

- ✅ Fazer backup do banco antes de migrations
- ✅ Testar em desenvolvimento antes de produção
- ✅ Usar o virtualenv sempre
- ✅ Commitar mudanças com mensagens descritivas
- ✅ Reload após mudanças no PythonAnywhere

---

## 📊 Informações Técnicas

### Stack Tecnológico
- **Backend:** Python 3.11, Flask 3.0, SQLAlchemy 3.1
- **Database:** SQLite (dev/local), PostgreSQL (produção cloud)
- **Frontend:** Jinja2, Vanilla CSS/JS
- **Relatórios:** OpenPyXL (Excel), ReportLab (PDF)
- **Servidor:** Waitress WSGI

### Performance
- Tempo de resposta: < 2s
- Suporta até 50 usuários simultâneos (SQLite)
- Relatórios: 30s para Excel, 25s para PDF

### Segurança
- Secret key aleatória
- Dados sensíveis apenas local
- HTTPS no PythonAnywhere (automático)

---

## 🤝 Contribuindo

1. Fork o projeto
2. Crie branch: `git checkout -b feature/nova-funcionalidade`
3. Commit: `git commit -m 'feat: adiciona funcionalidade X'`
4. Push: `git push origin feature/nova-funcionalidade`
5. Abra Pull Request

---

## 📝 Licença

MIT License - Veja [LICENSE](../LICENSE)

---

## 📞 Suporte

- **Issues:** https://github.com/Higo80s/gestao_editais/issues
- **Docs Completas:** https://github.com/Higo80s/gestao_editais/tree/main/docs

---

**Desenvolvido com ❤️ usando Python + Flask**
