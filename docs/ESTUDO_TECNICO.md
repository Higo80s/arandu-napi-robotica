# Estudo Técnico: Gestão de Editais (Versão 5.0)

Este documento apresenta uma análise abrangente das tecnologias, arquitetura, padrões de projeto e boas práticas adotados no desenvolvimento do sistema **Gestão de Editais**.

---

## 1. Visão Geral da Arquitetura
O sistema segue uma arquitetura **Monolítica Modular** baseada no padrão **MVC (Model-View-Controller)** adaptado para Flask.

*   **Model (Modelo):** Definido em `models.py` (SQLAlchemy). Representa a estrutura de dados e regras de negócio do banco.
*   **View (Visão):** Definida em `templates/` (Jinja2) e `static/` (CSS/JS). Responsável pela interface com o usuário.
*   **Controller (Controlador):** Definido em `app.py`. Gerencia rotas, recebe requisições, processa dados e retorna as views.

### Por que essa escolha?
Para aplicações de médio porte com requisitos de validação complexos (como a gestão de bolsas), o monolito simplifica o deploy, o compartilhamento de estado e a manutenção do banco de dados relacional.

---

## 2. Stack Tecnológico

### Backend (Servidor e Lógica)
*   **Linguagem:** Python 3.x (Foco na legibilidade e agilidade).
*   **Framework Web:** **Flask**. Um micro-framework que oferece flexibilidade. Não impõe estruturas rígidas, permitindo que o sistema cresça organicamente.
*   **Servidor WSGI:**
    *   *Desenvolvimento:* Werkzeug (Server nativo do Flask).
    *   *Produção:* **Waitress**. Um servidor WSGI puro Python, robusto, seguro e multi-thread (suporta múltiplas requisições simultâneas), ideal para Windows.

### Database (Banco de Dados)
*   **SGBD:** **SQLite**. Armazena todo o banco em um único arquivo (`.db`).
    *   *Vantagem:* Zero configuração, portabilidade total (basta copiar o arquivo), ideal para sistemas departamentais.
*   **ORM (Object Relational Mapper):** **SQLAlchemy**.
    *   *Função:* Abstrai comandos SQL puros. Permite manipular o banco usando classes Python (`Edital`, `Bolsista`).
    *   *Segurança:* Previne automaticamente injeção de SQL (SQL Injection).

### Frontend (Interface)
*   **Estrutura:** HTML5 Semântico com Templates **Jinja2** (permite lógica `if/for` dentro do HTML).
*   **Estilização:** CSS3 Puro com **CSS Variables** (`:root`).
    *   *Técnica de Temas:* Variáveis globais (`--primary-color`) permitem trocar o tema (Claro/Escuro) instantaneamente apenas alterando os valores na raiz via JavaScript.
*   **Interatividade:** JavaScript Vanilla (Sem frameworks pesados como React/Vue). Garante carregamento instantâneo e menor complexidade para manutenções simples.

---

## 3. Padrões e Técnicas Implementadas

### A. Normalização de Banco de Dados (Versão 5)
Foi realizada a transição do nível **1FN** para **3FN** (Terceira Forma Normal) em entidades críticas.
*   **Antes (V4):** O Campus e Programa do aluno eram textos soltos (`string`). Isso gerava duplicatas ("Curitiba" vs "Curitiba - Sede") e erros de digitação.
*   **Agora (V5):**
    *   Tabela `Campus`: Lista única e oficial dos 13 campi.
    *   Tabela `ProgramaAcademico`: Vinculada a um Campus.
    *   Benefício: Integridade referencial. É impossível cadastrar um bolsista em um programa inexistente.

### B. Gestão de Configuração e Segurança (.env)
Adotamos o padrão **12-Factor App** para configurações.
*   Segredos (`SECRET_KEY`, Senhas de Banco) **NUNCA** ficam no código fonte (`app.py`).
*   Eles são movidos para um arquivo `.env` (que é ignorado pelo Git via `.gitignore`).
*   A biblioteca `python-dotenv` carrega essas variáveis em tempo de execução. Isso permite que desenvolvedores diferentes tenham configurações diferentes sem conflito.

### C. Importação Robusta (Defensive Programming)
No módulo de importação em massa (CAPES DS), aplicamos programação defensiva:
1.  **Sniffer de CSV:** O sistema "sente" o arquivo para descobrir se ele usa vírgulas, ponto-e-vírgula ou tabulação, evitando erros comuns de formato.
2.  **Encoding Fallback:** Tenta ler como UTF-8 (Padrão Web). Se falhar, tenta Latin-1 (Padrão Excel antigo).
3.  **Validação Graciosa:** Se um programa não existe no banco, o sistema não quebra (Crash). Ele cria o registro com o campo nulo e avisa o usuário (Log de Aviso), permitindo correção posterior manual.

---

## 4. Boas Práticas para Novos Desenvolvedores

1.  **Ambiente Virtual (.venv):** Sempre use `venv` para isolar as dependências do projeto. Nunca instale bibliotecas no Python global do Windows.
2.  **Migrations Manuais:** Como usamos SQLite sem Alembic (para simplicidade), alterações no banco exigem scripts de migração (ex: `migrate_v5.py`) que copiam os dados para uma nova estrutura segura.
3.  **Flash Messages:** Use `flash()` para retornar feedback visual ao usuário após ações (Sucesso, Erro, Aviso).
4.  **Versionamento:** O arquivo `requirements.txt` deve ser atualizado (`pip freeze`) sempre que uma nova biblioteca for adicionada.

---

*Documento gerado para a versão 5.0 - Dezembro/2025*
*Gestão de Editais - UTFPR*
