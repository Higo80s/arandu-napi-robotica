# CURSO TÉCNICO: TECNOLOGIAS DO SISTEMA GESTÃO DE EDITAIS

**Professor:** Assistente IA (Equipe de Desenvolvimento)
**Público Alvo:** Desenvolvedores e Estudantes de TI
**Objetivo:** Ensinar os fundamentos e a aplicação prática das tecnologias que compõem o sistema.

---

## CAPÍTULO 1: PYTHON (O ALICERCE)

### 1.1 Apresentação
Python é uma linguagem de programação de alto nível, interpretada e conhecida por sua legibilidade e vasta biblioteca padrão. É a base de todo o "backend" do nosso sistema.

### 1.2 Principais Aspectos
*   **Sintaxe Limpa:** Usa indentação para definir blocos, forçando código organizado.
*   **Tipagem Dinâmica:** Não precisa declarar tipos de variáveis explicitamente.
*   **Multiparadigma:** Suporta orientação a objetos, funcional e imperativa.

### 1.3 Exemplo Geral
```python
def calcular_area(raio):
    pi = 3.14159
    return pi * (raio ** 2)

print(f"Área: {calcular_area(5)}")
```

### 1.4 Aplicação no Sistema (Mão na Massa)
No arquivo `app.py`, usamos Python para controlar toda a lógica. Veja como importamos bibliotecas e definimos funções:

```python
# app.py
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Uso prático: Calcular data final da bolsa
def calcular_fim(inicio, meses):
    return inicio + relativedelta(months=meses)
```

---

## CAPÍTULO 2: FLASK (O MOTOR WEB)

### 2.1 Apresentação
Flask é um "micro-framework" web para Python. Ele é leve e flexível, fornecendo apenas o essencial para colocar um site no ar, permitindo ao desenvolvedor escolher as demais ferramentas.

### 2.2 Principais Aspectos
*   **Roteamento (Routes):** Mapeia URLs (ex: `/bolsistas`) para funções Python.
*   **Decorators:** Usa `@app.route` para "decorar" funções.
*   **Contexto de Aplicação:** Gerencia requisições e sessões de forma isolada.

### 2.3 Exemplo Geral
```python
from flask import Flask
app = Flask(__name__)

@app.route("/")
def ola():
    return "Olá, Mundo!"
```

### 2.4 Aplicação no Sistema
No `Gestão de Editais`, o Flask orquestra tudo. Veja como uma rota recebe dados e chama o HTML:

```python
# app.py (Simplificado)
@app.route('/editais')
def editais_index():
    # 1. Busca dados no banco
    lista = Edital.query.all()
    # 2. Envia para o template HTML
    return render_template('editais/index.html', editais=lista)
```

---

## CAPÍTULO 3: SQLALCHEMY (OS DADOS)

### 3.1 Apresentação
SQLAlchemy é um ORM (Object Relational Mapper). Ele permite manipular o banco de dados usando classes e objetos Python, sem precisar escrever SQL puro (como `SELECT * FROM`).

### 3.2 Principais Aspectos
*   **Modelagem:** Tabelas viram Classes. Colunas viram Atributos.
*   **Sessão:** Gerencia transações (Commit/Rollback).
*   **Relacionamentos:** Define ligações (1:N, N:N) de forma pythônica.

### 3.3 Exemplo Geral
```python
# Definindo uma tabela
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50))

# Inserindo dados
novo = Usuario(nome="Maria")
db.session.add(novo)
db.session.commit()
```

### 3.4 Aplicação no Sistema
Em `models.py`, definimos a estrutura dos dados. Em `app.py`, fazemos consultas complexas de forma simples:

```python
# models.py
class Bolsista(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    edital_id = db.Column(db.Integer, db.ForeignKey('edital.id'))

# app.py (Consulta com Filtro)
# "Me dê todos os bolsistas ativos do edital 5"
ativos = Bolsista.query.filter_by(ativo=True, edital_id=5).all()
```

