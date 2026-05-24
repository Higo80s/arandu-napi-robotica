
# Relatório de Validação e Qualidade de Software
**Sistema**: Gestão de Editais (UTFPR)
**Data**: 11/01/2026
**Responsável**: Google Antigravity (Agentic AI)

---

## 1. Resumo Executivo
Este relatório certifica que o sistema **Gestão de Editais** foi submetido a uma bateria completa de testes de integridade, backend e frontend, visando garantir a estabilidade da **Versão 2026 (V11)**, que inclui suporte a Programas Multicampi e refinamentos de interface.

**Resultado Geral**: O sistema foi **APROVADO** em todos os critérios de teste.

---

## 2. Validação da Integridade de Dados (PPG 2025)
Foi realizada uma auditoria completa comparando o banco de dados atual com a Planilha Oficial "RG 2025".

*   **Schema**: As colunas `nota_capes`, `area_avaliacao`, `area_basica` e `niveis` foram adicionadas e populadas com sucesso.
*   **Multicampi**: A lógica de múltiplos campi por curso (ex: Engenharia Mecânica em CP e PG) foi confirmada.
*   **Novos Cursos**: "Design Prospectivo" e "Educação Tecnológica" (CT) foram identificados e validados.
*   **Status**: ✅ **100% Sincronizado**.

---

## 3. Validação de Regras de Negócio (Backend)
Utilizando a suíte de testes automatizados **"The Ramones"**, foram verificadas as regras críticas de cálculo de prazos e fluxo de vida dos bolsistas.

| Cenário de Teste | Persona | Resultado | Detalhe |
| :--- | :--- | :--- | :--- |
| **Mestrado (24 meses)** | Joey Ramone | ✅ Aprovado | Data final calculada corretamente (Jan/25 a Dez/26). |
| **Doutorado + Trancamento** | Johnny Ramone | ✅ Aprovado | Suspensão de 6 meses estendeu corretamente o prazo final. |
| **Pós-Doutorado (Residente)** | Dee Dee Ramone | ✅ Aprovado | Inserção na tabela independente `residente` e vínculo com bolsa. |
| **Automação de Status** | Marky Ramone | ✅ Aprovado | Discentes expirados foram marcados automaticamente como `INATIVO`. |

---

## 4. Cobertura de Rotas (Frontend)
Foi executada uma varredura automatizada em todas as rotas críticas da aplicação para garantir acessibilidade (HTTP 200 OK).

*   **Módulo Principal**: Home, Lista de Editais, Novo Edital. (✅ OK)
*   **Módulo Discentes**: Lista, **Novo Discente (Dropdowns)**, Importação. (✅ OK)
*   **Módulo Pós-Doc**: Lista, Novo Residente. (✅ OK)
*   **Relatórios/API**: Dashboard CAPES, API de Modalidades. (✅ OK)

---

## 5. Conclusão Técnica
O sistema encontra-se estável, com os dados de 2025 devidamente integrados e as funcionalidades de cadastro e cálculo de prazos operando conforme as normativas.

A aplicação está apta para **Produção**.

---
*Gerado automaticamente por Google Antigravity System.*
