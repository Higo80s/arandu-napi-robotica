# Roteiro de Preparação: Reunião com TI (Universidade)
**Data:** 14/02/2026
**Objetivo:** Aprovação Técnica para Homologação/Produção Institucional

---

## 1. Introdução (O "Elevator Pitch")
*Seja direto. A TI quer saber se o sistema resolve um problema real e se não vai dar dor de cabeça para eles.*

*   **O que é**: "É um sistema web para gestão financeira e operacional de editais de fomento e bolsas acadêmicas."
*   **O que resolve**: "Elimina o controle via planilhas descentralizadas, evita pagamentos indevidos (controle automático de vigência) e gera relatórios de transparência para auditoria."
*   **Estado Atual**: "O sistema está maduro (v11.4), validado com dados reais de 2025/2026 e pronto para implantação via Docker."

---

## 2. Arquitetura Técnica (Tech Stack)
*Mostre que você tomou decisões de engenharia, não apenas 'fez funcionar'.*

*   **Linguagem**: Python 3.11 (Moderna, segura, padrão de mercado para Data Science/Web).
*   **Framework**: Flask (Microframework leve, fácil de auditar, sem "mágica" excessiva).
*   **ORM (Camada de Dados)**: SQLAlchemy.
    *   *Por que é importante?*: "O uso do SQLAlchemy abstrai o banco de dados. Hoje rodamos em SQLite para desenvolvimento, mas o sistema já está configurado para **PostgreSQL** ou **Oracle** em produção apenas mudando uma variável de ambiente."
*   **Frontend**: HTML5 Semântico + CSS (Bootstrap/Custom) + JS Vanilla. (Server-Side Rendering para leveza e compatibilidade).

---

## 3. Infraestrutura & Deploy (O "Pulo do Gato")
*Aqui é onde você ganha o SysAdmin. Entregue a solução pronta.*

*   **Containerização**: "O sistema é entregue 100% Dockerizado."
    *   `Dockerfile`: Baseado em imagem oficial `python:3.11-slim` (segura e pequena).
    *   `docker-compose.yml`: Orquestra a aplicação (`web`) e o banco (`db`).
*   **Variáveis de Ambiente**: "Nenhuma senha fica no código (`Hardcoded`). Tudo é injetado via `ENV VARS` (DATABASE_URL, SECRET_KEY), compatível com Kubernetes ou Docker Swarm."
*   **Migrações**: "Possuímos scripts de inicialização (`init_db.py`) que criam o schema automaticamente se o banco estiver vazio."

---

## 4. Integração Institucional (O Diferencial)
*Mencione o estudo que fizemos. Isso mostra visão de longo prazo.*

*   **Compatibilidade Oracle**: "Sabemos que a universidade usa Oracle. O sistema já está preparado para conectar via driver `oracledb`."
*   **Prevenção de Erros (Anti-Fraude)**: "Projetamos um cenário de integração onde o sistema consulta a data de defesa do aluno no sistema acadêmico. Se o aluno defendeu, o sistema bloqueia o pagamento da bolsa automaticamente. Isso evitaria X% de processos de devolução de valores."

---

## 5. FAQ - Perguntas Prováveis & Respostas Sugeridas

**Q: "Por que não fizermos isso no sistema ERP oficial da universidade?"**
**A:** "Seria o ideal, mas a fila de demandas da TI é longa. Esta solução é um **satélite especializado** que resolve a dor imediata do departamento com agilidade, podendo ser integrado ou absorvido pelo ERP no futuro via API."

**Q: "Quem vai dar manutenção nesse código?"**
**A:** "O código segue a PEP-8 (guia de estilo Python), é modular (MVC) e está documentado (`docs/`). A curva de aprendizado para qualquer dev Python é baixíssima. Além disso, a estabilidade é garantida por testes de validação automatizados."

**Q: "Como é o backup?"**
**A:** "Como rodamos em container, o backup é padrão de banco de dados (`pg_dump`). O sistema não guarda arquivos locais críticos (stateless), exceto os gerados temporariamente."

**Q: "E a segurança?"**
**A:** "Usamos Gunicorn como servidor de aplicação (WSGI) atrás de um Proxy reverso (padrão de mercado). O framework proteje contra SQL Injection (via ORM) e XSS (via Jinja2 auto-escape)."

---

## 6. Check-List para a Reunião
Tenha em mãos (ou na tela) para mostrar se pedirem:
1.  [ ] O diagrama do banco de dados (pode abrir o `models.py` ou o PDF de estudo).
2.  [ ] O arquivo `Dockerfile` (mostra profissionalismo).
3.  [ ] O documento `ESTUDO_INTEGRACAO_ORACLE.md` (mostra que você estudou o ambiente deles).
4.  [ ] A demonstração rodando no seu PC ("Olha a velocidade de gerar um relatório").

---
**Dica Final:** Fale a língua deles. Use termos como "Container", "ORM", "Environment Variables", "Stateless". Isso gera confiança de que você não é um amador, mas um parceiro técnico.
