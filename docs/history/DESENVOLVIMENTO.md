# Guia de Desenvolvimento

## Estrutura do Projeto

```
gestao_editais/
├── app.py                      # Interface gráfica (Tkinter)
│   ├── Classe: ThemedTk (janela principal)
│   ├── Abas: Editais, Modalidades, Bolsistas, Acompanhamento
│   ├── ~1662 linhas
│   └── Padrão MVC: controla View + Model
│
├── db.py                       # Camada de dados
│   ├── Conexão SQLite
│   ├── Funções CRUD (Create, Read, Update, Delete)
│   ├── ~453 linhas
│   ├── Funções de Excel
│   └── Padrão Repository: centraliza acesso a dados
│
├── criar_banco.py              # Setup inicial
│   ├── Cria tabelas (editais, modalidades, bolsistas, acompanhamento)
│   ├── Define constraints e foreign keys
│   └── Roda uma vez na instalação
│
├── atualizar_banco_v2.py       # Migrações de schema
│   ├── Exemplo: adicionar coluna 'data_inicio_curso'
│   ├── Padrão: usar ALTER TABLE + error handling
│   └── Executar manualmente quando necessário
│
├── exportar_excel_mensal.py    # Automação (Task Scheduler)
│   ├── Script standalone
│   ├── Importa db module
│   ├── Gera Excel formatado
│   └── Agendado para rodar no 1º dia de cada mês
│
├── criar_agendamento.ps1/bat   # Setup Task Scheduler
│   ├── Cria tarefa agendada
│   ├── Associa python.exe ao script
│   └── Executa uma vez pelo administrador
│
├── gestao_editais.db           # Banco SQLite (gerado)
│   └── Arquivo único com todas as tabelas e dados
│
└── .venv/                      # Virtual environment
    ├── Scripts/python.exe
    ├── site-packages/ (ttkthemes, openpyxl, etc)
    └── Isolamento do ambiente
```

---

## Stack Tecnológico

**Frontend**:
- Tkinter (GUI nativa do Python)
- ttkthemes (temas modernos)
- Widgets: Treeview, Combobox, Entry, Button, etc.

**Backend**:
- SQLite3 (banco local, zero setup)
- Repository Pattern (centraliza DB)
- Parameterized queries (previne SQL injection)

**Dados**:
- Datas: ISO (YYYY-MM-DD) interno, DD/MM/YYYY UI
- Moeda: REAL no banco, formatada em UI e Excel
- Status: CHECK constraint (ativo, desligado, substituido)

**Automação**:
- openpyxl (geração Excel com formatação)
- Windows Task Scheduler (execução mensal)
- Python 3.13

---

## Convenções de Código

### Nomes
- **Tabelas**: plurais, snake_case: `editais`, `modalidades`, `bolsistas`
- **Colunas**: snake_case: `numero_edital`, `data_inicio_bolsa`
- **Funções**: snake_case: `obter_todos_editais()`, `inserir_bolsista()`
- **Variáveis**: snake_case: `referencia_mes`, `caminho_saida`
- **Classes**: PascalCase: `MainWindow`, `ExcelExporter`

### Comentários
```python
# Comentário breve em português

def funcao_importante():
    """Docstring descrevendo o quê, por quê e como usar"""
    pass
```

### Formatação
- 4 espaços de indentação
- Máximo 100 caracteres por linha
- Uma linha em branco entre funções
- Duas linhas em branco entre classes

---

## Como Adicionar Nova Funcionalidade

### Exemplo: Adicionar campo "observacoes" em Editais

#### 1. Criar arquivo de migração
`atualizar_banco_v3.py`:
```python
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'gestao_editais.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Adicionar coluna se não existir
    cursor.execute("""
        ALTER TABLE editais ADD COLUMN observacoes TEXT
    """)
    conn.commit()
    print("[OK] Coluna 'observacoes' adicionada a editais")
except sqlite3.OperationalError as e:
    if "already exists" in str(e):
        print("[SKIP] Coluna já existe")
    else:
        raise
finally:
    conn.close()
```

Executar: `python atualizar_banco_v3.py`

