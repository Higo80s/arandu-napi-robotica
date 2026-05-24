@echo off
echo ==========================================================
echo     Setup do Ambiente Vetorial RAG (Isolado)              
echo ==========================================================

echo [1/3] Criando ambiente virtual isolado (.venv_rag)...
python -m venv .venv_rag

echo [2/3] Ativando ambiente e instalando dependencias RAG...
call .venv_rag\Scripts\activate
pip install --upgrade pip
pip install -r requirements_rag.txt

echo [3/3] Verificando instalacao...
python -c "import chromadb; import sentence_transformers; print('>> ChromaDB e SentenceTransformers importados com sucesso!')"

echo ==========================================================
echo  Setup concluido! O ambiente principal do Arandu nao foi afetado.
echo  Para usar, ative com: .venv_rag\Scripts\activate
echo ==========================================================
pause
