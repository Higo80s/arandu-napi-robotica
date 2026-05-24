# Estudo de Melhoria e Migração do Banco de Dados (Gestão de Editais)

**Data:** 13/01/2026
**Responsável:** Antigravity Agent
**Objetivo:** Avaliar a integridade dos dados de "Programas de Pós-Graduação" e propor ajustes para atender aos novos requisitos de seleção na interface.

---

## 1. Análise Atual (Diagnóstico)

### 1.1 Fonte de Dados (Referência 2025)
Utilizamos como referência a "Planilha RG 2025" (constante no script de importação), que contém:
*   **Código Único**: Identificador estrito do programa (ex: `40006018179P5`).
*   **Multicampi**: Programas compartilhados entre campi (ex: `PPGEM` em `CP/PG`).
*   **Níveis**: Registros separados para Mestrado e Doutorado.

### 1.2 Problema Identificado no Banco de Dados Atual
Ao analisar o script de importação vigente, identificamos uma **falha na lógica de processamento**:
1.  **Descarte de Níveis**: O sistema lê as linhas de "Mestrado" e "Doutorado" separadamente. Porém, como elas possuem o mesmo *Código* e *Campus*, a segunda linha (Doutorado) apenas **sobrescreve** a primeira (Mestrado), ou vice-versa.
2.  **Coluna `niveis` Vazia**: A coluna `niveis` existe na tabela `ProgramaAcademico`, mas não está sendo preenchida pelo script.
3.  **Resultado**: O banco sabe que o programa existe, mas não sabe informar se ele é "M", "D" ou "M, D".

### 1.3 Comparativo
| Dado | Planilha RG 2025 | Banco Atual | Status |
| :--- | :--- | :--- | :--- |
| **Código** | `40006018008P6` | `40006018008P6` | OK |
| **Nome** | Engenharia Civil | Engenharia Civil | OK |
| **Nível** | Linha 1: Mestrado<br>Linha 2: Doutorado | **Perdido** (Sobrescrito) | ❌ **CRÍTICO** |
| **Vínculo** | CT (Curitiba) | CT | OK |

---

## 2. Plano de Ajuste e Atualização

### 2.1 Estratégia de Correção
Para atender ao requisito visual `{Código} - {Nome} - {Sigla} - {Campus} ({Níveis})`, faremos:

1.  **Refatoração do Importador**:
    *   Ler todas as linhas da planilha primeiro.
    *   **Agrupar em Memória**: Para cada par (Código, Campus), coletar todos os níveis encontrados (ex: `{'Mestrado', 'Doutorado'}`).
    *   **Gerar String Agregada**: Converter para siglas "M" e "D". Ex: Se tiver ambos, gravar `"M,D"`. Se tiver só mestrado, `"M"`.

2.  **Atualização da Interface (Dropdowns)**:
    *   Modificar as rotas `/posdoc/novo` e `/bolsistas/novo`.
    *   Alterar a query SQL para formatar o `label` do select field concatenando os campos solicitados.

### 2.2 Criação de Ambiente de Teste (Cópia Segura)
Conforme solicitado, criaremos uma **nova cópia do sistema** em uma pasta isolada (`validation_v2`) rodando na porta **5004**.
*   **Banco de Dados**: Será recriado do zero usando a lógica corrigida.
*   **Isolamento**: Não afetará o sistema de produção atual (porta 5003).

---

## 3. Próximos Passos
1.  Executar script de correção no ambiente de teste.
2.  Gerar print da tela mostrando o dropdown correto: `40006018008P6 - ENGENHARIA CIVIL - PPGEC - CT (M,D)`.
3.  Validar e aprovar para produção.
