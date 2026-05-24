# Arandú NAPI-Robótica - Software Architecture

O sistema Arandú segue uma arquitetura modularizada utilizando o padrão de **Blueprints** do Flask.

## Camada de Aplicação (Blueprints)

1. **`editais_bp` (`/editais`)**
   - **Responsabilidade**: Gerenciamento do ciclo de vida dos processos seletivos.
   - **Fluxos**: Criação de Editais, Rodadas, Cronogramas e o *Painel de Seleção* (onde os candidatos são avaliados e mudam de status).
   - **Interação**: Interage fortemente com os modelos `Edital`, `RodadaSelecao`, `EtapaCronograma` e `Candidatura`.

2. **`bolsistas_bp` (`/bolsistas`)**
   - **Responsabilidade**: Gestão do pós-seleção (ciclo de vida das bolsas).
   - **Fluxos**: Cadastro de novos bolsistas (conversão de `Candidatura` -> `Bolsista`), renovações, cancelamentos, histórico de movimentações (`BolsistaSnapshot`).
   - **Interação**: `Bolsista`, `Modalidade`, `DadosSociais`, `ProgramaAcademico`.

3. **`reports_bp` (`/reports`)**
   - **Responsabilidade**: Geração de PDFs e arquivos fiscais/administrativos.
   - **Fluxos**: Folha Mensal (Bolsa RP), Termos de Compromisso, Relatórios de Gestão por Programa.

4. **`api_v1_bp` (`/api/v1`)**
   - **Responsabilidade**: Backend assíncrono para o frontend (`Omni-Editor`).
   - **Fluxos**: Endpoint centralizado (`/update-component`) responsável pelas operações de edição in-place, drag-and-drop e status via requisições assíncronas (AJAX/Fetch).

## Camada de Dados (SQLAlchemy)
- O mapeamento objeto-relacional é centralizado em `models.py`.
- **RAG Notice**: Para extração de regras e indexação vetorial, as tabelas atreladas a `editais_bp` formam a base de conhecimento estática (regras, cronogramas), enquanto as tabelas de `bolsistas_bp` representam o estado dinâmico (status, vencimentos).

## Camada de Visão (Jinja2)
- Templates residem na pasta `templates/`.
- Uso do padrão "Master" (`dashboard/master_neon.html` e `base.html`).
- Modais são priorizados para ações de escrita a fim de manter as listagens limpas.
