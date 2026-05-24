# Arquitetura do Sistema: Histórico, Decisões e Roadmap

**Data:** Janeiro/2026
**Responsável Técnico:** Equipe de Desenvolvimento (Consultoria Especializada)
**Versão:** 6.2 (Stable)

---

## 1. Visão Geral da Arquitetura
O sistema "Gestão de Editais" opera sob uma **arquitetura monolítica modular** construída sobre o framework **Flask (Python 3.12)**. Esta escolha deliberada visa equilibrar facilidade de manutenção por equipes institucionais reduzidas (UTFPR) com robustez para processamento de dados financeiros sensíveis.

### Diagrama Conceitual (Textual)
- **Frontend:** Jinja2 (Serverside Rendering) + Vanilla JS + CSS (Tema Institucional UTFPR).
- **Backend:** Flask Core (Rotas e Controle) + SQLAlchemy (ORM).
- **Persistência:** SQLite (Dev/Homolog) -> PostgreSQL (Recomendado Prod).
- **Servidor de Aplicação:** Waitress (WSGI Prod-Ready).

---

## 2. Histórico Crítico e Decisões de Design (2018-2026)

### 2.1 A Escolha do Monolito (V1)
**Contexto:** Início do projeto com recursos escassos.
**Decisão:** Evitar microserviços.
**Impacto:** Permitiu implantação rápida em servidores locais modestos sem necessidade de orquestradores (Kubernetes).
**Governança:** Simplificou o backup (baseado em arquivos) e a auditoria de código, vital para instituições públicas.

### 2.2 A Crise de Migração V1 -> V2 (Jan/2026)
**Incidente "O Processo Zumbi":**
Durante a migração para a V2 (novos painéis administrativos), o sistema enfrentou instabilidade crítica (Erro 500).
- **Diagnóstico:** Um processo Flask órfão ("zumbi") na porta 5003 servia código antigo da memória RAM, ignorando atualizações de disco.
- **Ação Corretiva:** Implementação de `run_server_stable.py` com lógica *Self-Healing* (mata processos concorrentes antes do bind).
- **Lição Aprendida:** Em ambientes Windows Server sem containerização estrita, o gerenciamento de PID é responsabilidade da aplicação.

### 2.3 Refatoração do Frontend (V5)
**Mudança:** Abandono do Bootstrap pesado por CSS nativo otimizado + Lucide Icons.
**Impacto:** Redução de 40% no First Contentful Paint (FCP).
**Risco:** Manter compatibilidade com navegadores legados da instituição (Edge antigo).

---

## 3. Estado Atual e Desafios

### Robustez do Backend
O uso do SQLAlchemy previne quase 100% dos erros de SQL Injection, mas a dependência do SQLite em homologação cria gargalos de I/O em relatórios massivos (`/relatorios/consolidado`).

### Portabilidade
A aplicação roda sob `Waitress` em Windows, mas a falta de Dockerização oficial cria fricção em deploys no Linux (PythonAnywhere).

---

## 4. Governança e Ações Futuras (Roadmap V7)

### Curto Prazo (2026 Q2)
- [ ] **Dockerização:** Criar `Dockerfile` oficial para isolar dependências e eliminar problemas de "conflito de porta".
- [ ] **Migração PostgreSQL:** Abandonar SQLite em favor de um SGDB transacional para suportar >10k bolsistas.

### Médio Prazo (2027)
- [ ] **API Rest:** Desacoplar Frontend (React?) do Backend, transformando o Flask em API pura.
- [ ] **Auditoria de Logs:** Implementar ELK Stack para rastreamento granular de ações de usuários (LGPD).

---

## 5. Responsabilidade Técnica
A manutenção deste código exige conhecimento em:
- **Python Avançado:** Decorators, Context Managers.
- **Flask Patterns:** Blueprints, Application Factory.
- **SQLAlchemy:** Eager Loading, Subqueries complexas.

*Documento confidencial. Uso restrito à equipe técnica da UTFPR.*
