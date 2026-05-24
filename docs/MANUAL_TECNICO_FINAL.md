# Manual Técnico - Sistema de Gestão de Bolsas V6.2
**Ciclo de Entrega 2026**

## 1. Visão Geral
Este documento consolida as alterações técnicas realizadas para modernizar o **Sistema de Gestão de Editais e Bolsas (PROPPG/UTFPR)**, focando em governança, inteligência de dados e conformidade.

---

## 2. Arquitetura de Dados (PostgreSQL)

### 2.1. Novos Modelos
*   **`BolsaHistorico`**: Armazena a série temporal (2014-2025) de bolsas concedidas.
    *   *Colunas*: `programa_id`, `ano`, `agencia`, `nivel`, `quantidade`.
    *   *Performance*: Índice composto `idx_bolsa_agregado` nas colunas `(ano, agencia, nivel)`.
*   **`DadosFinanceiros`**: Rastreia captação de recursos externos.
    *   *Exemplo*: R$ 22.154.895,86 captados em 2025 (CNPq, Araucária, FINEP).
*   **`AuditoriaLogs`**: Tabela de log para operações sensíveis.

### 2.2. Segurança e Trigger
Um **Database Trigger** (`trg_audit_programa`) foi implementado para monitorar a coluna `tipo_oferta` na tabela `programa_academico`.
*   **Regra**: Qualquer alteração entre "Acadêmico" e "Profissional" é registrada automaticamente em `auditoria_logs` com usuário e timestamp.

---

## 3. Processos de ETL e Scripts

### 3.1. Importação de Histórico
*   **Script**: `scripts/import_scholarship_history.py`
    *   **Função**: Lê os CSVs oficiais (Mestrado/Doutorado), realiza *unpivot* das colunas de anos e normaliza nomes de agências (ex: "CAPES - IES" -> "CAPES").
*   **Recuperação**: Implementamos `scripts/restore_files.py` para reconstrução de binários em caso de perda de arquivos fonte.

### 3.2. Carga 2025
*   **Script**: `scripts/update_ppg_consolidated_2025.py` e `scripts/insert_financial_data.py`.
    *   Garantem que novos cursos (ex: "Design Prospectivo") e valores atualizados estejam presentes.

---

## 4. Dashboard de Inteligência (`/relatorios/estrategico`)

Novo módulo de BI integrado ao sistema.

### 4.1. Funcionalidades
1.  **Evolução Temporal**: Gráfico de linha comparando crescimento de Mestrado vs. Doutorado (2014-2025).
2.  **Qualidade do Investimento**: Gráfico de distribuição de bolsas por Nota CAPES (3 a 7).
3.  **Insights**: Cálculo automático de picos históricos e foco de investimento.

### 4.2. Stack Tecnológica
*   **Backend**: Agregações via SQLAlchemy (`func.sum`, `group_by`).
*   **Frontend**: Chart.js para visualização responsiva.

---

## 5. Manutenção e Comandos Úteis

| Ação | Comando |
| :--- | :--- |
| **Rodar Aplicação** | `python app.py` |
| **Validar Integridade** | `python scripts/final_qa_validation.py` |
| **Restaurar CSVs** | `python scripts/restore_files.py` |
| **Re-importar Histórico** | `python scripts/import_scholarship_history.py` |

---

**Equipe de Desenvolvimento**
*Google Antigravity - Fevereiro/2026*
