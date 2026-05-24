# Sistema de Gestão de Editais e Bolsistas

Sistema web para gestão completa de editais e bolsistas de pesquisa em instituições de ensino superior.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-3.1-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🎯 Funcionalidades

- ✅ **Gestão de Editais** com múltiplas modalidades
- ✅ **Gestão de Bolsistas** (dados pessoais, acadêmicos e bancários)
- ✅ **Gestão de Residentes Pós-Doutorais** (com emissão de certificados)
- ✅ **Gestão Financeira PROAP/PROAPINHO** (Repasses, Distribuições e Dashboard)
- ✅ **Busca Avançada** (SEI, Formulário, Programas)
- ✅ **Filtro de Status** (Ativos/Inativos)
- ✅ **Acompanhamento Mensal** de parcelas e requisições
- ✅ **Relatórios Automáticos** em Excel e PDF
- ✅ **Dashboard Financeiro Integrado** com métricas em tempo real
- ✅ **Validações Inteligentes** e cálculo automático de datas

## 📊 Resultados

- **99% de redução** no tempo de geração de relatórios
- **100% de eliminação** de erros em cálculos
- **120+ horas economizadas** por ano
- **50+ bolsistas** gerenciados simultaneamente

## 🚀 Instalação Rápida

```bash
git clone https://github.com/Higo80s/gestao_editais.git
cd gestao_editais
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
python production.py
```

Acesse: http://127.0.0.1:5000

## 🚀 Novidades (Fevereiro 2026)
- **Migração para PostgreSQL**: Base de dados de produção migrada para PostgreSQL para maior robustez e suporte a concorrência.
- **Programas Profissionais**: Suporte nativo a Mestrados e Doutorados Profissionais com classificação correta.
- **Multicampi**: Suporte aprimorado para programas ofertados em múltiplos campi.
- **Relatórios Consolidados**: Novos painéis administrativos com estatísticas detalhadas.

## 🛠️ Tecnologias
- **Backend**: Python (Flask), SQLAlchemy
- **Banco de Dados**: PostgreSQL (Produção), SQLite (Dev)
- **Frontend**: HTML5, CSS3, JavaScript
- **Infraestrutura**: Docker Support

## 📦 Instalação
Verifique o arquivo `COMO_USAR.md` para instruções detalhadas.

## 📁 Estrutura

```
gestao_editais/
├── app.py              # Aplicação Flask
├── models.py           # Modelos do banco
├── reports.py          # Geração de relatórios
├── production.py       # Servidor produção
├── requirements.txt    # Dependências
├── static/            # CSS, JS
├── templates/         # HTML
├── tests/             # Testes
└── docs/              # Documentação
```

## 🤝 Contribuindo

1. Fork o projeto
2. Crie branch: `git checkout -b feature/nova-funcionalidade`
3. Commit: `git commit -m 'feat: adiciona X'`
4. Push: `git push origin feature/nova-funcionalidade`
5. Abra Pull Request

## 📝 Licença

MIT License - Veja [LICENSE](LICENSE)

## 👨‍💻 Autor

**Higo Santos**
- GitHub: [@Higo80s](https://github.com/Higo80s)

## 📞 Suporte

Issues: https://github.com/Higo80s/gestao_editais/issues

---

**Desenvolvido com ❤️ usando Python + Flask**
