# DOCUMENTO INTERNO: PROJETO DE EXPANSÃO "RESERVA TÉCNICA" (V8)
**Confidencial - Uso Interno HaruLabs**

**Data:** 22/01/2026
**Autor:** Board Multidisciplinar (Engenharia, Dados & UX)
**Assunto:** Definição da Arquitetura de Seleção, Rodadas e Banco de Talentos.

---

## 1. Visão Geral e Mudança de Paradigma

Atualmente, o sistema gerencia **Recursos Financeiros** (Bolsas). A Feature V8 expande o escopo para gerenciar **Capital Humano** (Candidatos).

A premissa fundamental é a **Opcionalidade**:
*   **Editais Legados/Simples:** Continuam operando diretamente no cadastro de bolsistas, sem burocracia. O sistema deve "fingir" uma rodada padrão invisível no backend para manter a integridade, mas o usuário não vê.
*   **Editais de Seleção:** Exibem o novo painel de "Gestão de Processo Seletivo".

---

## 2. Análise de Engenharia de Software (Arquitetura)

### 2.1. O "Elo Perdido": A Entidade `Candidatura`
Para atender ao requisito de guardar "Excedentes" sem sujar a tabela principal de `Bolsistas` (que gera custo financeiro/folha), precisamos de uma entidade intermediária.

**Nova Estrutura de Banco de Dados:**

1.  **Edital** (1) <-> (N) **RodadaSelecao**
2.  **RodadaSelecao** (1) <-> (N) **EtapaCronograma**
3.  **RodadaSelecao** (1) <-> (N) **Candidatura** (NOVA)

**Schema Sugerido para `Candidatura`:**
*   `id`: PK
*   `rodada_id`: FK
*   `nome`, `cpf`, `email`: Dados Pessoais.
*   `campus_id`, `programa_id`: Vínculo Acadêmico (Importante: Usar IDs/FKs e não texto solto para analytics).
*   `numero_sei`: String (Processo individual do aluno, se houver).
*   `numero_formulario`: String (Rastreabilidade).
*   `anotacoes`: Text (Campo livre solicitado).
*   `status`: Enum (`EM_ANALISE`, `APROVADO`, `EXCEDENTE`, `DESCLASSIFICADO`).

### 2.2. O Fluxo de "Promoção" (The One-Click Hiring)
O ponto tecnicamente crítico é a transformação de um `Candidato` em `Bolsista`.
*   **Ação:** Botão "Implementar Bolsa" na lista de aprovados.
*   **Backend:** Copia os dados da `Candidatura` -> cria registro em `Bolsista` -> Redireciona para o formulário de bolsista (`/bolsistas/novo`) pré-preenchido com os dados bancários/datas para finalização.
*   **Integridade:** O sistema deve impedir que o mesmo CPF tenha duas candidaturas ativas na mesma rodada.

---

## 3. Análise de Ciência de Dados (Analytics & Business Intelligence)

A criação do "Banco de Excedentes" gera um ativo de dados valioso.

### 3.1. Métricas de Conversão (Funnel Analysis)
Com a nova tabela, podemos medir:
*   **Taxa de Demanda:** `Candidatos / Vagas Ofertadas` (Por Campus/Programa).
*   **Eficiência do Processo:** Tempo médio entre a "Inscrição" e o "Resultado Final".

### 3.2. Rastreabilidade e Auditoria
*   Campos como `link_publicacao` nas etapas do cronograma garantem que o sistema sirva como "Fonte da Verdade" para auditorias futuras. "Onde está o edital de resultado?" -> Está no link salvo na Etapa 3 da Rodada 1.

---

## 4. Análise de UX/UI (Minimalismo e Ads)

O usuário pediu uma interface "Minimalista" e "Intuitiva". Nossa abordagem deve reduzir a carga cognitiva (evitar telas com 50 inputs).

### 4.1. Layout Proposto: "Split-Panel de Operações"
Na página de detalhes do Edital, se o modo "Processo Seletivo" estiver ativo, exibimos dois painéis lado a lado (similar ao Dashboard atual):

**Painel Esquerdo: Cronograma & Controle**
*   Lista vertical das etapas (Timeline).
*   Cada etapa mostra: Data, Status (Pendente/Concluída) e ícone de Link (se houver publicação).
*   Botão discreto `[+ Nova Rodada]` no topo.

**Painel Direito: Lista de Candidatos (O "Funil")**
*   Não uma tabela gigante, mas cartões ou linhas compactas.
*   **Filtros Rápidos (Pills):** `Todos (50)` | `Aprovados (5)` | `Excedentes (10)` | `Desclassificados (35)`
*   **Ação Rápida:** Ao passar o mouse sobre um candidato aprovado, surge o botão "✨ Implementar Bolsa".

### 4.2. Fluxo de Cadastro de Candidatos
*   **Problema:** Cadastrar 50 candidatos um a um é tedioso.
*   **Solução Minimalista:** Permitir cadastro em lote (CSV simples) futuramente, mas para o MVP, um formulário modal que não recarrega a página (AJAX) para inserção rápida sequencial ("Salvar e Adicionar Outro").

---

## 5. Roadmap de Implementação e Riscos

| Risco Identificado | Solução Proposta |
| :--- | :--- |
| **Duplicidade de Dados** | Candidato vira Bolsista e os dados ficam em 2 lugares. **Decisão:** Manter histórico em Candidato (snapshot) e dados vivos em Bolsista. |
| **Erros de Digitação (Campus)** | **Obrigatório:** Usar os Dropdowns já existentes do sistema (Tabela `Campus` e `ProgramaAcademico`) no cadastro de candidatos. |
| **Complexidade para Editais Simples** | **Feature Flag:** Ao criar o Edital, perguntar: "Este edital terá processo seletivo via sistema?" Se NÃO, esconder toda a UI de rodadas. |

---

## 6. Conclusão do Board

A proposta é sólida. Transforma o sistema de um "Gerenciador de Pagamenos" para um "Gerenciador de Ciclo de Vida Acadêmico".

**Recomendação Imediata:**
1.  Criar tabelas `Rodada`, `Etapa`, `Candidatura`.
2.  Implementar a UI "Split-Panel" na view de Editais.
3.  Implementar a lógica de "Promoção" (Candidato -> Bolsista).

*Assinado: H. (Eng), A. (Dados), R. (UX)*
