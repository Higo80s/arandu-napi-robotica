# Documentação Completa - Gestão de Editais

## Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura do Sistema](#arquitetura-do-sistema)
3. [Guia de Instalação](#guia-de-instalação)
4. [Guia de Uso](#guia-de-uso)
5. [Estrutura do Banco de Dados](#estrutura-do-banco-de-dados)
6. [API de Funções](#api-de-funções)
7. [Automação e Agendamento](#automação-e-agendamento)
8. [Troubleshooting](#troubleshooting)

---

## Visão Geral

**Gestão de Editais** é uma aplicação desktop para gerenciar:
- **Editais (Chamadas de Pesquisa)**: Registro de número, data de publicação, data final
- **Modalidades**: Tipos de bolsa por edital (mestrado, doutorado, etc.) com valores mensais
- **Bolsistas**: Dados de pesquisadores em bolsa (CPF, nome, programa, data de início)
- **Acompanhamento Mensal**: Rastreamento mensal de cada bolsa (parcelas pagas, observações)

**Tecnologia**:
- **Frontend**: Tkinter + ttkthemes (interface desktop com tema escuro)
- **Backend**: SQLite3 (banco de dados local)
- **Automação**: Windows Task Scheduler (Excel mensal automático)
- **Linguagem**: Python 3.13
- **Versão**: 3.0 (com exportação Excel)

---

## Arquitetura do Sistema

```
gestao_editais/
├── app.py                      # Interface gráfica Tkinter (1662 linhas)
├── db.py                       # Camada de dados (453 linhas)
├── criar_banco.py              # Script de criação do DB
├── atualizar_banco_v2.py       # Migrações de schema
├── exportar_excel_mensal.py    # Script para Task Scheduler
├── criar_agendamento.ps1       # Setup de automação (PowerShell)
├── criar_agendamento.bat       # Setup de automação (batch)
├── gestao_editais.db           # Banco SQLite (gerado na primeira execução)
└── .venv/                      ## 1. Visão Geral
O sistema gerencia o ciclo de vida de editais e bolsas da PROPPG.

## 2. Arquitetura
O sistema utiliza o padrão MVC (Model-View-Controller) com Flask Blueprints para modularidade.

### Banco de Dados
- **Produção**: PostgreSQL
- **Desenvolvimento**: SQLite
- **Models**: Definidos em `models.py` usando SQLAlchemy ORM.

## 3. Funcionalidades Principais
- **Gestão de Editais**: Criação, edição e acompanhamento.
- **Bolsistas**: Cadastro, vigência e pagamentos.
- **Programas Acadêmicos**:
    - Suporte a Acadêmico e Profissional via campo `tipo_oferta`.
    - Distinção clara entre Pós-Graduação e Graduação.
    - Suporte a Multicampi.
```

### Padrões Arquiteturais

**MVC (Model-View-Controller)**:
- **Model**: `db.py` - Todas operações de DB via funções
- **View**: `app.py` - Interface gráfica Tkinter
- **Controller**: `app.py` - Lógica de interação entre View e Model

**Repository Pattern**:
- Todas funções de DB centralizadas em `db.py`
- Facilita testes, manutenção e migração futura

---

## Guia de Instalação

### Requisitos Mínimos
- Windows 7 ou superior
- Python 3.8+
- ~50 MB de espaço em disco

### Passo 1: Clonar ou Baixar o Projeto
```powershell
cd C:\Users\SEU_USUARIO\Documents
git clone <url-do-repositorio> gestao_editais
cd gestao_editais
```

### Passo 2: Criar Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Passo 3: Instalar Dependências
```powershell
pip install ttkthemes python-dateutil openpyxl
```

### Passo 4: Criar Banco de Dados
```powershell
python criar_banco.py
```

Saída esperada:
```
Criando banco de dados...
Tabela 'editais' criada
Tabela 'modalidades' criada
Tabela 'bolsistas' criada
Tabela 'acompanhamento' criada
Banco criado com sucesso em: C:\...\gestao_editais.db
```

### Passo 5: Iniciar a Aplicação
```powershell
python app.py
```

---

## Guia de Uso

### Fluxo Principal

#### 1. Criar um Edital
1. Abra a aba **"Editais"**
2. Clique em **"Novo Edital"**
3. Preencha:
   - Número do Edital: `Ex: EDITAL-001/2025`
   - Data de Publicação: `01/12/2025`
   - Data Final: `31/12/2025`
4. Clique **"Salvar"**

#### 2. Criar Modalidades de Bolsa
1. Vá para aba **"Modalidades"**
2. Clique **"Nova Modalidade"**
3. Selecione o Edital criado
4. Preencha:
   - Nível: `Mestrado`, `Doutorado`, etc.
   - Valor Mensal: `1.500,00`
5. Clique **"Salvar"**

#### 3. Cadastrar Bolsistas
1. Aba **"Bolsistas"**
2. Clique **"Novo Bolsista"**
3. Preencha dados:
   - CPF: `123.456.789-00`
   - Nome: `João Silva`
   - Programa: `Engenharia de Sistemas`
   - Campus: `Campus Centro`
   - Nível: `Mestrado`
   - Data de Início: `01/09/2025`
4. Clique **"Salvar"**

#### 4. Registrar Acompanhamento Mensal
1. Aba **"Acompanhamento"**
2. Clique **"Novo Registro"**
3. Preencha:
   - Bolsista: `(selecione na lista)`
   - Referência (Mês): `2025-12`
   - Parcela: `1`
   - Requisição Pagamento: `REQ-001/2025`
   - Observações: `Pagamento realizado`
4. Clique **"Salvar"**

#### 5. Gerar Relatório Excel
1. Aba **"Acompanhamento"**
2. Clique **"Exportar Excel"**
3. Escolha pasta para salvar
4. Arquivo será gerado: `acompanhamento_YYYY-MM.xlsx`

---

## Estrutura do Banco de Dados

### Tabela: editais
```sql
CREATE TABLE editais (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_edital TEXT NOT NULL UNIQUE,
    data_publicacao TEXT NOT NULL,
    data_final TEXT NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
**Campos**:
- `id`: Identificador único
- `numero_edital`: Ex: "EDITAL-001/2025" (não pode repetir)
- `data_publicacao`: ISO format (YYYY-MM-DD)
- `data_final`: ISO format (YYYY-MM-DD)

### Tabela: modalidades
```sql
CREATE TABLE modalidades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    edital_id INTEGER NOT NULL FOREIGN KEY,
    nivel TEXT NOT NULL,
    valor_mensal REAL NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (edital_id) REFERENCES editais(id) ON DELETE CASCADE
);
```
**Campos**:
- `edital_id`: Referência ao edital
- `nivel`: "Mestrado", "Doutorado", "Pós-Doc", etc.
- `valor_mensal`: Valor em reais (Ex: 1500.00)

### Tabela: bolsistas
```sql
CREATE TABLE bolsistas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    edital_id INTEGER NOT NULL FOREIGN KEY,
    cpf TEXT NOT NULL UNIQUE,
    nome TEXT NOT NULL,
    programa TEXT,
    campus TEXT,
    nivel TEXT NOT NULL,
    data_inicio_bolsa TEXT NOT NULL,
    status TEXT DEFAULT 'ativo' CHECK(status IN ('ativo','desligado','substituido')),
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (edital_id) REFERENCES editais(id) ON DELETE CASCADE
);
```
**Campos**:
- `cpf`: Formato: 123.456.789-00 (UNIQUE)
- `status`: Pode ser 'ativo', 'desligado', ou 'substituido'
- `data_inicio_bolsa`: ISO format (YYYY-MM-DD)

### Tabela: acompanhamento
```sql
CREATE TABLE acompanhamento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bolsista_id INTEGER NOT NULL FOREIGN KEY,
    referencia_mes TEXT NOT NULL,
    parcela INTEGER NOT NULL,
    requisicao_pagamento TEXT,
    observacoes TEXT,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bolsista_id) REFERENCES bolsistas(id) ON DELETE CASCADE
);
```
**Campos**:
- `referencia_mes`: Formato YYYY-MM (Ex: "2025-12")
- `parcela`: Número da parcela (1, 2, 3...)
- `requisicao_pagamento`: Número do processo/requisição
- `observacoes`: Notas livres sobre a parcela

---

## API de Funções

### Funções em `db.py`

#### Editais
```python
def obter_todos_editais()
    # Retorna lista de dicts com todos editais

def obter_edital_por_numero(numero_edital: str)
    # Retorna edital específico ou None

def inserir_edital(numero, data_pub, data_final)
    # Cria novo edital, retorna ID

def deletar_edital(edital_id)
    # Remove edital (cascata deleta modalidades, bolsistas, acompanhamento)
```

#### Bolsistas
```python
def obter_bolsistas_por_edital(edital_id)
    # Retorna lista de bolsistas do edital

def obter_bolsista(bolsista_id)
    # Retorna dados completos de 1 bolsista

def inserir_bolsista(edital_id, cpf, nome, programa, campus, nivel, data_inicio)
    # Cria novo bolsista, retorna ID

def atualizar_bolsista(bolsista_id, ...)
    # Atualiza dados do bolsista

def deletar_bolsista(bolsista_id)
    # Remove bolsista e seu acompanhamento
```

#### Acompanhamento
```python
def obter_acompanhamento(referencia_mes=None)
    # Retorna acompanhamento com JOIN de todas tabelas

def inserir_acompanhamento(bolsista_id, referencia_mes, parcela, requisicao, obs)
    # Registra nova parcela de bolsa

def atualizar_acompanhamento(acompanhamento_id, ...)
    # Atualiza registro de acompanhamento

def deletar_acompanhamento(acompanhamento_id)
    # Remove registro
```

#### Excel
```python
def exportar_acompanhamento_para_excel(referencia_mes=None, caminho_saida=None)
    # Gera arquivo .xlsx com formatação profissional
    # Se referencia_mes=None, exporta mês atual
    # Se caminho_saida=None, salva em pasta padrão
    # Retorna caminho do arquivo gerado

def exportar_acompanhamento_mensal_automatico()
    # Wrapper para Task Scheduler - usa mês anterior
    # Retorna caminho do arquivo ou None
```

---

## Automação e Agendamento

### Configurar Exportação Automática (Windows Task Scheduler)

#### Opção 1: PowerShell (Recomendado)
```powershell
# Abra PowerShell como Administrador
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
C:\Users\SEU_USUARIO\Documents\gestao_editais\criar_agendamento.ps1
```

#### Opção 2: Arquivo Batch
```
1. Clique direito em criar_agendamento.bat
2. Selecione "Executar como administrador"
```

#### Opção 3: Manual (GUI)
```
1. Pressione Win+R
2. Digite: taskschd.msc
3. Clique "Criar Tarefa Básica..."
4. Nome: "Exportar Excel Gestao Editais"
5. Gatilho: Mensal, dia 1º, 10:00 AM
6. Ação: 
   - Programa: C:\Users\SEU_USUARIO\Documents\gestao_editais\.venv\Scripts\python.exe
   - Argumentos: C:\Users\SEU_USUARIO\Documents\gestao_editais\exportar_excel_mensal.py
   - Iniciar em: C:\Users\SEU_USUARIO\Documents\gestao_editais
```

### Verificar se está Agendado
```powershell
schtasks /query /tn "Exportar Excel Gestao Editais" /v
```

### Testar Manualmente
```powershell
cd C:\Users\SEU_USUARIO\Documents\gestao_editais
.\.venv\Scripts\python.exe exportar_excel_mensal.py
```

### Arquivos Gerados Automaticamente
Os arquivos Excel são salvos em:
```
C:\Users\SEU_USUARIO\Documents\gestao_editais\acompanhamento_YYYY-MM.xlsx
```

---

## Troubleshooting

### Problema: "ModuleNotFoundError: No module named 'ttkthemes'"
**Solução**:
```powershell
.\.venv\Scripts\pip.exe install ttkthemes
```

### Problema: "Banco de dados bloqueado"
**Causa**: Aplicação aberta em outro processo
**Solução**:
- Feche todos os processos Python: `taskkill /im python.exe /f`
- Ou reinicie o computador

### Problema: Datas em formato errado
**Nota**: O sistema interno usa ISO (YYYY-MM-DD)
- UI aceita e mostra em DD/MM/YYYY
- Banco armazena em YYYY-MM-DD
- Excel exporta em DD/MM/YYYY

### Problema: Excel não abre ou está corrompido
**Solução**:
- Verifique espaço em disco (>50 MB)
- Reinstale openpyxl: `pip install --upgrade openpyxl`
- Regenere o arquivo manualmente via UI

### Problema: Task Scheduler não executa
**Verificar**:
```powershell
# Ver último resultado da tarefa
schtasks /query /tn "Exportar Excel Gestao Editais" /v /fo list
```

**Possíveis causas**:
- Computador desligado no dia 1º do mês
- Permissões insuficientes (execute como Administrador)
- Caminho do Python incorreto (verifique em: `.venv\Scripts\python.exe`)

---

## Conversão de Datas

O sistema usa funções internas para conversão:

```python
def converter_data_br_para_iso(data_br: str) -> str:
    """Converte DD/MM/YYYY para YYYY-MM-DD"""
    return datetime.strptime(data_br, "%d/%m/%Y").strftime("%Y-%m-%d")

def converter_data_iso_para_br(data_iso: str) -> str:
    """Converte YYYY-MM-DD para DD/MM/YYYY"""
    return datetime.strptime(data_iso, "%Y-%m-%d").strftime("%d/%m/%Y")
```

---

## Formato Excel Exportado

### Colunas (A-N)
1. **Edital**: Número do edital
2. **SEI**: Processo (campo "requisicao_pagamento")
3. **CPF**: CPF do bolsista
4. **Nome**: Nome completo
5. **Programa**: Programa de pesquisa
6. **Campus**: Campus onde atua
7. **Nível**: Nível da bolsa
8. **Valor**: Valor mensal formatado (R$ X.XXX,XX)
9. **Início Bolsa**: Data início (DD/MM/YYYY)
10. **Referência**: Mês (MM/YYYY)
11. **Parcela**: Número da parcela
12. **Requisição**: Número de requisição
13. **Observações**: Notas
14. **Data Criação**: Quando foi registrado

### Formatação
- **Header**: Azul (366092) com texto branco e negrito
- **Bordas**: Todas as células com borda fina preta
- **Alinhamento**: Centralizado, com quebra de linha onde necessário
- **Moeda**: Coluna "Valor" formatada em R$ com 2 casas decimais
- **Largura**: Auto-ajustada por coluna (máx 50)

---

## Referências

- [Python 3.13 Docs](https://docs.python.org/3/)
- [Tkinter Docs](https://docs.python.org/3/library/tkinter.html)
- [SQLite3 Docs](https://www.sqlite.org/docs.html)
- [openpyxl Docs](https://openpyxl.readthedocs.io/)
- [Windows Task Scheduler](https://docs.microsoft.com/en-us/windows/win32/taskschd/task-scheduler-start-page)

---

**Versão**: 3.0 | **Data**: Dezembro 2025 | **Mantido por**: Tim
