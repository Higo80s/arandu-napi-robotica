# 📑 Índice de Documentação Completa

Bem-vindo à documentação do **Gestão de Editais v3.0**!

## 🎯 Por Onde Começar?

### Sou usuário final
👉 Comece aqui: **[GUIA_RAPIDO.md](GUIA_RAPIDO.md)**
- Instruções passo-a-passo
- Tarefas comuns
- Atalhos de teclado

### Tenho uma dúvida / problema
👉 Consulte: **[FAQ.md](FAQ.md)**
- Perguntas frequentes
- Troubleshooting
- Dicas de segurança
- Roadmap futuro

### Preciso de detalhes técnicos
👉 Leia: **[DOCUMENTACAO.md](DOCUMENTACAO.md)**
- Arquitetura completa
- Estrutura do banco de dados
- API de funções
- Automação e agendamento
- Referências

### Vou contribuir com código
👉 Estude: **[DESENVOLVIMENTO.md](DESENVOLVIMENTO.md)**
- Estrutura do projeto
- Stack tecnológico
- Convenções de código
- Como adicionar funcionalidades
- Testes
- Git workflow

### Quero configurar Excel mensal
👉 Veja: **[GUIA_EXCEL_MENSAL.md](GUIA_EXCEL_MENSAL.md)**
- Exportação manual
- Automação (Task Scheduler)
- Estrutura do Excel
- Exemplos de customização

### Preciso do README geral
👉 Acesse: **[README.md](README.md)**
- Visão geral do projeto
- Instalação
- Funcionalidades principais
- Links para documentação

---

## 📂 Estrutura de Arquivos

```
gestao_editais/
│
├── 📄 Documentação (você está aqui)
│   ├── INDEX.md                    ← VOCÊ ESTÁ AQUI
│   ├── README.md                   ← Visão geral + Links
│   ├── DOCUMENTACAO.md             ← Guia técnico completo
│   ├── GUIA_RAPIDO.md              ← Quick start
│   ├── FAQ.md                      ← Perguntas frequentes
│   ├── DESENVOLVIMENTO.md          ← Para desenvolvedores
│   └── GUIA_EXCEL_MENSAL.md        ← Excel + automação
│
├── 🐍 Código Principal
│   ├── app.py                      ← UI Tkinter (1662 linhas)
│   ├── db.py                       ← Banco de dados (453 linhas)
│   ├── criar_banco.py              ← Schema inicial
│   ├── atualizar_banco_v2.py       ← Migração 1
│   └── atualizar_banco_v3.py       ← (futuro)
│
├── 🤖 Automação
│   ├── exportar_excel_mensal.py    ← Script para Task Scheduler
│   ├── criar_agendamento.ps1       ← Setup (PowerShell)
│   └── criar_agendamento.bat       ← Setup (Batch)
│
├── 💾 Dados
│   ├── gestao_editais.db           ← Banco SQLite (gerado)
│   └── acompanhamento_YYYY-MM.xlsx ← Exportações Excel
│
└── ⚙️ Ambiente
    ├── .venv/                      ← Virtual environment Python
    ├── requirements.txt            ← Dependências
    └── .gitignore
```

---

## 🔍 Guia por Tópico

