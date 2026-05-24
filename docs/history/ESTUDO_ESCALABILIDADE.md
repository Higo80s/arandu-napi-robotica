---
title: Estudo Técnico de Escalabilidade e Distribuição (V20)
author: Antigravity Assistant (Google Deepmind)
date: 2026-01-28
context: Evolução do sistema "Gestão de Editais" para ambiente multiusuário (10+ pessoas)
---

# 1. Introdução e Mudança de Paradigma

Atualmente, o sistema roda localmente (`http://127.0.0.1...`) com um banco de dados SQLite (arquivo `.db`). Para permitir acesso simultâneo de 10 pessoas, precisamos mudar a arquitetura.

Existem duas formas de "instalar em outros computadores":

### A. Modelo Desktop Distribuído (Não recomendado para Web Apps)
- **Como funciona:** Gera-se um `.exe` do sistema, instala-se em cada um dos 10 computadores. Todos se conectam a um banco de dados na nuvem via internet.
- **Problemas Críticos:** 
    - **Manutenção:** Se você corrigir um bug, terá que reinstalar o software em 10 computadores manualmente.
    - **Segurança:** As credenciais do banco de dados ficariam embutidas no código em cada máquina.
    - **Performance:** Interfaces Web rodando localmente conectando em bancos remotos tendem a ser mais lentas devido à latência de cada query.

### B. Modelo Servidor Web (Altamente Recomendado)
- **Como funciona:** O sistema é "instalado" apenas UMA vez em um servidor na nuvem (ex: PythonAnywhere ou Render).
- **Para o usuário:** Ele não instala nada. Ele apenas abre o navegador (Chrome/Edge) e acessa `https://sua-empresa.pythonanywhere.com`.
- **Vantagens:** Atualizações instantâneas para todos, segurança centralizada e performance otimizada.

> **Conclusão:** Para uma aplicação Flask, a opção B é o padrão de mercado. O estudo seguirá focando nesta arquitetura, pois resolve o problema de "instalação" transformando-o em "acesso via link".

---

# 2. Migração de Banco de Dados: Adeus SQLite

O SQLite é excelente para desenvolvimento, mas trava (erro `Database is locked`) quando 2 ou mais pessoas tentam salvar dados ao mesmo tempo.

## Comparativo: MySQL vs PostgreSQL

| Característica | MySQL / MariaDB | PostgreSQL (Recomendado) |
| :--- | :--- | :--- |
| **Concorrência** | Boa, mas bloqueios de tabela podem ocorrer em engines antigas (MyISAM). InnoDB é ok. | **Excelente**. Usa MVCC (Controle de Concorrência Multiversão), ideal para usuários simultâneos. |
| **Integridade** | Bom, mas historicamente mais permissivo com dados ruins. | **Rigoroso**. Garante consistência forte dos dados. Melhor suporte a JSON nativo. |
| **Comunidade Python** | Suporte bom (driver `pymysql`). | **Suporte Premium** (driver `psycopg2`). É o banco preferido da comunidade Django/Flask. |
| **Custo na Nuvem** | Disponível em quase todos os lugares. | Planos gratuitos (Free Tier) tendem a ser mais generosos (ex: Neon, Supabase, Render). |

### Decisão Técnica: PostgreSQL
**Motivo:** O PostgreSQL lida melhor com tipos complexos de dados e possui serviços de nuvem gratuitos modernos e robustos. A migração do SQLAlchemy de SQLite para Postgres é transparente (mudança apenas na string de conexão).

---

# 3. Hospedagem e Compartilhamento (Nuvem)

Para 10 usuários simultâneos com atualizações em tempo real, precisamos de um servidor de aplicação (onde fica o Python) e um servidor de banco de dados.

## Opções de Arquitetura "Custo-Benefício"

### Opção 1: Tudo no PythonAnywhere (Opção "Mais Fácil")
- **Plano:** Hacker ($5/mês - aprox. R$ 30,00). *O plano gratuito deles não permite conexões externas ou domínios customizados decentes para DB externo com facilidade.*
- **Banco:** MySQL incluso no preço.
- **Vantagem:** Muito fácil de configurar. Ambiente estável.
- **Desvantagem:** Tecnologia um pouco antiga, interface menos moderna.

