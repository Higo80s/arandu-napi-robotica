# Plano de Expansão: Módulo de Impacto Social e Demografia (V7+)

**Alinhamento Estratégico:** Novo Modelo de Avaliação CAPES / Plano Nacional de Pós-Graduação (PNPG)
**Foco:** Coleta de dados socioculturais e econômicos para fundamentar políticas de permanência e ações afirmativas.

---

## 1. Contextualização e Justificativa

O atual cenário da Pós-Graduação brasileira exige métricas que vão além da produção bibliográfica e tempo de titulação. A CAPES tem enfatizado a **Avaliação Multidimensional**, onde o **Impacto Social** e a **Inclusão** são eixos centrais.

Para que a Instituição (e o Sistema Haru/Stricto) possa propor políticas eficazes de distribuição de bolsas, é imperativo conhecer o perfil socioeconômico do discente. Sem dados, não há política pública eficiente.

### Objetivos da Expansão:
1.  **Diagnóstico:** Mapear o perfil real dos bolsistas (raça, renda, gênero, origem escolar).
2.  **Políticas de Permanência:** Identificar grupos vulneráveis com maior risco de evasão para priorização de fomento.
3.  **Compliance:** Atender aos quesitos de Ações Afirmativas nos relatórios Sucupira.

---

## 2. Modelagem de Dados Sugerida (Novos Campos)

Para viabilizar esta análise, a tabela `Bolsistas` (ou uma nova tabela vinculada `PerfilSocioeconomico`, relação 1:1) precisará coletar:

### A. Identidade e Diversidade (Dados Sensíveis - LGPD)
*   **Cor/Raça:** (Branca, Preta, Parda, Amarela, Indígena - padrão IBGE).
*   **Pessoas com Deficiência (PCD):** flag booleano + campo descritivo (CID opcional) ou categoria (Visual, Auditiva, Motora, Intelectual).
*   **Identidade de Gênero:** (Cisgênero, Transgênero, Não-binário, etc) - *Diferente do "Sexo" biológico já coletado.*

### B. Contexto Socioeconômico
*   **Renda Familiar *per capita*:** Faixas de Salário Mínimo (até 1,5 SM, 1,5 a 3, > 3, etc).
*   **Origem Escolar:** (Escola Pública Integral, Pública Parcial, Privada com Bolsa, Privada).
*   **Trabalho:** Possui vínculo empregatício além da bolsa? (Sim/Não).
*   **Moradia:** Reside com família, República, Sozinho, Moradia Estudantil.

### C. Fatores Socioculturais e Mobilidade
*   **Primeira Geração:** É o primeiro da família nuclear a cursar Pós-Graduação? (Indicador de mobilidade social).
*   **Parentalidade:** Possui filhos? (Impacto direto na produtividade e necessidade de licença/prorrogação).
*   **Língua Materna:** (Relevante para populações indígenas ou estrangeiros).

---

## 3. Governança de Dados e Ética (LGPD)

A coleta desses dados classifica o sistema como **Controlador de Dados Sensíveis** (Art. 5º, II da LGPD).

**Requisitos Obrigatórios na Implementação:**
1.  **Consentimento Explícito:** O bolsista deve optar por fornecer esses dados (exceto os exigidos por lei para cotas).
2.  **Pseudonimização:** Relatórios gerenciais e dashboards (BI) *nunca* devem exibir o nome do aluno vinculado ao dado sensível (ex: "Lista de alunos com renda X"), apenas agregados estatísticos.
3.  **Controle de Acesso:** Apenas perfis de "Assistência Estudantil" ou "Gestão Estratégica" podem ver os dados brutos. Coordenadores de curso veriam apenas agregados.

---

## 4. Visão de Futuro: O "Stricto Social Intelligence" (Dashboard)

Com esses dados, o sistema evoluirá de um armazenador de cadastros para uma **Ferramenta de Inteligência de Políticas Públicas**.

### Novos Indicadores Possíveis:
*   **Índice de Inclusão do Programa:** % de bolsas destinadas a pretos, pardos e indígenas por PPG.
*   **Correlação Renda x Desempenho:** A vulnerabilidade econômica está afetando o tempo de titulação?
*   **Mapa de Evasão:** Identificar se a evasão é maior em grupos específicos (ex: mães pesquisadoras) para criar editais de apoio suplementar (auxílio-creche, etc).

## 5. Roteiro Técnico Preliminar (V7)

1.  **Fase 1 (Banco de Dados):** Criar Tabela `social_profile` vinculada ao `bolsista_id`.
2.  **Fase 2 (Coleta):** Atualizar formulário de cadastro com aba "Perfil Social" (Opção "Não desejo declarar").
3.  **Fase 3 (Visualização):** Criar Dashboard "Diversidade e Inclusão" no painel administrativo.
4.  **Fase 4 (API):** Conectar com sistemas da Pró-Reitoria de Assuntos Estudantis (se houver) para evitar redigitação.

---
*Documento elaborado pela equipe HaruLabs para planejamento estratégico.*
