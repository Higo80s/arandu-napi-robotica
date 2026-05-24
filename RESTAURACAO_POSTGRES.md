# 🚀 Restauração e Execução - Gestão de Editais com PostgreSQL

## 📋 Pré-requisitos

### 1. PostgreSQL Instalado
- **Download:** https://www.postgresql.org/download/windows/
- **Versão recomendada:** PostgreSQL 16 ou 17
- **Durante instalação:**
  - Username: `postgres`
  - Password: `admin123` (ou o que preferir)
  - Port: `5432` (padrão)

### 2. Python 3.8+
```powershell
python --version
```

---

## 🔧 Configuração Rápida (5 minutos)

### Passo 1: Clone/Abra o repositório
```powershell
cd c:\Users\higosantos\Documents\gestao_editais\gestao_editais_novo.worktrees\copilot-worktree-2026-03-02T22-56-56
```

### Passo 2: Instale dependências Python
```powershell
pip install -r requirements.txt
```

Se tiver erro com `psycopg2`, instale a versão binária:
```powershell
pip install psycopg2-binary
```

### Passo 3: Configure o `.env` (já criado!)
O arquivo `.env` já foi criado com as configurações padrão:
```env
DATABASE_URL=postgresql://gestao_user:gestao_password@localhost:5432/gestao_editais_db
```

**Importante:** Verifique se as credenciais correspondem à sua instalação PostgreSQL.

---

## 🔄 Restaurar Backup

### Opção 1: Usar o Script Python (Recomendado)
```powershell
python restore_backup_postgres.py
```

Este script:
- ✓ Extrai o backup ZIP
- ✓ Cria o banco de dados no PostgreSQL
- ✓ Restaura todos os dados
- ✓ Verifica integridade

### Opção 2: Usar o Launcher Automático (Windows)
```powershell
.\launch_with_postgres.bat
```

Este arquivo:
- ✓ Inicia PostgreSQL (se não estiver rodando)
- ✓ Verifica e restaura backup
- ✓ Instala dependências
- ✓ Inicia a aplicação

---

## 🌐 Rodar a Aplicação

### Opção 1: Launcher (Mais fácil)
```powershell
.\launch_with_postgres.bat
```

### Opção 2: Manual com PowerShell
```powershell
# 1. Inicie PostgreSQL (se necessário)
# Services > PostgreSQL > Start

# 2. Instale dependências
pip install -r requirements.txt

# 3. Configure o .env (já feito)

# 4. Rode a app
python app.py
```

### Opção 3: Com Docker (Alternativa)
```powershell
# Se tiver Docker instalado
docker-compose up
```

---

## 📊 Verificar Status

### Verificar PostgreSQL rodando
```powershell
# Windows PowerShell
Get-Process postgres

# Ou via tasklist
tasklist | findstr postgres
```

### Conectar ao banco com psql
```powershell
# Template
psql -h localhost -p 5432 -U gestao_user -d gestao_editais_db

# Digite a senha quando solicitado
```

### Verificar tabelas
```sql
-- Dentro do psql
\dt                    -- Lista todas as tabelas
SELECT COUNT(*) FROM editais;          -- Conta de editais
SELECT COUNT(*) FROM bolsistas;        -- Conta de bolsistas
\q                     -- Sair
```

---

## 🌍 Acessar Aplicação

Após iniciar, abra no navegador:
```
http://localhost:5000
```

**Credenciais padrão** (após restauração):
- Email: `admin@example.com`
- Senha: (verificar no banco ou criar novo usuário)

---

## 🐛 Troubleshooting

### Erro: "psycopg2.OperationalError: could not connect to server"
```
Solução:
1. Verifique se PostgreSQL está rodando
   → net start postgresql-x64-17
2. Verifique credenciais em .env
3. Verifique porta 5432 aberta
```

### Erro: "pg_restore not found"
```
Solução:
1. Instale PostgreSQL (inclui pg_restore)
2. Adicione ao PATH:
   → C:\Program Files\PostgreSQL\17\bin
3. Ou edite restore_backup_postgres.py com caminho correto
```

### Erro: "database gestao_editais_db does not exist"
```
Solução:
1. Execute: python restore_backup_postgres.py
2. Verifique arquivo backup_pre_auth_20260129_010726.zip existe
```

### Erro: "permission denied"
```
Solução:
1. Verifique permissões da pasta
2. Execute como Administrador:
   → Clique direito em PowerShell > "Run as administrator"
```

---

## 📁 Estrutura de Arquivos Criados

```
.
├── .env                              # ✓ Configuração (criado)
├── restore_backup_postgres.py        # ✓ Script de restauração (criado)
├── launch_with_postgres.bat          # ✓ Launcher automático (criado)
├── RESTAURACAO_POSTGRES.md           # ✓ Este arquivo (criado)
├── backup_pre_auth_20260129_010726.zip  # Seu backup
├── app.py                            # App principal
├── models.py                         # Modelos SQLAlchemy
├── requirements.txt                  # Dependências
└── instance/                         # Pasta de dados (local)
```

---

## ⚙️ Configuração Avançada

### Mudar credenciais PostgreSQL
Edite `.env`:
```env
DATABASE_URL=postgresql://seu_usuario:sua_senha@localhost:5432/seu_database
DB_HOST=seu_host
DB_PORT=seu_port
```

### Usar Docker Compose (Recomendado para produção)
```powershell
docker-compose up -d

# Verificar se rodou
docker ps

# Ver logs
docker-compose logs -f web

# Parar
docker-compose down
```

### Integrar com Waitress (Produção)
```powershell
pip install waitress
waitress-serve --port=5000 app:app
```

---

## 📝 Notas Importantes

1. **Segurança:** Mude a `SECRET_KEY` em produção!
2. **Backup:** Configure backup automático em `scripts/backup_postgres.py`
3. **Logs:** Verifique logs em `logs/` para diagnóstico
4. **Performance:** PostgreSQL é mais rápido que SQLite para grandes volumes

---

## 🎯 Próximos Passos

- [ ] Restaurar backup com sucesso
- [ ] Acessar http://localhost:5000
- [ ] Verificar dados restaurados
- [ ] Criar novo usuário admin (se necessário)
- [ ] Configurar autenticação LDAP/SAML (se necessário)
- [ ] Setup de backups automáticos

---

**Dúvidas?** Verifique os logs ou use:
```powershell
python restore_backup_postgres.py --help
```

**Última atualização:** 2026-03-02
