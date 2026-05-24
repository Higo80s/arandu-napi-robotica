# Guia Completo de Deploy no PythonAnywhere

## 📋 Pré-requisitos

- Conta no PythonAnywhere (gratuita ou paga)
- Projeto no GitHub atualizado
- Email verificado no PythonAnywhere

## 🚀 Passo a Passo Detalhado

### Etapa 1: Criar Conta no PythonAnywhere

1. Acesse: https://www.pythonanywhere.com
2. Clique em "Pricing & Signup"
3. Escolha plano:
   - **Beginner (Gratuito)**: Ideal para teste e pequeno uso
   - **Hacker ($5/mês)**: Mais recursos e domínio próprio

4. Crie sua conta e verifique email

### Etapa 2: Configurar Ambiente

#### 2.1 Abrir Console Bash

1. Faça login no PythonAnywhere
2. Vá para aba "Consoles"
3. Clique em "Bash"

#### 2.2 Clone o Repositório

```bash
# Navegar para home
cd ~

# Clonar repositório
git clone https://github.com/Higo80s/gestao_editais.git

# Entrar no diretório
cd gestao_editais
```

#### 2.3 Criar Ambiente Virtual

```bash
# Criar virtualenv (Python 3.10 no PythonAnywhere Free)
mkvirtualenv --python=/usr/bin/python3.10 gestao-editais

# O ambiente será ativado automaticamente
# Para ativar manualmente no futuro:
workon gestao-editais
```

#### 2.4 Instalar Dependências

```bash
# Instalar todas as dependências
pip install -r requirements.txt

# Verificar instalação
pip list
```

### Etapa 3: Configurar Web App

#### 3.1 Criar Nova Web App

1. Vá para aba "Web"
2. Clique em "Add a new web app"
3. Escolha seu domínio: `seuusername.pythonanywhere.com`
4. Selecione "Manual configuration" (não Flask)
5. Escolha "Python 3.10"

#### 3.2 Configurar WSGI File

1. Na aba "Web", seção "Code"
2. Clique no link do arquivo WSGI (algo como `/var/www/seuusername_pythonanywhere_com_wsgi.py`)
3. Substitua TODO o conteúdo por:

```python
"""
WSGI config for gestao_editais project.
"""
import sys
import os

# Path do projeto
project_home = '/home/seuusername/gestao_editais'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Variáveis de ambiente
os.environ['FLASK_ENV'] = 'production'

# Importar aplicação Flask
from app import app as application

# Inicializar banco de dados na primeira execução
with application.app_context():
    from models import db
    db.create_all()
    print("Database initialized!")
```

**⚠️ IMPORTANTE:** Substitua `seuusername` pelo seu username do PythonAnywhere!

4. Clique em "Save"

#### 3.3 Configurar Virtualenv

1. Ainda na aba "Web"
2. Encontre seção "Virtualenv"
3. Clique em "Enter path to a virtualenv"
4. Digite:

```
/home/seuusername/.virtualenvs/gestao-editais
```

5. Clique no ícone de confirmação (✓)

#### 3.4 Configurar Arquivos Estáticos

Na seção "Static files", adicione:

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/seuusername/gestao_editais/static/` |

Clique em "Save"

#### 3.5 Reload da Aplicação

1. Role até o topo da página
2. Clique no grande botão verde **"Reload seuusername.pythonanywhere.com"**
3. Aguarde alguns segundos

### Etapa 4: Testar Aplicação

1. Clique no link: `https://seuusername.pythonanywhere.com`
2. A aplicação deve carregar!

### Etapa 5: Resolver Problemas Comuns

#### Erro 500: Internal Server Error

**Solução 1: Verificar Logs**

```bash
# No console Bash
cd ~
cat /var/log/seuusername.pythonanywhere.com.error.log
```

**Solução 2: Verificar WSGI**

- Certifique-se que o path em `project_home` está correto
- Verifique se importações estão corretas

