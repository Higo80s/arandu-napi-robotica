# FAQ Detalhado: Segurança, Manutenção e Backup
**Documento de Apoio para Reunião com TI**

Este documento aprofunda as respostas para as "perguntas difíceis" que a equipe de TI costuma fazer. Utilize os termos técnicos em **negrito** para demonstrar domínio.

---

## 1. SEGURANÇA (Security)

**P: "O sistema é seguro? Como ele trata dados sensíveis e autenticação?"**

**Sua Resposta Técnica:**

1.  **Proteção contra SQL Injection**:
    *   "Nós utilizamos o **SQLAlchemy (ORM)** para todas as interações com o banco de dados. Ele parametriza automaticamente as queries, eliminando o risco de injeção de SQL via inputs do usuário."

2.  **Proteção contra XSS (Cross-Site Scripting)**:
    *   "O Frontend é renderizado pelo **Jinja2** (motor de templates do Flask), que possui *Auto-Escaping* ativado por padrão. Isso impede que scripts maliciosos inseridos em formulários sejam executados no navegador de outros usuários."

3.  **Segurança de Sessão e Cookies**:
    *   "As sessões são assinadas criptograficamente usando uma `SECRET_KEY` complexa (configurada via variável de ambiente, nunca hardcoded). Os cookies são configurados como `HttpOnly` para evitar roubo via JavaScript."
    *   *Nota: Se perguntarem sobre HTTPS, diga que isso deve ser configurado no Nginx/Load Balancer da universidade (SSL Termination).*

4.  **Autenticação**:
    *   "Atualmente o sistema possui login local, mas a arquitetura Flask permite integração fácil com **LDAP** ou **OAuth2** (Google/Microsoft) caso a universidade queira centralizar o acesso no futuro."

---

## 2. MANUTENÇÃO (Maintenance)

**P: "Quem vai manter esse código depois que você sair? É uma 'caixa preta'?"**

**Sua Resposta Técnica:**

1.  **Padrões de Código (Clean Code)**:
    *   "O projeto segue estritamente a **PEP-8** (guia de estilo oficial do Python). O código é organizado no padrão **MVC (Model-View-Controller)**, o que qualquer desenvolvedor web entende facilmente:
        *   `models.py`: Definição das tabelas.
        *   `app.py`: Rotas e lógica de controle.
        *   `templates/`: Telas em HTML."

2.  **Gerenciamento de Dependências**:
    *   "Não instalamos bibliotecas aleatórias. Todas as dependências (Flask, SQLAlchemy, Pandas) estão listadas no arquivo `requirements.txt` com versões fixadas (`pinned versions`), garantindo que o ambiente seja reprodutível em qualquer máquina."

3.  **Ambiente Isolado (Docker)**:
    *   "A maior dor de cabeça de manutenção é 'funciona na minha máquina mas não no servidor'. Com o **Docker**, eliminamos isso. Entregamos a imagem exata do sistema operacional e bibliotecas que o sistema precisa. Para atualizar, basta dar um `git pull` e `docker-compose up --build`."

---

## 3. BACKUP & RECUPERAÇÃO (Disaster Recovery)

**P: "E se o servidor queimar? Como recuperamos os dados?"**

**Sua Resposta Técnica:**

1.  **Dados Persistentes vs. Efêmeros (Stateless)**:
    *   "A aplicação em si é **Stateless** (não guarda dados nela mesma). Se o container da aplicação morrer, basta subir outro. O único ponto de estado é o **Banco de Dados**."

2.  **Backup de Banco de Dados**:
    *   "Estamos usando PostgreSQL. A estratégia de backup padrão é via utilitário **`pg_dump`**. Recomendo agendar uma tarefa (Cron Job) no servidor para rodar o `pg_dump` toda noite e enviar o arquivo `.sql` para um armazenamento externo (S3/Backup Server)."
    *   *Dica: Se eles perguntarem "Você já fez o script?", diga: "O comando é simples, mas a política de onde salvar (fita, nuvem, outro disco) depende da regra da universidade."*

3.  **Volumes Docker**:
    *   "Os dados do banco não ficam 'presos' dentro do container. Mapeamos um **Volume Docker** (`postgres_data`) para o sistema de arquivos do servidor. Isso garante que, mesmo se atualizarmos o Docker, os dados permanecem intactos no disco."

---

## Resumo (Cheat Sheet)

| Tópico | Palavras-Chave para Usar | O que NÃO dizer |
| :--- | :--- | :--- |
| **Segurança** | ORM, SQL Injection, Auto-Escaping, Environment Variables. | "Eu fiz um login simples na mão." |
| **Manutenção** | PEP-8, MVC, Requirements.txt, Docker. | "É só me ligar que eu arrumo." |
| **Backup** | pg_dump, Volumes Persistentes, Stateless. | "Eu copio a pasta do projeto num Pen Drive." |
