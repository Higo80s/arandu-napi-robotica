# Guia de Implantação (Deploy) com Docker
**Gestão de Editais - Versão Enterprise**

Este guia é destinado à equipe de **Tecnologia da Informação (TI)** da Universidade. Ele descreve os passos para implantar o sistema em um servidor de produção usando containers Docker.

## 1. Pré-requisitos
O servidor de destino deve ter instalado:
- **Docker Engine** (v20.10+)
- **Docker Compose** (v2.0+)
- Acesso à Internet (para baixar as imagens Python e Postgres)

## 2. Instalação Rápida

1. **Clone o Repositório** (ou copie a pasta do projeto para o servidor via SFTP):
   ```bash
   git clone https://github.com/seu-usuario/gestao_editais.git
   cd gestao_editais
   ```

2. **Configure as Variáveis de Ambiente**:
   O arquivo `docker-compose.yml` já vem com configurações padrão. Para produção, é **altamente recomendável** alterar as senhas.
   
   Edite o `docker-compose.yml`:
   ```yaml
   environment:
     - POSTGRES_PASSWORD=sua_senha_segura_aqui  # No serviço 'db'
     - DATABASE_URL=postgresql://gestao_user:sua_senha_segura_aqui@db:5432/gestao_editais_db # No serviço 'web'
     - SECRET_KEY=chave_aleatoria_super_secreta # No serviço 'web'
   ```

3. **Inicie os Serviços**:
   Execute o comando abaixo para construir a imagem e subir os containers em segundo plano (detached):
   ```bash
   docker-compose up -d --build
   ```

4. **Verifique o Status**:
   ```bash
   docker-compose ps
   ```
   *O sistema estará acessível na porta 5000 do servidor (ex: `http://servidor:5000`).*

## 3. Manutenção

### Acessando os Logs
Para ver o que está acontecendo na aplicação:
```bash
docker-compose logs -f web
```

### Atualizando o Sistema
Quando houver uma nova versão do código:
```bash
git pull origin main
docker-compose up -d --build
```
*O Docker irá reconstruir apenas as camadas necessárias.*

## 4. Backup e Restauração (PostgreSQL)

Como o banco agora roda dentro de um container, o backup é feito via comando `pg_dump`.

### Realizar Backup (Dump)
```bash
# Cria um arquivo backup_hoje.sql no servidor host
docker-compose exec -t db pg_dump -U gestao_user gestao_editais_db > backup_hoje.sql
```

### Restaurar Backup
⚠️ **Cuidado:** Isso apaga os dados atuais.
```bash
cat backup_hoje.sql | docker-compose exec -T db psql -U gestao_user gestao_editais_db
```

## 5. Migração de Dados (SQLite -> Postgres)
Se a universidade já utilizava a versão "Mono-usuário" (SQLite) e deseja migrar os dados:

1. A aplicação suporta um script de migração (não incluso neste pacote padrão).
2. Recomendamos iniciar o banco Postgres "limpo" para novas instalações institucionais.

---
**Suporte Técnico**
Para dúvidas de infraestrutura, consulte a documentação oficial do [Docker](https://docs.docker.com/).
