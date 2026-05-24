# Guia Rápido - Gestão de Editais

## Iniciar a Aplicação

```powershell
# Abra PowerShell e execute:
cd C:\Users\SEU_USUARIO\Documents\gestao_editais
.\.venv\Scripts\Activate.ps1
python app.py
```

---

## Tarefas Comuns

### 1. Criar um novo Edital
- Aba **Editais** → Botão **Novo Edital**
- Preencha número, data publicação, data final
- Clique **Salvar**

### 2. Adicionar modalidade de bolsa
- Aba **Modalidades** → Botão **Nova Modalidade**
- Selecione edital, nível (Mestrado/Doutorado), valor mensal
- Clique **Salvar**

### 3. Cadastrar bolsista
- Aba **Bolsistas** → Botão **Novo Bolsista**
- Preencha CPF, nome, programa, campus, nível, data início
- Clique **Salvar**

### 4. Registrar pagamento mensal
- Aba **Acompanhamento** → Botão **Novo Registro**
- Selecione bolsista, mês, parcela, requisição, observações
- Clique **Salvar**

### 5. Exportar relatório em Excel
- Aba **Acompanhamento** → Botão **Exportar Excel**
- Escolha pasta para salvar
- Arquivo salvo como `acompanhamento_YYYY-MM.xlsx`

### 6. Editar registro existente
- Localize na lista
- Clique duas vezes na linha
- Janela de edição abrirá
- Modifique e clique **Salvar**

### 7. Deletar registro
- Localize na lista
- Selecione (clique uma vez)
- Clique botão **Deletar**
- Confirme exclusão

---

## Validação de Dados

| Campo | Formato | Obrigatório |
|-------|---------|------------|
| Número Edital | Texto livre | Sim (único) |
| CPF | 000.000.000-00 | Sim (único) |
| Nome | Texto | Sim |
| Data (UI) | DD/MM/YYYY | Sim |
| Valor | Número positivo | Sim |
| Email | email@dominio.com | Não |

---

## Atalhos de Teclado

| Atalho | Ação |
|--------|------|
| Ctrl+Q | Sair |
| Ctrl+N | Novo registro (em algumas abas) |
| Enter | Salvar (em diálogos) |
| Esc | Cancelar (em diálogos) |
| F5 | Atualizar lista |

---

## Automação (Excel Mensal)

### Verificar se está configurado
```powershell
schtasks /query /tn "Exportar Excel Gestao Editais" /v
```

### Testar manualmente
```powershell
cd C:\Users\SEU_USUARIO\Documents\gestao_editais
.\.venv\Scripts\python.exe exportar_excel_mensal.py
```

### Configurar (se não estiver)
```powershell
# Como Administrador:
C:\Users\SEU_USUARIO\Documents\gestao_editais\criar_agendamento.ps1
```

---

## Arquivos Importantes

| Arquivo | Descrição |
|---------|-----------|
| `app.py` | Aplicação principal (UI) |
| `db.py` | Banco de dados (funções) |
| `gestao_editais.db` | Banco SQLite (dados) |
| `exportar_excel_mensal.py` | Script para automação |
| `.venv/` | Ambiente Python isolado |

---

## Localizar Arquivos Gerados

**Excel mensal**: `C:\Users\SEU_USUARIO\Documents\gestao_editais\acompanhamento_YYYY-MM.xlsx`

**Banco de dados**: `C:\Users\SEU_USUARIO\Documents\gestao_editais\gestao_editais.db`

---

## Suporte

### Reinstalar dependências
```powershell
.\.venv\Scripts\pip.exe install -r requirements.txt
```

### Recriar banco (CUIDADO: deleta tudo!)
```powershell
# Faça backup primeiro!
del gestao_editais.db
python criar_banco.py
```

### Ver logs de erro
Erros aparecem em:
- Dialog boxes (UI)
- Console (se iniciou via terminal)
- Task Scheduler logs (se automático)

---

**Última atualização**: Dezembro 2025
