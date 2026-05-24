# Plano de Implantação - Sistema de Gestão de Editais

**Versão:** 1.0  
**Data:** Janeiro 2026  
**Responsável:** Higo Santos

---

## 1. Visão Geral

Este documento detalha o processo de implantação do Sistema de Gestão de Editais em servidor institucional da UTFPR.

### 1.1 Premissas

- Servidor Linux disponibilizado pela DIRGTI/DESIS-RT
- Acesso SSH com privilégios sudo
- PostgreSQL disponível ou instalável
- Conectividade de rede interna UTFPR

---

## 2. Preparação do Ambiente

### 2.1 Requisitos de Sistema

```bash
# Sistema Operacional
Ubuntu 22.04 LTS (recomendado) ou similar

# Recursos Mínimos
CPU: 2 cores / 4 cores (recomendado)
RAM: 2 GB / 4 GB (recomendado)
Disco: 10 GB / 20 GB (recomendado)

# Software Base
Python 3.11 ou superior
PostgreSQL 14 ou superior
Git
Nginx (opcional, para proxy reverso)
```

### 2.2 Instalação de Dependências do Sistema

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python 3.11+
sudo apt install python3.11 python3.11-venv python3-pip -y

# Instalar PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Instalar Git
sudo apt install git -y

# Instalar Nginx (opcional)
sudo apt install nginx -y

# Instalar supervisor (para gerenciar processo)
sudo apt install supervisor -y
```

---

## 3. Configuração do Banco de Dados

### 3.1 Criar Banco PostgreSQL

```bash
# Acessar PostgreSQL
sudo -u postgres psql

# Criar usuário
CREATE USER gestao_editais WITH PASSWORD 'SENHA_SEGURA_AQUI';

# Criar banco de dados
CREATE DATABASE gestao_editais_db OWNER gestao_editais;

# Conceder privilégios
GRANT ALL PRIVILEGES ON DATABASE gestao_editais_db TO gestao_editais;

# Sair
\q
```

### 3.2 Testar Conectividade

```bash
psql -h localhost -U gestao_editais -d gestao_editais_db
# Inserir senha quando solicitado
```

---

## 4. Deploy da Aplicação

### 4.1 Criar Usuário do Sistema

```bash
# Criar usuário dedicado (boa prática de segurança)
sudo adduser --system --group --home /opt/gestao_editais gestao_app
```

### 4.2 Clonar Repositório

```bash
# Como usuário gestao_app
sudo su - gestao_app

# Clonar repositório
cd /opt/gestao_editais
git clone https://github.com/Higo80s/gestao_editais.git app
cd app
```

### 4.3 Configurar Ambiente Virtual

```bash
# Criar ambiente virtual
python3.11 -m venv .venv

# Ativar ambiente
source .venv/bin/activate

# Atualizar pip
pip install --upgrade pip

# Instalar dependências
pip install -r requirements.txt
```

### 4.4 Configurar Variáveis de Ambiente

```bash
# Criar arquivo .env
nano .env
```

Conteúdo do arquivo `.env`:

```bash
# Configuração de Banco de Dados
DATABASE_URL=postgresql://gestao_editais:SENHA_SEGURA_AQUI@localhost/gestao_editais_db

# Chave Secreta (gerar uma única via: python -c "import os; print(os.urandom(24).hex())")
SECRET_KEY=sua_chave_secreta_de_64_caracteres_aqui

# Ambiente
FLASK_ENV=production

# Porta (opcional, padrão 5003)
PORT=5003
```

### 4.5 Inicializar Banco de Dados

```bash
# Ativar ambiente virtual (se não estiver)
source .venv/bin/activate

# Executar script de inicialização
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('Banco inicializado!')"
```

### 4.6 Testar Aplicação

```bash
# Executar servidor em modo de teste
python production.py

# Em outro terminal, testar
curl http://localhost:5003
# Deve retornar HTML da página inicial
```

---

## 5. Configuração do Supervisor

O Supervisor garante que a aplicação inicie automaticamente e reinicie em caso de falhas.

### 5.1 Criar Arquivo de Configuração

```bash
sudo nano /etc/supervisor/conf.d/gestao_editais.conf
```

Conteúdo:

```ini
[program:gestao_editais]
directory=/opt/gestao_editais/app
command=/opt/gestao_editais/app/.venv/bin/python production.py
user=gestao_app
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/gestao_editais/error.log
stdout_logfile=/var/log/gestao_editais/access.log
environment=PATH="/opt/gestao_editais/app/.venv/bin"
```

### 5.2 Criar Diretório de Logs

```bash
sudo mkdir -p /var/log/gestao_editais
sudo chown gestao_app:gestao_app /var/log/gestao_editais
```

### 5.3 Ativar e Iniciar Serviço

```bash
# Recarregar configuração do Supervisor
sudo supervisorctl reread
sudo supervisorctl update

# Iniciar serviço
sudo supervisorctl start gestao_editais

