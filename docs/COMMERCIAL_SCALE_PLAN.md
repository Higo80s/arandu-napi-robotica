# Arquitetura para Escala Comercial (Universidades Públicas)

Este documento descreve o roteiro técnico para transformar o protótipo "Gestão de Editais" em uma solução Enterprise pronta para implantação em servidores de TI de universidades.

## 1. Containerização (Docker)

O uso de Docker elimina o clássico problema "funciona na minha máquina". Facilita a auditoria de segurança e a instalação pela equipe de TI da universidade (STI/DTI).

### 1.1 Dockerfile (Aplicação)
Imagem leve baseada em `python:3.11-slim`.
- **Gunicorn**: Servidor WSGI robusto (substitui o Waitress em Linux/Prod).
- **Dependências**: Instalação limpa via requirements.txt.
- **Usuário não-root**: Segurança básica.

### 1.2 Docker Compose (Orquestração)
Arquivo único para subir todo o ambiente:
1.  **Web App**: O Flask rodando Gunicorn.
2.  **Database**: PostgreSQL 16 (Imagem oficial).
3.  **Reverse Proxy (Opcional)**: Nginx para SSL/TLS e arquivos estáticos.

## 2. Migração de Banco de Dados (SQLite -> PostgreSQL)

O SQLite é excelente para até ~5 usuários simultâneos. Para uma universidade (Secretarias, Departamentos, Coordenações acessando juntos), o PostgreSQL é obrigatório.

### 2.1 Adaptação do Código (`app.py`)
Atualmente, o banco é hardcoded:
```python
db_path = os.path.join(basedir, 'instance', 'gestao_editais_new.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
```

Mudança necessária (Uso de Variáveis de Ambiente):
```python
# Tenta ler do ambiente (Docker), senão cai no SQLite (Desenvolvimento Local)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///' + db_path)
```

### 2.2 Migração de Dados
Se houver dados reais no SQLite, usaremos um script de "dump" e "load" para o Postgres, ou ferramentas como `pgloader`.

## 3. Segurança & Auditoria (Requisitos Enterprise)

Para venda/licitação, estes pontos são cobrados em Editais de TI:

-   **Logs de Auditoria**: Quem mexeu no quê? (AuditLog Table).
-   **HTTPS**: Obrigatório. (Nginx resolve).
-   **Backup Automatizado**: Script de dump diário do Postgres.

---

## 4. Plano de Ação Imediato

1.  [ ] Criar `Dockerfile`.
2.  [ ] Criar `docker-compose.yml` com Postgres.
3.  [ ] Atualizar `app.py` para suportar `DATABASE_URL`.
4.  [ ] Testar subida dos containers localmente.
