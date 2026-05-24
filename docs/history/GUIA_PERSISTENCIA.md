# Guia: Problema de Persistência - Editais Não Salvam

## 🐛 Problema Relatado

> "Quando fui cadastrar um edital, ele aparecia nas demais abas, porém ao sair do programa e abrir novamente, as informações não foram salvas."

## 🔍 Raiz do Problema

O código estava **correto**, mas havia um **problema de caminhos de banco de dados**:

### Múltiplos Caminhos de Banco

Alguns scripts usavam **caminhos relativos** e outros **caminhos absolutos**:

| Arquivo | Caminho | Tipo |
|---------|---------|------|
| `app.py` | `os.path.join(os.path.dirname(__file__), 'gestao_editais.db')` | ✅ Absoluto |
| `db.py` | `os.path.join(os.path.dirname(__file__), 'gestao_editais.db')` | ✅ Absoluto |
| `criar_banco.py` *(anterior)* | `'gestao_editais.db'` | ❌ Relativo |
| `test_*.py` *(anterior)* | `'gestao_editais.db'` | ❌ Relativo |

### Cenário que Causa o Bug

Se você executasse comandos assim:
```bash
# Terminal aberto em C:\
C:\ python Documents\gestao_editais\criar_banco.py
# Cria banco em: C:\gestao_editais.db ❌

# Depois, abrir o programa
C:\Users\higosantos\Documents\gestao_editais> python app.py
# Usa banco em: C:\Users\higosantos\Documents\gestao_editais\gestao_editais.db ❌
```

Resultado: **Dois bancos diferentes!** Os dados salvos em um não aparecem no outro.

## ✅ Solução Implementada

Todos os scripts foram atualizados para usar **caminho absoluto baseado no arquivo**:

```python
import os

# Antes ❌
conn = sqlite3.connect('gestao_editais.db')

# Depois ✅
db_path = os.path.join(os.path.dirname(__file__), 'gestao_editais.db')
conn = sqlite3.connect(db_path)
```

### Arquivos Corrigidos
- ✅ `criar_banco.py`
- ✅ `test_persistence.py`
- ✅ `test_save.py`
- ✅ `test_tryagain.py`

### Nota adicional
O aplicativo agora garante o schema do banco automaticamente ao iniciar. Foi adicionada em `db.py` a função
`ensure_db_schema()` que executa os `CREATE TABLE IF NOT EXISTS` necessários. `app.py` chama essa função
no startup, então mesmo que o `gestao_editais.db` esteja ausente ou falte alguma tabela, o aplicativo irá
criar as tabelas necessárias automaticamente.
## 🚀 Como Usar Corretamente

### 1️⃣ Criar o Banco (primeira vez)
```bash
cd C:\Users\higosantos\Documents\gestao_editais
python criar_banco.py
```

### 2️⃣ Rodar a Aplicação
```bash
cd C:\Users\higosantos\Documents\gestao_editais
python app.py
```

### 3️⃣ Ou, Usar a Versão Compilada
```bash
cd C:\Users\higosantos\Documents\gestao_editais
.\dist\GestaoEditais.exe
```

## 🛡️ Regra de Ouro

**Sempre execute scripts do diretório do projeto ou use caminhos absolutos!**

```bash
# ✅ CORRETO
cd C:\Users\higosantos\Documents\gestao_editais
python app.py

# ❌ EVITAR
cd C:\
python gestao_editais\app.py
```

## 📋 Verificação

Se você quer verificar que os dados estão sendo salvos corretamente:

```bash
cd C:\Users\higosantos\Documents\gestao_editais
python test_persistence.py
```

**Saída esperada:**
```
=== Teste 1: Inserir Novo Edital ===
Edital criado com ID: X
Número: TEST-PERSIST-...

=== Teste 2: Verificar Persistência (imediatamente) ===
✓ Edital ENCONTRADO no banco: ID=X, Número=...

=== Teste 3: Listar Todos os Editais ===
  - ID=1: 14/2025
  - ID=2: TEST-001/2025
  - ...
```

## 📝 Resumo

| Item | Status |
|------|--------|
| Banco persistindo dados | ✅ Funciona |
| App carregando dados ao iniciar | ✅ Funciona |
| Caminhos padronizados | ✅ Corrigido |
| Múltiplos bancos | ✅ Eliminado |