### Opção 2: Render.com + Neon.tech (Opção "Moderna e Gratuita/Barata")
- **Aplicação (Render):** Plano Free (hiberna após inatividade) ou Plano Starter ($7/mês) para ficar sempre ligado.
- **Banco (Neon.tech):** PostgreSQL Serverless **Gratuito** (limitado a 500MB de armazenamento, o que é muito texto).
- **Vantagem:** Stack moderna (Postgres), Deploy automático via GitHub (você dá push no git, o site atualiza sozinho).
- **Desvantagem:** O plano Free do Render "dorme" e demora 1 minuto para acordar no primeiro acesso.

### Opção 3: Railway (Opção "Equilibrada")
- **Tudo em um:** Hospeda o Flask e o PostgreSQL no mesmo painel.
- **Custo:** Modelo pré-pago (paga o que usa). Para 10 usuários leves, pode custar cerca de $5 a $8 dólares.
- **Vantagem:** Interface incrível, setup extremamente simples.

> **Recomendação:** Começar com **Render (App) + Neon (DB)** para teste custo zero, ou **PythonAnywhere ($5)** para estabilidade imediata sem complexidade de DevOps.

---

# 4. Segurança e Gestão de Acessos (O Novo Módulo ADMIN)

Ao colocar o sistema na internet, a segurança passa a ser a prioridade número 1.

## A. Sistema de Login (Authentication)
Não podemos mais ter acesso direto. Precisaremos implementar:
1.  **Tabela `Usuarios`:** Campos `id, email, senha_hash, nome, funcao, ativo`.
2.  **Hashing de Senha:** NUNCA salvar senhas em texto puro. Usar `werkzeug.security.generate_password_hash`.
3.  **Flask-Login:** Biblioteca padrão para gerenciar sessões (lembrar usuário logado).

## B. Níveis de Acesso (Authorization)
Definir hierarquia na tabela de usuários (Coluna `role` ou `perfil`):
1.  **Admin:** Acesso total (Criar usuários, Configurar Editais, Ver Auditoria).
2.  **Gestor:** Gerenciar bolsistas e seleção.
3.  **Visualizador:** Apenas relatórios (Dashboard).

## C. Funcionalidade de "Administrador do Sistema"
O sistema precisará de uma nova tela: **Painel de Controle de Acesso**.
- **Quem acessa:** Apenas usuários com perfil `Admin`.
- **O que faz:**
    - "Cadastrar Novo Usuário" (Envia convite ou cria senha provisória).
    - "Resetar Senha" (Para quando alguém esquecer).
    - "Bloquear Acesso" (Ex: servidor saiu da PROPPG, clica em Bloquear e ele perde acesso na hora).

---

# 5. Roteiro de Implementação (Roadmap)

Para transformar o estudo em realidade, seguiremos estes passos nas próximas sessões:

### Fase 1: Preparação do Terreno (Local)
1.  Criar modelos `User` e `Role` no `models.py`.
2.  Implementar `Flask-Login` e telas de Login/Logout.
3.  Criar o primeiro usuário "Admin" via script (superusuário).
4.  Proteger as rotas existentes com `@login_required`.

### Fase 2: Migração do Banco
1.  Instalar PostgreSQL localmente para teste.
2.  Configurar URI do banco para Postgres.
3.  Executar migrações para recriar as tabelas no Postgres.
4.  Criar script de exportação (SQLite) -> importação (Postgres) para não perder dados.

### Fase 3: Deploy (Nuvem)
1.  Criar conta no Cloud Provider (ex: Render + Neon).
2.  Configurar variáveis de ambiente (Senhas não ficam no código!).
3.  Subir a aplicação e conectar o banco.
4.  Testar acesso concorrente (usuário A edita, usuário B vê).

### Fase Post-Mortem (Manutenção)
- Implementar logs de auditoria (Saber *QUEM* alterou *O QUE* e *QUANDO*).

---

### Tópicos Transversais Essenciais

1.  **Variáveis de Ambiente (.env):** O segredo para segurança. Suas senhas de banco, chaves secretas do Flask, tudo sai do código (`app.py`) e vai para um arquivo `.env` que não é compartilhado, ou configurado no painel da nuvem.
2.  **Concorrência (Locking Otimista):** O que acontece se duas pessoas abrirem o mesmo bolsista e clicarem em "Salvar" ao mesmo tempo?
    - *Solução:* Adicionar campo `version` no registro. Se a versão no banco for maior que a versão que você editou, o sistema avisa: "Alguém editou este registro enquanto você lia. Atualize a página."
3.  **Backup Automatizado:** No SQLite fazíamos cópia do arquivo. No Postgres em nuvem, configuramos backups automáticos diários (serviços gerenciados como Neon/Render já oferecem isso, ou criamos um script agendado).
