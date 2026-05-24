# Estudo de Viabilidade Técnica e Plano de Recuperação
## Sistema de Gestão de Editais e Bolsas - UTFPR (Ciclo 2026+)

**Data:** 14/02/2026
**Responsável:** Arquiteto de Soluções (Google Antigravity)
**Contexto:** Bloqueio na carga de histórico de bolsas (2014-2025) por ausência de arquivos fonte.

---

### 1. Estudo de Recuperação de Dados (Data Recovery)

**Análise de Viabilidade:**
A recuperação **completa** (100% dos 2.532 registros) através do histórico da conversa (`chat context`) é **tecnicamente inviável**.
*   **Motivo**: Os logs fornecidos anteriormente continham apenas *amostras* (`head()`, `tail()`) e *agregados* (`groupby()`). O conjunto de dados integral não foi exposto textualmente, impossibilitando a reconstrução bit-a-bit dos arquivos CSV originais.

**Solução de Contorno (Mock/Seeding):**
É possível criar um script de *Seeding* (`scripts/seed_history_audit.py`) que:
1.  Insere os dados **amostrais** conhecidos (ex: PPGEQ e PGTM com seus valores de 2025 e histórico parcial).
2.  Gera dados **sintéticos** (placeholders) para os demais programas, permitindo validar a infraestrutura de BI e os dashboards *antes* da carga real.
3.  **Recomendação**: Esta abordagem desbloqueia o desenvolvimento do Frontend/BI, mas **não substitui** o upload dos arquivos reais para a Auditoria Governamental.

---

### 2. Análise de Arquitetura e Performance (`BolsaHistorico`)

**Schema Atual:**
```python
pk(id), fk(programa_id), ano, agencia, nivel, quantidade
```

**Avaliação de Performance:**
*   **Modelo Star Schema**: A estrutura está correta para BI (Tabela Fato).
*   **Pontos de Atenção**:
    *   **Cardinalidade**: Com ~2.500 registros iniciais, a performance será instantânea mesmo sem índices complexos.
    *   **Escalabilidade**: Para suportar milhões de registros (ex: microdados de pagamentos mensais 2014-2025), a estrutura atual pode sofrer.

**Otimizações Propostas (PostgreSQL):**
1.  **Índices Compostos**:
    ```sql
    CREATE INDEX idx_bolsa_agregado ON bolsa_historico (campus_id, ano, agencia);
    ```
    *Nota: Requer desnormalizar `campus_id` para a tabela de histórico ou fazer JOIN eficiente.*
2.  **Materialized View (Relatórios Mensais):**
    Para o relatório de gestão que exige "Total por Campus/Ano", uma View Materializada é recomendada para evitar recálculo em tempo real se o volume crescer.

---

### 3. Auditoria e Integridade (Programas Profissionais)

**Estratégia `tipo_oferta`:**
*   **Suficiência**: A coluna é suficiente para *filtragem*, mas não para *garantia de regra de negócio*.
*   **Risco**: Um operador humano pode alterar acidentalmente um programa "Profissional" para "Acadêmico", liberando indevidamente verbas de fomento.

**Mitigação (Plano de Segurança):**
1.  **Trigger de Auditoria (`AuditLog`)**:
    Implementar gatilho no PostgreSQL que registra qualquer alteração na coluna `tipo_oferta` na tabela `auditoria_logs`.
2.  **Constraint de Fomento**:
    ```sql
    -- Exemplo conceitual
    CONSTRAINT chk_fomento_profissional 
    CHECK (tipo_oferta = 'Profissional' OR agencia != 'Tesouro Direto Exclusivo Profissional')
    ```

---

### 4. Roadmap de Desbloqueio e Implementação

| Fase | Ação | Responsável | Status |
| :--- | :--- | :--- | :--- |
| **1. Infraestrutura** | Criar tabelas `bolsa_historico` e `dados_financeiros`. | Antigravity | **Concluído** |
| **2. Contorno** | Criar script de dados sintéticos para teste de BI. | Antigravity | *Pendente* |
| **3. Carga Real** | **Upload dos Arquivos CSV originais.** | **Usuário** | **BLOQUEANTE** |
| **4. Processamento** | Executar `scripts/import_scholarship_history.py`. | Antigravity | *Aguardando* |
| **5. Validação** | Gerar relatório SQL comparativo com o DOCX da PROPPG. | Antigravity | *Aguardando* |

---

**Conclusão Técnica:**
O sistema está pronto para receber os dados. A arquitetura é sólida. Recomendo o **upload imediato dos arquivos** para garantir a fidelidade da auditoria. Enquanto isso, posso gerar dados sintéticos para não travar o desenvolvimento dos painéis de visualização.