# Verificar status
sudo supervisorctl status gestao_editais
# Deve mostrar: RUNNING
```

---

## 6. Configuração do Nginx (Opcional)

Para melhor performance e segurança, recomenda-se usar Nginx como proxy reverso.

### 6.1 Configurar Virtual Host

```bash
sudo nano /etc/nginx/sites-available/gestao_editais
```

Conteúdo:

```nginx
server {
    listen 80;
    server_name gestao-editais.utfpr.edu.br;  # Ajustar conforme domínio

    # Logs
    access_log /var/log/nginx/gestao_editais_access.log;
    error_log /var/log/nginx/gestao_editais_error.log;

    # Proxy para aplicação Flask
    location / {
        proxy_pass http://127.0.0.1:5003;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Arquivos estáticos (opcional, se servidos diretamente)
    location /static {
        alias /opt/gestao_editais/app/static;
        expires 30d;
    }
}
```

### 6.2 Ativar Site

```bash
# Criar link simbólico
sudo ln -s /etc/nginx/sites-available/gestao_editais /etc/nginx/sites-enabled/

# Testar configuração
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx
```

### 6.3 Configurar HTTPS (Recomendado)

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obter certificado SSL
sudo certbot --nginx -d gestao-editais.utfpr.edu.br

# Testar renovação automática
sudo certbot renew --dry-run
```

---

## 7. Backup e Recuperação

### 7.1 Script de Backup do Banco

```bash
sudo nano /opt/gestao_editais/backup.sh
```

Conteúdo:

```bash
#!/bin/bash
BACKUP_DIR="/opt/gestao_editais/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$DATE.sql"

# Criar diretório se não existir
mkdir -p $BACKUP_DIR

# Fazer backup
pg_dump -h localhost -U gestao_editais gestao_editais_db > $BACKUP_FILE

# Comprimir
gzip $BACKUP_FILE

# Remover backups antigos (manter últimos 30 dias)
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete

echo "Backup concluído: $BACKUP_FILE.gz"
```

Tornar executável:

```bash
sudo chmod +x /opt/gestao_editais/backup.sh
```

### 7.2 Agendar Backup com Cron

```bash
# Editar crontab do usuário gestao_app
sudo crontab -u gestao_app -e
```

Adicionar linha (backup diário às 2h):

```
0 2 * * * /opt/gestao_editais/backup.sh >> /var/log/gestao_editais/backup.log 2>&1
```

### 7.3 Restaurar Backup

```bash
# Descomprimir
gunzip /opt/gestao_editais/backups/backup_YYYYMMDD_HHMMSS.sql.gz

# Restaurar
psql -h localhost -U gestao_editais gestao_editais_db < /opt/gestao_editais/backups/backup_YYYYMMDD_HHMMSS.sql
```

---

## 8. Migração de Dados Existentes

### 8.1 Exportar Dados do Ambiente Atual

Se houver dados existentes em SQLite:

```bash
# No ambiente de desenvolvimento
sqlite3 instance/gestao_editais_new.db .dump > dados_exportados.sql
```

### 8.2 Importar para PostgreSQL

```bash
# Ajustar SQL para PostgreSQL (se necessário)
# Importar
psql -h localhost -U gestao_editais -d gestao_editais_db < dados_exportados.sql
```

---

## 9. Monitoramento e Manutenção

### 9.1 Verificar Logs

```bash
# Logs da aplicação
sudo tail -f /var/log/gestao_editais/access.log
sudo tail -f /var/log/gestao_editais/error.log

# Logs do Nginx
sudo tail -f /var/log/nginx/gestao_editais_access.log
sudo tail -f /var/log/nginx/gestao_editais_error.log

# Logs do Supervisor
sudo supervisorctl tail -f gestao_editais
```

### 9.2 Reiniciar Serviço

```bash
# Reiniciar aplicação
sudo supervisorctl restart gestao_editais

# Reiniciar Nginx
sudo systemctl restart nginx
```

### 9.3 Atualizar Aplicação

```bash
# Como usuário gestao_app
sudo su - gestao_app
cd /opt/gestao_editais/app

# Fazer backup antes
cp -r . ../app_backup_$(date +%Y%m%d)

# Atualizar código
git pull origin main

# Atualizar dependências (se houver mudanças)
source .venv/bin/activate
pip install -r requirements.txt

# Reiniciar
exit  # Voltar para usuário com sudo
sudo supervisorctl restart gestao_editais
```

---

## 10. Checklist Pós-Implantação

- [ ] Aplicação acessível via navegador
- [ ] Banco de dados conectando corretamente
- [ ] Testes de CRUD (Criar, Ler, Atualizar, Excluir)
- [ ] Geração de relatórios funcionando
- [ ] Dashboard carregando corretamente
- [ ] Backup automatizado configurado
- [ ] Logs sendo gravados corretamente
- [ ] HTTPS funcionando (se configurado)
- [ ] Acesso restrito à rede UTFPR (firewall)
- [ ] Documentação entregue à equipe

---

## 11. Troubleshooting

### Aplicação não inicia

```bash
# Verificar logs
sudo supervisorctl tail gestao_editais stderr

# Verificar se porta está em uso
sudo netstat -tulpn | grep 5003

# Testar manualmente
sudo su - gestao_app
cd /opt/gestao_editais/app
source .venv/bin/activate
python production.py
```

### Erro de conexão com banco

```bash
# Verificar se PostgreSQL está rodando
sudo systemctl status postgresql

# Testar conexão manual
psql -h localhost -U gestao_editais -d gestao_editais_db

# Verificar .env
cat .env | grep DATABASE_URL
```

### Nginx não conecta à aplicação

```bash
# Verificar se aplicação está rodando
curl http://localhost:5003

# Verificar configuração Nginx
sudo nginx -t

# Ver logs
sudo tail -f /var/log/nginx/error.log
```

---

## 12. Contatos e Suporte

**Desenvolvimento:**  
Higo Santos - GitHub: [@Higo80s](https://github.com/Higo80s)

**Infraestrutura UTFPR:**  
Patrícia Strapasson Piccinini (DIRGTI/DESIS-RT)

---

**Documentação versão:** 1.0  
**Última atualização:** Janeiro 2026
