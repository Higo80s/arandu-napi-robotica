#!/bin/bash
echo "=========================================================="
echo "    Setup do Ambiente Vetorial RAG (Isolado)              "
echo "=========================================================="

echo "[1/3] Criando ambiente virtual isolado (.venv_rag)..."
python3 -m venv .venv_rag

echo "[2/3] Ativando ambiente e instalando dependências RAG..."
source .venv_rag/bin/activate
pip install --upgrade pip
pip install -r requirements_rag.txt

echo "[3/3] Verificando instalação..."
python -c "import chromadb; import sentence_transformers; print('>> ChromaDB e SentenceTransformers importados com sucesso!')"

echo "=========================================================="
echo " Setup concluído! O ambiente principal do Arandú não foi afetado."
echo " Para usar, ative com: source .venv_rag/bin/activate"
echo "=========================================================="
