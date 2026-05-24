# Estudo de Viabilidade Técnica e Diagnóstico de Arquitetura: Implementação de RAG

## Introdução
Este documento apresenta a análise de viabilidade técnica para a integração de um sistema **RAG (Retrieval-Augmented Generation)** no sistema Arandú NAPI-Robótica. O objetivo é permitir que o sistema responda perguntas complexas baseadas em seus próprios dados (editais, candidatos, regras) e em conhecimentos externos (manuais e legislações).

---

## 1. Diagnóstico de Estrutura e Dados

### Onde residem as regras de negócio e dados críticos?
- **Modelos de Banco de Dados (`models.py`)**: A estrutura principal reside aqui. Classes críticas incluem `Edital`, `EditalRegra`, `EtapaCronograma`, `Candidatura`, `Bolsista`, `RodadaSelecao` e entidades estruturais como `Campus`, `ProgramaAcademico` e `Instituicao`.
- **Lógica de Aplicação (`blueprints/`)**: As regras de negócio para processamento estão distribuídas nos blueprints (ex: `editais.py`, `bolsistas.py`, `reports_bp.py`, `api_v1.py`).
- **Lógica Auxiliar (`utils/`)**: Funções de formatação, idempotência e verificações.

### Consistência da Documentação e Lacunas
- **Ponto Forte**: O projeto possui um vasto acervo de arquivos de documentação (ex: `DOCUMENTACAO.md`, `GLOSSARIO_TECNICO.md`, diversos PDFs e relatórios de estudos técnicos como `ESTUDO_BANCO_DADOS.md`).
- **Lacunas para um LLM**: 
  - **Fragmentação**: Há dezenas de arquivos de log (`.txt`), scripts de debug isolados (`debug_*.py`), e arquivos soltos (ex: `out.txt`, `err.txt`) na raiz do projeto. Um LLM ingerindo tudo isso sem filtros pode sofrer alucinações baseadas em dados de debug antigos.
  - **Falta de uma API Doc Estruturada**: Não há um OpenAPI/Swagger claro listando os payloads aceitos de forma padronizada para as rotas.
  - **Esquema de Banco de Dados**: Há múltiplos scripts de verificação (ex: `schema_mapping.txt`), mas uma visão unificada e limpa do schema atualizado precisa ser curada.

---

## 2. Mapeamento de Falhas e Erros

### Conflitos entre Arquitetura Atual e Camada de Vetorização
- **Falta de Identificadores de Contexto (Metadata)**: Quando vetorizarmos o conteúdo, precisaremos garantir que um "chunk" de texto sobre um `Edital` saiba referenciar o `edital_id` e `rodada_id` para que a busca seja filtrada por contexto (ex: "Quais as regras do edital 5?", o vetor precisa ter metadados atrelados para filtragem exata antes do RAG, evitando misturar regras de editais diferentes).
- **Mutabilidade dos Dados**: Dados como "Candidaturas" mudam de status frequentemente. Um RAG baseado em dados dinâmicos requer *Real-Time Embedding* ou buscas híbridas (SQL para dados estruturados + Vector DB para dados não estruturados). Apenas vetorizar o banco relacional não é eficiente.

### Arquivos Carentes de Padronização para IA
- Scripts de migração e auditoria (`carga_março_2026.py`, `debug_capes_final.py` etc.) não têm docstrings claros sobre se são apenas históricos ou de uso contínuo.
- Relatórios em formato `.txt` não estruturado deveriam ser convertidos para JSON ou Markdown para ingestão limpa por IA.

---

## 3. Plano de Documentação Automatizada

Para compor uma base RAG de alta qualidade, posso gerar e consolidar os seguintes artefatos:

1. **`docs/ARCHITECTURE.md`**: Um documento unificado descrevendo a separação de responsabilidades (Blueprints, Models, Utils) e o fluxo de dados (ex: como um candidato vira bolsista e entra na folha).
2. **`docs/API_REFERENCE.md`**: Mapeamento das rotas do sistema (especialmente `/api/v1/update-component` e relatórios) com payloads esperados e respostas.
3. **`docs/DATABASE_SCHEMA.md`**: Uma representação em Markdown (tabelas e relacionamentos vitais) limpa, gerada a partir do `models.py`, focando apenas nas tabelas ativas e desconsiderando históricos depreciados.
4. **Refinamento do `CONTRIBUTING.md` / `COMO_USAR.md`**: Consolidar as regras de implantação, variáveis de ambiente (do `.env.example`) e comandos de execução (limpando o excesso de scripts `.bat` e `.vbs`).

