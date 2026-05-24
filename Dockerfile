# Base Image: Python 3.11 Slim (Leve e segura)
FROM python:3.11-slim

# Variáveis de Ambiente
# PYTHONDONTWRITEBYTECODE: Impede criação de .pyc
# PYTHONUNBUFFERED: Garante logs em tempo real
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Diretório de Trabalho
WORKDIR /app

# Instalação de Dependências do Sistema (Bibliotecas p/ Postgres e PDF)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar Requirements e Instalar Dependências Python
# Dica: Copiar só o requirements primeiro otimiza o cache do Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn psycopg2-binary

# Copiar Código Fonte
COPY . .

# Criar diretório instance (para consistência, mesmo que use banco externo)
RUN mkdir -p instance

# Expor Porta 5000 (Padrão Flask/Gunicorn)
EXPOSE 5000

# Comando de Inicialização (Bootstrapping DB + Gunicorn)
# Usa 'sh -c' para encadear comandos
CMD ["sh", "-c", "python scripts/init_db.py && gunicorn --workers=4 --bind=0.0.0.0:5000 app:app"]