#### 2. Adicionar função em `db.py`
```python
def obter_edital_com_observacoes(edital_id):
    """Retorna edital com observações"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, numero_edital, data_publicacao, data_final, observacoes
        FROM editais WHERE id = ?
    """, (edital_id,))
    resultado = cursor.fetchone()
    conn.close()
    
    if resultado:
        return {
            'id': resultado[0],
            'numero_edital': resultado[1],
            'data_publicacao': resultado[2],
            'data_final': resultado[3],
            'observacoes': resultado[4]
        }
    return None
```

#### 3. Atualizar UI em `app.py`
```python
def abrir_janela_edicao_edital(self):
    # ... código existente ...
    
    # Adicionar campo de observações
    tk.Label(frame, text="Observações:").grid(row=3, column=0, sticky='w', pady=5)
    observacoes_entry = tk.Text(frame, height=3, width=40)
    observacoes_entry.grid(row=3, column=1, padx=10, pady=5)
    
    if edital_id:
        edital = db.obter_edital_com_observacoes(edital_id)
        observacoes_entry.insert('1.0', edital.get('observacoes', ''))
    
    # Ao salvar, incluir observações
    def salvar_edital():
        observacoes = observacoes_entry.get('1.0', 'end-1c')
        # ... salvar com observacoes ...
```

#### 4. Testar
```python
# Script de teste
import db

# Simule o novo campo
db.inserir_edital(
    numero="EDITAL-TEST/2025",
    data_pub="2025-12-01",
    data_final="2025-12-31",
    observacoes="Teste de observações"
)

print("Teste bem-sucedido!")
```

---

## Testes

### Manual Testing Checklist

```
[ ] Criar novo edital
    [ ] Com datas válidas
    [ ] Com número duplicado (deve rejeitar)
    
[ ] Criar modalidade
    [ ] Associada a edital existente
    [ ] Valores negativos (deve rejeitar)
    
[ ] Cadastrar bolsista
    [ ] CPF duplicado (deve rejeitar)
    [ ] Todas as datas em DD/MM/YYYY
    
[ ] Registrar acompanhamento
    [ ] Múltiplas parcelas mesmo bolsista
    [ ] Exportar Excel com dados
    
[ ] Deletar registros
    [ ] Edital (cascata deleta modal, bolsistas, acomp)
    [ ] Bolsista (deleta seu acompanhamento)
    
[ ] Ler após editar
    [ ] Valores aparecem corretos
    [ ] Datas em formato correto
```

### Como Criar Testes Unitários

Criar `test_db.py`:
```python
import unittest
import db
import os

class TestDB(unittest.TestCase):
    
    def setUp(self):
        """Rodado antes de cada teste"""
        # Usar DB temporário para testes
        self.db_path = "test_gestao_editais.db"
        # Setup DB de teste
    
    def test_inserir_edital(self):
        """Testa inserção de edital"""
        resultado = db.inserir_edital(
            "EDITAL-TEST/2025",
            "2025-12-01",
            "2025-12-31"
        )
        self.assertIsNotNone(resultado)
    
    def test_cpf_duplicado(self):
        """Testa rejeição de CPF duplicado"""
        db.inserir_bolsista(1, "123.456.789-00", ...)
        with self.assertRaises(Exception):
            db.inserir_bolsista(1, "123.456.789-00", ...)
    
    def tearDown(self):
        """Rodado após cada teste"""
        # Limpar DB de teste
        os.remove(self.db_path)

if __name__ == '__main__':
    unittest.main()
```

Executar: `python -m unittest test_db.py`

---

## Padrões e Boas Práticas

### CRUD Pattern em `db.py`

```python
# CREATE
def inserir_entidade(campo1, campo2, ...):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tabela (col1, col2) VALUES (?, ?)
    """, (campo1, campo2))
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()
    return novo_id

# READ
def obter_entidade(entidade_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tabela WHERE id = ?", (entidade_id,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado

# UPDATE
def atualizar_entidade(entidade_id, campo1, campo2):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE tabela SET col1=?, col2=? WHERE id=?
    """, (campo1, campo2, entidade_id))
    conn.commit()
    conn.close()

# DELETE
def deletar_entidade(entidade_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tabela WHERE id=?", (entidade_id,))
    conn.commit()
    conn.close()
```

