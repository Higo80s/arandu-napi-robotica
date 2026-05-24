# Arandú NAPI-Robótica - Database Schema

Este documento apresenta as tabelas e relacionamentos vitais para o motor de busca vetorial (RAG) do sistema Arandú. Tabelas focadas em log ou metadados de UI (ex: `UIState`, `AuditLog`) foram omitidas por clareza.

## Core Acadêmico e Seleção

### `edital` (Edital)
Representa um instrumento de seleção de fomento.
- `id` (PK)
- `numero_ano` (String) - Ex: "01/2026"
- `titulo` (String) - Nome descritivo do edital
- `link_edital` (String) - URL original
- `data_publicacao` (Date)
- **Relações**: Tem muitas `EditalRegra` e `RodadaSelecao`.

### `edital_regra` (EditalRegra)
Critérios específicos atrelados a um edital (usados como fonte de verdade para o RAG).
- `id` (PK)
- `edital_id` (FK -> `edital.id`)
- `descricao` (Text) - O texto da regra
- `ordem` (Integer)

### `rodada_selecao` (RodadaSelecao)
Chamadas específicas dentro de um Edital.
- `id` (PK)
- `edital_id` (FK -> `edital.id`)
- `nome` (String) - Ex: "Chamada 1"
- `data_inicio`, `data_fim` (Date)
- `ativa` (Boolean)
- **Relações**: Tem muitas `EtapaCronograma` e `Candidatura`.

### `etapa_cronograma` (EtapaCronograma)
Datas importantes de uma Rodada.
- `id` (PK)
- `rodada_id` (FK -> `rodada_selecao.id`)
- `nome` (String)
- `data_inicio`, `data_limite` (Date)
- `concluida` (Boolean)

---

## Core de Pessoas e Fomento

### `candidatura` (Candidatura)
Pessoas inscritas em uma Rodada de Seleção.
- `id` (PK)
- `rodada_id` (FK -> `rodada_selecao.id`)
- `nome`, `email`, `cpf`, `numero_sei` (Strings)
- `status` (Enum: `INSCRITO`, `SELECIONADO`, `EXCEDENTE`, `REJEITADO`, `EFETIVADO`)
- `projeto_pesquisa` (String)
- `campus_id`, `programa_id` (FKs opcionais)
- `instituicao`, `cidade` (Strings para parceiros externos)

### `bolsista` (Bolsista)
Candidatos que tiveram matrícula efetivada no sistema.
- `id` (PK)
- `cpf` (EncryptedString)
- `nome`, `email`, `banco`, `agencia`, `conta_corrente`
- `modalidade_id` (FK -> `modalidade.id`)
- `programa_id` (FK -> `programa_academico.id`)
- `ativo` (Boolean)
- `data_inicio`, `data_fim` (Date)

---

## Core Institucional

### `campus` (Campus)
- `id` (PK)
- `nome` (String) - Ex: "Curitiba"
- `instituicao` (String) - Ex: "UTFPR"

### `programa_academico` (ProgramaAcademico)
- `id` (PK)
- `campus_id` (FK -> `campus.id`)
- `nome_programa` (String)
- `area_conhecimento` (String)
- `niveis` (String) - Ex: "ME/DO"