---

## 4. Composição de Dados Externos

Para o Arandú atuar como um "Assistente de Seleção e Fomento", o RAG deve ingerir:
- **Editais em PDF/Texto**: Arquivos PDF originais dos editais (CAPES, PROPPG, Fundação Araucária) processados via OCR/Extração de texto.
- **Manuais Institucionais**: Regulamentos de pós-graduação da UTFPR e normas do NAPI-Robótica.
- **Portarias Governamentais**: Portarias da CAPES e CNPq relativas a acúmulo de bolsas, valores e requisitos de titulação.
- **Dicionário de Programas/Campi**: Tabelas de referência oficias do MEC/Sucupira.

---

## 5. Recomendação e Estratégia "Free-Tier"

### Avaliação de Necessidade
Um RAG é altamente recomendado se os gestores precisarem de respostas instantâneas como:
- *"O candidato João pode acumular esta bolsa com vínculo empregatício segundo o edital vigente?"*
- *"Quais são os critérios de desempate da Rodada 2?"*
- *"Gere um rascunho de e-mail cobrando relatórios dos bolsistas atrasados baseando-se no cronograma do Edital 5."*

### Estratégia "Free-Tier" (Custo Zero)
Para evitar custos com APIs fechadas (OpenAI, Anthropic):
1. **Modelos de Embedding (Geração de Vetores)**: Usar biblioteca `sentence-transformers` (ex: modelo `all-MiniLM-L6-v2` via Hugging Face). Roda localmente na CPU de forma rápida e grátis.
2. **Banco de Dados Vetorial**: Utilizar **FAISS** (Facebook AI Similarity Search) ou **ChromaDB**. Ambos são open-source, rodam localmente (como o SQLite para vetores) e não exigem servidor externo.
3. **LLM para Geração**: 
   - Se houver capacidade de hardware local (GPU/RAM suficiente), rodar um modelo open-source via **Ollama** (ex: `Llama-3-8B` ou `Mistral`).
   - Se o servidor for limitado (nuvem barata), utilizar o **Google Gemini API** (Nível Gratuito - Free Tier), que permite processar contexto extenso gratuitamente (com limites de RPM razoáveis para uso interno administrativo).

---

## 6. Workflow de Execução (Passo a Passo)

1. **Fase 1: Ingestão e Limpeza (Preparação da Base de Conhecimento)**
   - Consolidar as regras dos editais ativos (`EditalRegra`) e manuais externos em arquivos Markdown estruturados.
   - Limpar e unificar a documentação técnica atual (ex: remover logs antigos).

2. **Fase 2: Motor de Indexação (Embedding)**
   - Criar um script Python autônomo (ou um blueprint `rag_bp.py`) que consome os documentos Markdown e as descrições dos editais do PostgreSQL, quebra em *chunks* (ex: 500 tokens) e gera os embeddings via `sentence-transformers`.
   - Armazenar esses vetores no `ChromaDB` persistente (ex: na pasta `/database/vector_store`).

3. **Fase 3: Rota de Busca (Retrieval)**
   - Quando o usuário fizer uma pergunta na interface, o sistema converterá a pergunta em um vetor, buscará os top-K (ex: 5) *chunks* mais relevantes no ChromaDB, cruzando com filtros de metadata (ex: `edital_id = 3`).

4. **Fase 4: Geração com Contexto (Augmented Generation)**
   - Montar um prompt estruturado: *"Responda a pergunta usando APENAS o contexto fornecido. Contexto: [textos recuperados]. Pergunta: [pergunta do usuário]."*.
   - Enviar ao LLM (Gemini Free Tier ou Ollama) e retornar a resposta formatada na interface.

5. **Fase 5: Interface do Assistente**
   - Criar uma interface de chat no template `dashboard/master_neon.html` ou em uma aba dedicada (`/assistente`), com indicação de fontes (citações) de onde o assistente tirou a resposta.