---

## CAPÍTULO 4: HTML5 & JINJA2 (A VISÃO)

### 4.1 Apresentação
HTML5 estrutura o conteúdo. Jinja2 é o motor de templates do Flask que permite misturar Python dentro do HTML para exibir dados dinâmicos.

### 4.2 Principais Aspectos
*   **Herança de Template:** `{% extends 'base.html' %}` evita repetir cabeçalhos/rodapés.
*   **Laços de Repetição:** `{% for item in lista %}` cria tabelas dinâmicas.
*   **Filtros:** `{{ valor | Dolar }}` formata dados na tela.

### 4.3 Exemplo Geral (Jinja2)
```html
<ul>
{% for usuario in usuarios %}
    <li>{{ usuario.nome }}</li>
{% endfor %}
</ul>
```

### 4.4 Aplicação no Sistema
Em `templates/bolsistas/index.html`, usamos Jinja para listar os bolsistas cadastrados:

```html
<!-- Tabela Zebrada -->
<tbody>
    {% for bolsista in bolsistas %}
    <tr>
        <td>{{ bolsista.nome }}</td>
        <td>{{ bolsista.modalidade.nivel }}</td> <!-- Acesso ao relacionamento -->
        <td>
            <a href="{{ url_for('bolsistas_editar', id=bolsista.id) }}">Editar</a>
        </td>
    </tr>
    {% endfor %}
</tbody>
```

---

## CAPÍTULO 5: CSS3 (O ESTILO)

### 5.1 Apresentação
CSS3 dá vida e beleza ao HTML. No nosso sistema, utilizamos recursos modernos para criar temas e layouts responsivos.

### 5.2 Principais Aspectos
*   **Flexbox:** Para alinhar botões e cards (cards de estatística).
*   **CSS Variables:** Para temas (Claro/Escuro/UTFPR).
*   **Responsividade:** O site se adapta a telas menores.

### 5.3 Exemplo Geral (Variáveis)
```css
:root {
    --primary-color: #007bff;
}
button {
    background-color: var(--primary-color);
}
```

### 5.4 Aplicação no Sistema
Em `static/css/styles.css`, definimos as cores globais que mudam conforme o tema selecionado no rodapé:

```css
/* Definição do Tema Padrão */
:root {
    --bg-color: #f8f9fa;
    --card-bg: #ffffff;
    --text-color: #333333;
}

/* Tema Escuro (ativado via JS) */
[data-theme="dark"] {
    --bg-color: #121212;
    --card-bg: #1e1e1e;
    --text-color: #e0e0e0;
}
```

---

## CAPÍTULO 6: JAVASCRIPT (A INTERATIVIDADE)

### 6.1 Apresentação
JavaScript (Vanilla, sem frameworks pesados) roda no navegador do usuário. Ele é usado para tudo que acontece "sem recarregar a página".

### 6.2 Principais Aspectos
*   **DOM Manipulation:** Alterar textos e classes HTML dinamicamente.
*   **Event Listeners:** Reagir a cliques (`onclick`).
*   **Fetch API:** Buscar dados no servidor assincronamente (AJAX).

### 6.3 Exemplo Geral
```javascript
document.getElementById('botao').addEventListener('click', function() {
    alert('Botão Clicado!');
});
```

### 6.4 Aplicação no Sistema
No rodapé (`base.html`), usamos JS para trocar o tema instantaneamente:

```javascript
function setTheme(themeName) {
    // Salva no LocalStorage do navegador
    localStorage.setItem('theme', themeName);
    // Aplica no HTML
    document.documentElement.setAttribute('data-theme', themeName);
}
```

---

## CONCLUSÃO

Este sistema é um exemplo clássico de arquitetura "Full Stack" com Python. Dominando estas tecnologias (Python, Flask, SQL, HTML/CSS/JS), você tem total controle para criar, manter e evoluir o **Gestão de Editais**.

*Bons estudos!*
