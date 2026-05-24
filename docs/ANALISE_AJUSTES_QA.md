# Plano de Análise e Ajustes (QA Staging)

> **Ambiente**: Teste (Staging)
> **Objetivo**: Corrigir inconsistências de dados e validar lógica do painel antes da aplicação oficial.

## 1. Diagnóstico e Proposta de Correção

### A. Duplicidade no Curso "Zootecnia"
*   **Problema**: Existem dois registros de cursos de Zootecnia no Banco de Dados.
    *   `ID 114`: "Zootecnia" (Campus: Dois Vizinhos) - **0 Bolsistas vinculados**.
    *   `ID 115`: "Zootecnia (Associação Unioeste e DV)" - **12 Bolsistas vinculados**.
*   **Análise**: O ID 114 parece ser um "lixo" de importação ou teste antigo. O ID 115 é o correto e ativo.
*   **Ação Proposta**: Excluir o registro `ID 114`.

### B. Opção "Multi" (Novo Discente/Residente)
*   **Problema**: Verificar se a opção "Multi" no campo Campus está em uso.
*   **Análise**: Existe um Campus chamado "Multicampi" (`ID 14`). Ele possui vínculos com programas acadêmicos, mas **nenhum bolsista ativo** está ligado diretamente a ele (apenas zerados).
*   **Ação Proposta**: 
    1. Manter o registro no banco (pois está ligado a Programas).
    2. Via código, ocultar "Multi" do formulário de *Novo Discente* se a regra de negócio exigir que o aluno esteja sempre em um campus físico. **Decisão:** Manter oculto ou renomear para "Multicampi (Adm)".

### C. Dados de Teste ("tes campus" e "testgrafh")
*   **Problema**: Registros de lixo visíveis nos filtros.
*   **Análise**: Confirmada a existência no banco.
*   **Ação Proposta**: Exclusão física (Delete) desses registros nas tabelas `Campus` e `ProgramaAcademico`.

### D. Dashboard: Arrecadação Jan-Dez 2026
*   **Problema**: Verificar se o cálculo anual considera o período correto (Jan-Dez do ano corrente).
*   **Análise de Código (`app.py` / `/api/dashboard-data`)**:
    *   A lógica atual soma `b.modalidade.valor_mensal` para todos os bolsistas ativos *hoje*.
    *   **Correção Necessária**: O cálculo de "Arrecadação Anual" (YTD) geralmente projeta o gasto *até o fim do ano* ou soma o *gasto realizado*. A lógica atual parece estar mostrando apenas uma projeção simplificada ou snapshot.
    *   **Ação**: Ajustar a query para somar pagamentos de `Jan/2026` a `Dez/2026` (baseado na vigência das bolsas).

### E. Dashboard: Gráficos (Por Campus/Programa)
*   **Problema**: Validar integridade.
*   **Análise**: A lógica agrupa bolsistas ativos. A duplicidade de "Zootecnia" estava dividindo os dados.
*   **Ação**: Após a correção do item A (Zootecnia), o gráfico se corrigirá automaticamente.

### F. Ocupação de Vagas
*   **Problema**: Verificar atualização.
*   **Análise**: O cálculo é `Vagas Totais (Modalidade) - Bolsistas Ativos Hoje`.
*   **Ação**: Validar se a definição de "Ativo" (Data de Hoje entre Início e Fim) está correta. (Parece correta no código linha 1459).

---

## 2. Plano de Execução (Passo a Passo)

### Fase 1: Limpeza de Dados (SQL)
Executar script Python na shell interativa para:
1.  `DELETE FROM programa_academico WHERE id = 114;` (Zootecnia Vazio)
2.  `DELETE FROM campus WHERE nome LIKE '%tes%';` (Lixo)
3.  `DELETE FROM programa_academico WHERE nome_programa LIKE '%test%';` (Lixo)

### Fase 2: Ajuste de Código (Backend)
1.  **Dashboard Financeiro**: Revisar função `dashboard_data` para garantir que `total_anual` considere o ano de 2026 (Projeção: Valor Mensal * Meses Restantes no Ano + Meses Pagos).

### Fase 3: Validação
1.  Acessar painel e verificar desaparecimento de "Zootecnia" duplicado.
2.  Verificar valores financeiros.

---
**Pergunta**: Posso iniciar a **Fase 1 (Limpeza de Dados)** imediatamente no ambiente de teste?