### Tratamento de Erros

```python
try:
    resultado = db.inserir_bolsista(...)
    messagebox.showinfo("Sucesso", "Bolsista cadastrado!")
except sqlite3.IntegrityError as e:
    messagebox.showerror("Erro", "CPF já existe")
except Exception as e:
    messagebox.showerror("Erro", f"Algo deu errado: {str(e)}")
```

### Queries com JOIN

```python
def obter_acompanhamento_detalhado():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            e.numero_edital,
            b.nome,
            m.valor_mensal,
            a.referencia_mes,
            a.parcela
        FROM acompanhamento a
        JOIN bolsistas b ON a.bolsista_id = b.id
        JOIN editais e ON b.edital_id = e.id
        LEFT JOIN modalidades m ON e.id = m.edital_id
    """)
    resultados = cursor.fetchall()
    conn.close()
    return resultados
```

---

## Git Workflow

```bash
# Criar branch para nova feature
git checkout -b feature/nova-funcionalidade

# Fazer commits pequenos e descritivos
git commit -m "feat: adicionar campo observacoes em editais"
git commit -m "refactor: reorganizar funcoes em db.py"
git commit -m "docs: atualizar documentacao"

# Push para remoto
git push origin feature/nova-funcionalidade

# Criar Pull Request via GitHub

# Após review, fazer merge
git checkout main
git merge feature/nova-funcionalidade
git push origin main
```

### Tipos de Commit
- **feat**: Nova funcionalidade
- **fix**: Correção de bug
- **docs**: Mudança em documentação
- **refactor**: Refatoração sem mudança de comportamento
- **test**: Adição ou modificação de testes
- **chore**: Mudanças em build, dependências, etc

---

## Performance

### Otimizações Implementadas
- ✅ Parameterized queries (previne SQL injection + cache)
- ✅ Connection pooling implícito (reutiliza conexões)
- ✅ Índices implícitos em PRIMARY KEY e FOREIGN KEY
- ✅ Treeview com scroll virtual (não carrega tudo)

### Otimizações Futuras
- [ ] Adicionar índice em `cpf` e `numero_edital` (queries rápidas)
- [ ] Paginação em Treeviews muito grandes
- [ ] Cache em memória para tabelas não-mutáveis
- [ ] Análise de plano de execução (`EXPLAIN QUERY PLAN`)

### Exemplo: Adicionar índice
```python
# Em criar_banco.py ou novo arquivo atualizar_banco_v4.py
cursor.execute("CREATE INDEX IF NOT EXISTS idx_cpf ON bolsistas(cpf)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_edital_id ON bolsistas(edital_id)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_referencia ON acompanhamento(referencia_mes)")
```

---

## Deploy / Produção

### Checklist Antes de Liberar
- [ ] Todos os testes passando
- [ ] Documentação atualizada
- [ ] Sem hardcoded credentials/paths
- [ ] Backup/rollback plan pronto
- [ ] Version bump em README
- [ ] Git tags criadas

### Como Versionar
```
Versão: MAJOR.MINOR.PATCH
- 3.0.0: Exportação Excel (feature major)
- 3.1.0: Novo campo em Editais (feature minor)
- 3.0.1: Correção de bug (patch)
```

### Release Process
```bash
# Tag a versão
git tag -a v3.0.0 -m "Release versão 3.0.0 com exportação Excel"
git push origin v3.0.0

# GitHub criará automatic release
```

---

## Recursos Úteis

- [SQLite Best Practices](https://www.sqlite.org/bestpractice.html)
- [Tkinter Documentation](https://docs.python.org/3/library/tkinter.html)
- [openpyxl Documentation](https://openpyxl.readthedocs.io/)
- [Python PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [Repository Pattern](https://docs.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/infrastructure-persistence-layer-design)

---

**Última atualização**: Dezembro 2025  
**Mantido por**: Tim Couto
