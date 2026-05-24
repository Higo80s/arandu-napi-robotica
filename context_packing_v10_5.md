# 🧠 Arandú v10.5 - Context Packing (Snapshot de Ouro)

Este documento representa a "Versão Estável da Verdade" do sistema Arandú v10, consolidando regras de negócio, estrutura de dados e inteligência técnica para garantir sincronia total e prevenir alucinações.

---

## 1. 📊 Módulos de Dados (Models & Relations)

A estrutura de dados é baseada em SQLAlchemy com relacionamentos otimizados para performance via `joinedload`.

### Entidades Centrais
- **Bolsista**: Entidade central. Vincula `Edital`, `Modalidade` e `ProgramaAcademico`. Possui campos criptografados para CPF.
- **Residente**: Modelo separado para Pós-Doutorado (autonomia de ciclo de vida).
- **Edital / Modalidade**: Estrutura de fomento com controle orçamentário e de vagas.
- **Campus / ProgramaAcademico**: Base normalizada para integridade dos dados da UTFPR.

### Otimizações de Consulta (`joinedload`)
Para evitar problemas de N+1, as consultas críticas utilizam carregamento antecipado:
```python
# Exemplo de consulta otimizada em app.py
ProgramAcademico.query.options(db.joinedload(ProgramaAcademico.campus)).all()
```

---

## 2. ⚙️ Core Logic & Hotfixes (v10.5)

### 🛡️ Hotfix CSRF Global
Implementação de proteção robusta contra ataques de falsificação de requisição, com tratamento diferenciado para AJAX e formulários.
```python
@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'error': 'CSRF Error', ...}), 401
    return render_template('errors/csrf_retry.html', ...), 400
```

### 📋 Padronização Global de Menus
Estrutura centralizada no `templates/base.html` utilizando herança do Jinja2 para consistência visual em todos os módulos.

---

## 3. 🧠 Inteligência de Parsing (`StrictoSensuParser`)

Motor de extração de dados otimizado para formulários da UTFPR.
- **Regex Robusta**: Ignora conteúdos entre parênteses para evitar quebras de linha acidentais.
- **Sanitização Integrada**: Limpeza automática de nomes, CPFs e formatação de datas (ISO).
- **Fallback**: Lógica de busca em linhas subsequentes caso o valor não esteja na mesma linha da label.

---

## 4. 🛠️ Infrastructure & Safety

### 📦 Requisitos de Produção
- **Server**: `waitress` para execução multithreaded.
- **DB**: Suporte Dual (PostgreSQL para Produção/Docker e SQLite para desenvolvimento).
- **Libs**: `Flask-SQLAlchemy`, `Flask-WTF` (CSRF), `Flask-Login`, `pandas` (relatórios).

### 🛡️ Backup & Rollback (v6.1)
- **Primary**: `pg_dump` para instâncias PostgreSQL.
- **Fallback**: Exportação JSON Otimizada (escrita por partes para economizar RAM).
- **Storage**: Rotação de 30 dias e cópia opcional para Cloud (Google Drive/OneDrive).

---

## ⚠️ 5. Dívida Técnica (Mapeada pela Yoko)

| Item | Descrição | Prioridade |
| --- | --- | --- |
| **Particionamento de Logs** | `logs_automacao` precisa de limpeza automática após 100k registros. | Média |
| **Cache de Programas** | Implementar `Flask-Caching` para a lista de programas (latência). | Baixa |
| **Vínculo GCUB** | Expansão dos campos de internacionalização para acordos específicos. | Alta |
| **Segurança** | Rotatividade obrigatória de chaves de criptografia em `encryption.py`. | Média |

---
**Objetivo:** Garantir a estabilidade para deploy imediato na UTFPR.
