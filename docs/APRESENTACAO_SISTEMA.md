# Apresentação do Sistema: Gestão de Editais (V11.4)

## 1. O Problema (A Origem)
Todos aqui conhecem a complexidade de gerenciar bolsas e editais manualmente. Até ontem, nosso processo dependia de:
*   Múltiplas planilhas de Excel desconectadas.
*   Cálculos manuais de datas (Vigência vs. Duração).
*   Risco alto de perder prazos de renovação ou prestação de contas.
*   Dificuldade em responder perguntas simples como: *"Quanto já gastamos neste edital?"*

A ideia do **Gestão de Editais** surgiu da necessidade de **automatizar a burocracia** para que possamos focar no que importa: a gestão acadêmica.

---

## 2. A Solução (Visão Geral)
Desenvolvemos um sistema web centralizado, intuitivo e robusto. Não é apenas uma "planilha melhorada", é uma aplicação completa que **aplica as regras de negócio da universidade automaticamente**.

### Para a Equipe (Facilidade de Uso)
*   **Semáforo de Prazos**: O sistema avisa quem está "Ativo" (Verde), "Finalizando" (Amarelo) ou "Inativo" (Vermelho).
*   **Automação de Datas**: Você insere o início da bolsa e a duração; o sistema calcula o fim, considerando suspensões e regras do edital.
*   **Dashboard Financeiro**: Gráficos em tempo real mostram o saldo de vagas e valores comprometidos.
*   **Alertas Inteligentes (Novo na V11.4)**: Uma central de notificações nos avisa sobre Bolsistas vencendo este mês e Editais pendentes de prestação de contas.

---

## 3. Visão Técnica (Para Engenharia/TI)
O sistema foi construído seguindo padrões de mercado para garantir escalabilidade, segurança e manutenibilidade.

### Arquitetura (Stack)
*   **Backend**: Python 3.11 com framework **Flask**. Escolhido pela robustez e facilidade de manutenção.
*   **ORM (Banco de Dados)**: SQLAlchemy. Garante integridade referencial (ex: não permite excluir um Edital se houver bolsistas ativos vinculados).
*   **Frontend**: HTML5/CSS3 Semântico (Renderização Server-Side via Jinja2). Leve, rápido e responsivo (funciona em mobile).

### Diferenciais de Engenharia
1.  **Banco de Dados Híbrido & Normalizado**:
    *   O banco passou por um processo de **Normalização (3FN)** na versão V5, eliminando redundâncias (Tabelas separadas para `Campus` e `Programas`).
    *   **Dual-Database Support**: O código (`app.py`) detecta o ambiente. Roda com **SQLite** localmente (zero config para o usuário final) e chaveia automaticamente para **PostgreSQL** quando detecta um ambiente de servidor (Docker).

2.  **Containerização (Docker)**:
    *   O sistema está "Dockerizado". Entregamos a aplicação em containers isolados (App + Banco), garantindo que funcione no servidor da Reitoria exatamente como funciona no meu computador.
    *   Uso de **Gunicorn** como servidor de aplicação WSGI para alta concorrência.

3.  **Segurança & Compliance**:
    *   Logs de auditoria nas transações.
    *   Código preparado para registro no **INPI** (Hash SHA-256 gerado).

---

## 4. Onde Estamos (Status do Projeto)
O sistema atingiu a versão **11.4 (Enterprise Ready)**.
*   ✅ Cadastro completo de Editais e Bolsistas.
*   ✅ Regras de Negócio complexas implementadas (ex: cálculo de tempo de suspensão por maternidade).
*   ✅ Relatórios Operacionais e Financeiros.
*   ✅ Infraestrutura pronta para escala.

## 5. Proposta de Piloto
Gostaria de propor a utilização oficial deste sistema no nosso departamento como um **Projeto Piloto**.
O objetivo é validar o ganho de eficiência no dia-a-dia e, com esse "Case de Sucesso", pleitear a adoção institucional junto à DTI/Reitoria.

*Estou à disposição para uma demonstração prática agora mesmo.*