**Solução 3: Dependências**

```bash
workon gestao-editais
pip install -r requirements.txt --upgrade
```

#### Erro: Virtualenv não encontrado

```bash
# Verificar virtualenvs existentes
lsvirtualenv

# Recriar se necessário
mkvirtualenv --python=/usr/bin/python3.10 gestao-editais
pip install -r ~/gestao_editais/requirements.txt
```

#### CSS/JS não carregando

1. Verifique seção "Static files"
2. Confirme que path está correto
3. Faça reload da aplicação

### Etapa 6: Configurações Avançadas (Opcional)

#### 6.1 Usar PostgreSQL (Plano Pago)

```bash
# No console Bash
pip install psycopg2-binary

# Em app.py, alterar:
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:pass@localhost/dbname'
```

#### 6.2 Configurar HTTPS (Já incluído)

PythonAnywhere fornece HTTPS automaticamente!

#### 6.3 Agendar Tasks (Cron Jobs)

Na aba "Tasks", você pode agendar scripts Python:

```python
# backup_daily.py
import shutil
from datetime import datetime

source = '/home/seuusername/gestao_editais/instance/gestao_editais_new.db'
backup = f'/home/seuusername/backups/backup_{datetime.now().strftime("%Y%m%d")}.db'

shutil.copy2(source, backup)
print(f"Backup criado: {backup}")
```

Agendar para rodar diariamente às 2h AM.

#### 6.4 Configurar Domínio Próprio (Plano Pago)

1. Aba "Web" → "Add a new web app"
2. Digite seu domínio
3. Siga instruções de DNS

### Etapa 7: Atualizar Aplicação

Quando fizer mudanças no código:

```bash
# No console Bash
cd ~/gestao_editais

# Puxar atualizações do GitHub
git pull origin main

# Reativar virtualenv
workon gestao-editais

# Atualizar dependências (se necessário)
pip install -r requirements.txt --upgrade

# Fazer migrations (se houver)
python migrate_v2.py
```

Depois, na aba "Web", clique em **"Reload"**.

### Etapa 8: Monitoramento

#### Verificar Logs em Tempo Real

```bash
# Console Bash
tail -f /var/log/seuusername.pythonanywhere.com.error.log
```

#### Verificar Uso de Recursos

1. Aba "Account"
2. Veja CPU seconds utilizados
3. Plano gratuito tem limite de 100 CPU seconds/dia

## 📊 Comparação de Planos

| Recurso | Beginner (Free) | Hacker ($5/mês) |
|---------|----------------|-----------------|
| CPU/dia | 100 seconds | Ilimitado |
| Apps | 1 | Ilimitado |
| Storage | 512MB | 1GB |
| PostgreSQL | ❌ | ✅ |
| Domínio próprio | ❌ | ✅ |
| Always-on | ❌ | ✅ |

## 🔒 Segurança

### Alterar Secret Key

```python
# app.py
import secrets

app.config['SECRET_KEY'] = secrets.token_hex(32)
```

### Ocultar Informações Sensíveis

Crie arquivo `.env` (não commitar):

```env
SECRET_KEY=sua-chave-super-secreta
DATABASE_URL=postgresql://...
```

Instale python-dotenv:

```bash
pip install python-dotenv
```

Em `app.py`:

```python
from dotenv import load_dotenv
import os

load_dotenv()

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
```

## 📞 Suporte

**Problemas?**

1. Verifique logs de erro
2. Consulte [PythonAnywhere Help](https://help.pythonanywhere.com/)
3. Abra issue no GitHub
4. Fórum PythonAnywhere: https://www.pythonanywhere.com/forums/

## 🎉 Pronto!

Sua aplicação está no ar! 🚀

URL: **https://seuusername.pythonanywhere.com**

---

**Desenvolvido com ❤️ para facilitar deploy Flask no PythonAnywhere**
