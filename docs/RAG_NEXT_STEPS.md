# RAG (Retrieval-Augmented Generation) - Próximos Passos

Este documento serve como um **Ponto de Controle** para retomar a implementação do sistema RAG no Arandú. 

## 📌 Resumo do que foi feito (Fase 1 e 2)
1. **Limpeza e Governança:** O diretório raiz foi limpo. Mais de 150 arquivos de logs e scripts antigos de debug foram arquivados em `_archive/logs_old/`.
2. **Arquitetura Cognitiva Documentada:** Foram gerados os artefatos técnicos `DATABASE_SCHEMA.md` e `ARCHITECTURE.md`, que traduzem as lógicas do `models.py` e os fluxos dos Blueprints do Flask de maneira compreensível.
3. **Exportação da Base de Conhecimento:** O script `scripts/export_rules_to_json.py` extraiu os metadados e regras do banco de dados relacional.
   - 🎯 **Fonte de Dados Primária:** O conhecimento exportado está em `data/knowledge_base/editais_rules.json`.

---

## 🚀 Como Retomar (Fase 3)

Quando você voltar, seu ambiente principal (onde o sistema Arandú roda) ainda estará intacto. Siga estes três passos para iniciar a "incubadora de IA":

### Passo 1: Preparar o Ambiente Isolado
Rode o script de setup que criamos para baixar as dependências (`sentence-transformers` e `chromadb`) em uma bolha que não quebra o seu Flask.

**No Linux/Mac (Bash):**
```bash
sh scripts/setup_rag_env.sh
source .venv_rag/bin/activate
```
**No Windows (PowerShell/CMD):**
```cmd
scripts\setup_rag_env.bat
.venv_rag\Scripts\activate
```

### Passo 2: Criar o Script de Vetorização (Embeddings)
O próximo passo lógico será ler o arquivo `data/knowledge_base/editais_rules.json`, quebrar as regras em pequenos blocos de texto (chunks) e usar o `sentence-transformers` para salvá-los no `ChromaDB`.

*Sugestão:* Criar o arquivo `scripts/generate_embeddings.py`.

### Passo 3: Teste de Busca de Similaridade
Após popular o banco vetorial (`vector_db/`), crie um teste simples (ex: `scripts/test_rag_search.py`) onde você digita *"quais são os critérios de desempate?"* e a IA deve retornar a regra exata extraída do ChromaDB.

Bom descanso! ☕