### Instalação e Setup
- 📘 [DOCUMENTACAO.md § Guia de Instalação](DOCUMENTACAO.md#guia-de-instalação)
- ⚡ [GUIA_RAPIDO.md § Iniciar a Aplicação](GUIA_RAPIDO.md#iniciar-a-aplicação)

### Usando o Sistema
- ⚡ [GUIA_RAPIDO.md § Tarefas Comuns](GUIA_RAPIDO.md#tarefas-comuns)
- 📘 [DOCUMENTACAO.md § Guia de Uso](DOCUMENTACAO.md#guia-de-uso)
- ❓ [FAQ.md § Operacional](FAQ.md#operacional)

### Banco de Dados
- 📘 [DOCUMENTACAO.md § Estrutura do BD](DOCUMENTACAO.md#estrutura-do-banco-de-dados)
- 🛠️ [DESENVOLVIMENTO.md § Queries SQL](DESENVOLVIMENTO.md#como-fazer-query-sql-diretamente)

### Automação Excel
- 📊 [GUIA_EXCEL_MENSAL.md](GUIA_EXCEL_MENSAL.md) (documento completo)
- 📘 [DOCUMENTACAO.md § Automação](DOCUMENTACAO.md#automação-e-agendamento)
- ⚡ [GUIA_RAPIDO.md § Automação](GUIA_RAPIDO.md#automação-excel-mensal)

### Desenvolvendo
- 🛠️ [DESENVOLVIMENTO.md](DESENVOLVIMENTO.md) (documento completo)
- 📘 [DOCUMENTACAO.md § API de Funções](DOCUMENTACAO.md#api-de-funções)

### Troubleshooting
- ❓ [FAQ.md § Problemas Comuns](FAQ.md#problemas-comuns)
- 📘 [DOCUMENTACAO.md § Troubleshooting](DOCUMENTACAO.md#troubleshooting)

---

## 🚀 Fluxo de Uso Típico

```
NOVO USUÁRIO
    ↓
    └─→ Ler: GUIA_RAPIDO.md (5 min)
    ↓
    └─→ Executar: python app.py
    ↓
    └─→ Criar: Edital → Modalidades → Bolsistas → Acompanhamento
    ↓
    └─→ Exportar: Excel (botão na UI)
    ↓
    └─→ Dúvida? → Consultar: FAQ.md
```

```
ADMIN / SETUP INICIAL
    ↓
    └─→ Ler: GUIA_RAPIDO.md (conhecer sistema)
    ↓
    └─→ Ler: DOCUMENTACAO.md § Instalação
    ↓
    └─→ Instalar dependências: pip install -r requirements.txt
    ↓
    └─→ Criar DB: python criar_banco.py
    ↓
    └─→ Testar: python app.py
    ↓
    └─→ Automatizar: Executar criar_agendamento.ps1
    ↓
    └─→ Fim! Sistema pronto para produção
```

```
DESENVOLVEDOR / CONTRIBUIDOR
    ↓
    └─→ Ler: DESENVOLVIMENTO.md (estrutura completa)
    ↓
    └─→ Fork/Clone do GitHub
    ↓
    └─→ Setup local: .venv + pip install -r requirements.txt
    ↓
    └─→ Criar branch: git checkout -b feature/...
    ↓
    └─→ Modificar código: app.py, db.py, etc
    ↓
    └─→ Testar mudanças
    ↓
    └─→ Commit + Push + PR
    ↓
    └─→ Review → Merge
```

---

## 📞 Suporte

### Antes de contatar suporte, verifique:
1. ✅ Consultou [FAQ.md](FAQ.md)?
2. ✅ Leu a seção relevante em [DOCUMENTACAO.md](DOCUMENTACAO.md)?
3. ✅ Tentou as soluções em [DESENVOLVIMENTO.md § Troubleshooting](DESENVOLVIMENTO.md)?

### Informações a incluir no report:
- Versão do sistema: `Abra app.py e procure por "v3.0" ou verifique window title`
- Windows version: `Win+R → winver`
- Python version: `.venv\Scripts\python.exe --version`
- Erro completo (screenshot ou texto)
- Passos para reproduzir

---

## 📚 Referências Externas

### Python
- [Python 3.13 Documentation](https://docs.python.org/3/)
- [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)

### UI (Tkinter)
- [Official Tkinter Docs](https://docs.python.org/3/library/tkinter.html)
- [Real Python Tkinter Tutorial](https://realpython.com/python-gui-tkinter/)

### Banco de Dados (SQLite)
- [SQLite Official Docs](https://www.sqlite.org/docs.html)
- [SQLite Best Practices](https://www.sqlite.org/bestpractice.html)

### Excel (openpyxl)
- [openpyxl Documentation](https://openpyxl.readthedocs.io/)
- [Excel Formatting Guide](https://openpyxl.readthedocs.io/en/stable/styles.html)

### Automação (Windows)
- [Task Scheduler Documentation](https://docs.microsoft.com/en-us/windows/win32/taskschd/task-scheduler-start-page)
- [PowerShell Docs](https://docs.microsoft.com/en-us/powershell/)

---

## 🎓 Aprenda Conceitos

### Model-View-Controller (MVC)
Veja: [DESENVOLVIMENTO.md § Padrões Arquiteturais](DESENVOLVIMENTO.md#padrões-arquiteturais)

### Repository Pattern
Veja: [DESENVOLVIMENTO.md § CRUD Pattern](DESENVOLVIMENTO.md#crud-pattern-em-dbpy)

### Migrações de Banco
Veja: [DESENVOLVIMENTO.md § Como Adicionar Nova Funcionalidade](DESENVOLVIMENTO.md#como-adicionar-nova-funcionalidade)

### SQL Joins
Veja: [DESENVOLVIMENTO.md § Queries com JOIN](DESENVOLVIMENTO.md#queries-com-join)

---

## 📊 Estatísticas do Projeto

- **Linhas de código**: ~2.100+ (app.py + db.py)
- **Linhas de documentação**: ~2.500+ (este arquivo + outros .md)
- **Tabelas no BD**: 4 (editais, modalidades, bolsistas, acompanhamento)
- **Funções em db.py**: 30+
- **Versão Python**: 3.13
- **Dependências**: 3 (ttkthemes, python-dateutil, openpyxl)

---

## 📝 Changelog

### v3.0 (Dezembro 2025)
- ✨ Exportação Excel com formatação profissional
- 🤖 Automação via Windows Task Scheduler
- 📚 Documentação completa (5 arquivos .md)
- 🐛 Correções de encoding e performance

### v2.1 (Novembro 2025)
- 🐛 Bugs corrigidos em edição

### v2.0 (Outubro 2025)
- 🏗️ Refatoração para MVC + Repository Pattern
- 📦 Módulo db.py centralizado
- 📊 Novo sistema de acompanhamento

### v1.0 (Setembro 2025)
- 🎉 Lançamento inicial

---

## ✅ Qualidade

- ✅ Zero dependências externas não-essenciais
- ✅ Banco de dados local (sem servidor)
- ✅ Código testado manualmente
- ✅ Padrões de código seguidos (PEP 8)
- ✅ Documentação abrangente
- ✅ Preparado para produção

---

**Documentação v1.0 | Dezembro 2025 | Mantido por: Tim Couto**

💡 **Dica**: Adicione este arquivo como bookmark para referência rápida!
