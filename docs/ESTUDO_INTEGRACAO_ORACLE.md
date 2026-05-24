# Estudo de Viabilidade: Suporte a Oracle e Integração Institucional

## 1. Compatibilidade com Oracle Database

O sistema atual, desenvolvido em **Python (Flask) + SQLAlchemy**, é altamente portável. O SQLAlchemy (ORM utilizado) possui suporte nativo robusto para Oracle Database, o que facilita a adaptação.

### 1.1. Ajustes Técnicos Necessários

Para tornar o sistema compatível com Oracle (além de SQLite e PostgreSQL), seriam necessárias as seguintes adaptações:

1.  **Driver de Conexão**:
    *   Substituição do driver padrão (`sqlite3` ou `psycopg2`) pelo **`oracledb`** (antigo `cx_Oracle`).
    *   Este driver funciona em modo "Thin" (sem necessidade de instalar o Oracle Instant Client pesado), o que facilita o uso em contêineres Docker.

2.  **URI de Conexão (Configuração)**:
    *   A string de conexão muda para: `oracle+oracledb://usuario:senha@host:port/?service_name=xyz`.

3.  **Tipos de Dados e Schemas**:
    *   **Booleanos**: Versões antigas do Oracle (11g/12c) não têm tipo `BOOLEAN` nativo em tabelas. O SQLAlchemy gerencia isso mapeando automaticamente para `NUMBER(1)` (0 ou 1) ou `CHAR(1)` ('Y'/'N'). Versões novas (23c) já suportam.
    *   **Auto-Increment**: Oracle 11g usa `SEQUENCE` + `TRIGGER`. Oracle 12c+ usa `IDENTITY columns` (similar ao Postgres/MySQL). O SQLAlchemy lida bem com ambos, mas é preciso definir a estratégia correta na criação das tabelas.
    *   **Case Sensitivity**: Oracle trata nomes de tabelas sem aspas como UPPERCASE. O SQLAlchemy normaliza isso, mas esquemas legados exigem atenção.

4.  **Custo de Adaptação**:
    *   **Baixo**. O código da aplicação (`app.py`, rotas) permanece 99% inalterado. As mudanças ocorrem apenas na configuração (`config.py`) e na camada de modelos (`models.py`) para garantir compatibilidade de tipos.

---

## 2. Cenários de Integração com Banco Institucional (Universidade)

Para resolver o problema de discrepância de dados (ex: aluno defende tese no sistema acadêmico, mas continua ativo no sistema de bolsas), propomos três cenários de integração, do mais simples ao mais robusto.

### Cenário A: Integração via Views (Banco a Banco)
*Ideal se o banco da Universidade também for Oracle ou permitir acesso direto.*

*   **Como funciona**: A TI da Universidade cria uma **VIEW de leitura (ReadOnly)** contendo apenas os dados necessários (Matrícula, Nome, CPF, Status do Curso, Data de Defesa, Data de Desligamento).
*   **Conexão**: Nosso sistema acessa essa VIEW via `DBLINK` (se ambos forem Oracle) ou via uma conexão secundária configurada no Flask (Bind `institutional_db`).
*   **Vantagem**: Dados em tempo real. Implementação rápida se a rede permitir.

### Cenário B: Integração via API (Web Services)
*Padrão moderno de segurança.*

*   **Como funciona**: A Universidade fornece um endpoint (API REST ou SOAP) onde enviamos o CPF ou Matrícula e recebemos o status atual.
*   **Fluxo**:
    1.  Toda noite, uma rotina (Cron Job) consulta a API para todos os bolsistas ativos.
    2.  Se a API retornar status "Concluído", "Defendido" ou "Desligado", o sistema gera um alerta.
*   **Vantagem**: Segurança (não expõe banco de dados), desacoplamento.

### Cenário C: Carga de Dados (ETL Diário)
*Solução de menor impacto na infraestrutura da TI.*

*   **Como funciona**: A TI disponibiliza diariamente um arquivo (CSV, JSON ou DUMP) em um servidor seguro (SFTP e/ou Bucket).
*   **Fluxo**: Nosso sistema lê esse arquivo toda madrugada e atualiza uma tabela local de "espelho de status".
*   **Vantagem**: Simples, não afeta performance do sistema principal.

---

## 3. Solução Anti-Pagamento Indevido (Fluxo Proposto)

Para evitar o pagamento de bolsas após a defesa/desligamento, propomos a implementação da seguinte lógica de verificação cruzada:

### Requisito: Campo "Matrícula"
Adicionar o campo `matricula_institucional` na tabela `bolsistas` (atualmente usamos CPF, que também serve, mas Matrícula é chave primária acadêmica).

### O Robô de Auditoria (Daily Check)
Criaríamos um script diário (`audit_status.py`) que executa a seguinte lógica:

1.  **Busca**: Seleciona todos os Bolsistas com `ativo = TRUE` em nosso sistema.
2.  **Consulta**: Para cada bolsista, verifica o status na Base Institucional (via View, API ou Espelho).
3.  **Comparação**:
    *   **SE** (Data Defesa Institucional < Hoje) **E** (Bolsista Ativo no Nosso Sistema)
    *   **ENTÃO**:
        1.  Marca flag de "Pendência de Desligamento" no Painel.
        2.  Envia e-mail automático para o Gestor e Orientador: *"Alerta: Discente X defendeu em [Data]. Suspender bolsa imediatamente."*
        3.  (Opcional) Bloqueia automaticamente a geração do pagamento na folha do mês seguinte.

### Benefícios
*   **Prevenção de Erro**: Elimina o delay entre a defesa e a comunicação manual ao gestor da bolsa.
*   **Economia**: Evita processos administrativos de devolução de valores (GRU), que são custosos e burocráticos.
*   **Auditoria**: Garante que o sistema de bolsas esteja sempre sincronizado com a vida acadêmica real do aluno.

## 4. Conclusão

*   **Oracle é viável?** Sim, totalmente suportado pelo SQLAlchemy com esforço baixo de adaptação.
*   **Integração Institucional**: É fundamental para a maturidade do projeto em produção oficial. Recomendamos iniciar o diálogo com a TI solicitando o **Cenário A (View)** ou **Cenário B (API)** para consulta de status acadêmico por CPF/Matrícula.
