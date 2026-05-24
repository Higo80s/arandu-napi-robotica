# 📊 Guia: Exportação de Excel Mensal

## O Que Foi Adicionado

O sistema agora pode **gerar arquivos Excel profissionais** mensalmente com os dados de acompanhamento de bolsas.

```
Antes: Apenas CSV simples (sem formatação)
Depois: Excel formatado + automação mensal
```

---

## ✨ Características do Excel Exportado

✅ **Headers profissionais** (azul escuro, texto branco, negrito)  
✅ **Valores monetários formatados** (R$ 1.500,00)  
✅ **Bordas em todas as células**  
✅ **Colunas ajustadas automaticamente**  
✅ **Alinhamento correto** (texto à esquerda, valores à direita)  
✅ **Data e hora na primeira linha**  
✅ **Arquivo nomeado por mês** (acompanhamento_2025-12.xlsx)  

---

## 🎯 Como Usar (Manual)

### Opção 1: Via Interface (Aba Acompanhamento)

1. **Abra a aplicação:**
   ```powershell
   python app.py
   ```

2. **Clique na aba "Acompanhamento"**

3. **Clique no botão "Exportar Excel"**
   ```
   [Preencher mês atual] [Registrar requisição] [Exportar CSV] [Exportar Excel]
                                                                         ↑
                                                                    Novo botão
   ```

4. **Escolha a pasta onde salvar**

5. **Pronto!** Arquivo `acompanhamento_YYYY-MM.xlsx` será gerado

### Opção 2: Script Python (sem UI)

Execute o script diretamente:

```powershell
cd C:\Users\higosantos\Documents\gestao_editais
python exportar_excel_mensal.py
```

**Saída:**
```
============================================================
EXPORTAÇÃO MENSAL DE ACOMPANHAMENTO EM EXCEL
============================================================
[OK] Exportação concluída com sucesso!
    Referência: 2025-12
    Registros: 3
    Arquivo: C:\Users\higosantos\Documents\gestao_editais\acompanhamento_2025-12.xlsx
============================================================
Data/Hora: 09/12/2025 15:30:00
============================================================
```

---

## 🤖 Como Automatizar (Task Scheduler)

### Cenário: Gerar Excel automaticamente no 1º do mês às 10:00 AM

#### Método 1: GUI do Agendador (Recomendado)

1. **Abra Agendador de Tarefas:**
   ```powershell
   tasksched.msc
   # Ou: Win + R → taskschd.msc → Enter
   ```

2. **Painel direito → Criar Tarefa**

3. **Aba Geral:**
   - Nome: `Gestão de Editais - Excel Mensal`
   - Marque: `Executar com privilégios mais altos`

4. **Aba Gatilhos → Novo:**
   - Tipo: `Mensal`
   - Dia: `1` (primeiro dia)
   - Hora: `10:00:00` (ou preferida)
   - Marque: `Habilitado`

5. **Aba Ações → Novo:**
   - Programa/script:
     ```
     C:\Users\higosantos\Documents\gestao_editais\.venv\Scripts\python.exe
     ```
   - Argumentos:
     ```
     C:\Users\higosantos\Documents\gestao_editais\exportar_excel_mensal.py
     ```
   - Iniciar em:
     ```
     C:\Users\higosantos\Documents\gestao_editais
     ```

6. **OK**

#### Método 2: PowerShell (Script)

Cole e execute no PowerShell (como Admin):

```powershell
# Criar ação
$Action = New-ScheduledTaskAction `
    -Execute "C:\Users\higosantos\Documents\gestao_editais\.venv\Scripts\python.exe" `
    -Argument "C:\Users\higosantos\Documents\gestao_editais\exportar_excel_mensal.py" `
    -WorkingDirectory "C:\Users\higosantos\Documents\gestao_editais"

# Criar trigger (1º do mês às 10:00)
$Trigger = New-ScheduledTaskTrigger -Monthly -DaysOfMonth 1 -At 10:00AM

# Registrar tarefa
Register-ScheduledTask `
    -TaskName "Gestão de Editais - Excel Mensal" `
    -Action $Action `
    -Trigger $Trigger `
    -Description "Exporta acompanhamento em Excel automaticamente" `
    -RunLevel Highest
```

---

## 📋 Estrutura do Excel Gerado

Exemplo de arquivo gerado: `acompanhamento_2025-12.xlsx`

```
┌─────────┬──────────┬─────────────────┬──────────┬───────────────┐
│ Edital  │ SEI      │ CPF             │ Nome     │ ... (10+ cols)│
├─────────┼──────────┼─────────────────┼──────────┼───────────────┤
│CAPES... │ 25640... │ 123.456.789-00  │ João S.  │               │
│         │          │                 │          │               │
├─────────┼──────────┼─────────────────┼──────────┼───────────────┤
│CNPq...  │ 51649... │ 234.567.890-11  │ Maria S. │               │
│         │          │                 │          │               │
└─────────┴──────────┴─────────────────┴──────────┴───────────────┘

Colunas incluídas:
1. Edital
2. SEI
3. CPF
4. Nome
5. Programa (curso)
6. Campus
7. Nível (mestrado, doutorado)
8. Valor Mensal (formatado como R$)
9. Início da Bolsa (data)
10. Referência (mês)
11. Parcela (número)
12. Nº Requisição (SEI do pagamento)
13. Observações
14. Data Criação (timestamp)
```

---

## 🔄 Fluxo Completo: Um Mês Inteiro

### 1º de dezembro (06:00 AM)
```
Task Scheduler dispara prefill_acompanhamento.py
  └─ Cria registros para bolsistas ativos
  └─ Exemplo: João Silva, parcela 1
```

### Ao longo de dezembro
```
Requisições chegam (CAPES, CNPq, etc)
  └─ Você abre aba Acompanhamento
  └─ Duplo-clica em João Silva
  └─ Registra número da requisição
  └─ Clica [Registrar]
```

### 1º de janeiro (10:00 AM) - NOVO!
```
Task Scheduler dispara exportar_excel_mensal.py
  └─ Gera acompanhamento_2025-12.xlsx
  └─ Com todas as requisições de dezembro
  └─ Formatado profissionalmente
  └─ Pronto para enviar para director
```

---

## 🛠️ Personalização

### Mudar o horário de geração

**Editar no PowerShell:**
```powershell
$Trigger = New-ScheduledTaskTrigger -Monthly -DaysOfMonth 1 -At 14:30  # 14:30 (2:30 PM)
```

### Incluir mais colunas

**Editar em db.py, função `exportar_acompanhamento_para_excel()`:**
```python
SELECT 
    e.numero_edital,
    b.processo_sei,
    b.cpf,
    b.nome,
    b.programa,
    # Adicione aqui novos campos como:
    # b.email_bolsista as 'Email',
    # b.previsao_defesa as 'Previsão Defesa',
    ...
FROM acompanhamento a
JOIN bolsistas b ...
```

### Alterar cores/formatação

**Editar em db.py:**
```python
# Linha: cell.fill = PatternFill(start_color="366092", ...)
# "366092" é código hexadecimal da cor azul
# Mude para: "70AD47" (verde), "FF0000" (vermelho), etc.
```

---

## 📊 Comparação: CSV vs Excel

| Aspecto | CSV | Excel (Novo) |
|---------|-----|--------------|
| **Formatação** | Nenhuma | Profissional |
| **Headers** | Simples | Azul com negrito |
| **Valores monetários** | 1500.0 | R$ 1.500,00 |
| **Bordas** | Nenhuma | Em tudo |
| **Colunas ajustadas** | Não | Sim |
| **Cores alternadas** | Não | Sim (futuro) |
| **Tamanho arquivo** | ~2 KB | ~10 KB |
| **Abrir em Excel** | Sim | Nativo |
| **Impressão bonita** | Não | Sim |

**Uso recomendado:**
- **CSV:** Importar em sistemas automatizados
- **Excel:** Enviar para directors, imprimir, compartilhar

---

## 🐛 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'openpyxl'"

**Solução:**
```powershell
pip install openpyxl
```

### Erro: "Arquivo não pode ser aberto"

**Causas possíveis:**
- Arquivo aberto em Excel (não pode sobrescrever)
- Pasta sem permissão de escrita

**Solução:**
1. Feche arquivo no Excel
2. Escolha pasta diferente
3. Verifique permissões

### Arquivo Excel vazio

**Solução:**
1. Verifique se há registros de acompanhamento para o mês
2. Execute `python prefill_acompanhamento.py` manualmente
3. Registre uma requisição (duplo-clique + [Registrar])
4. Tente exportar novamente

---

## 📈 Próximos Passos (Futuro)

- ✅ Cores alternadas nas linhas (melhor legibilidade)
- ✅ Gráficos de gastos mensais dentro do Excel
- ✅ Assinatura digital e timestamp
- ✅ Email automático com arquivo anexado
- ✅ Formato PDF com mesmo design

---

## 🎯 Resumo Rápido

```
Para usar Excel exportado mensalmente:

1. MANUAL: Clique [Exportar Excel] na aba Acompanhamento
2. AUTOMÁTICO: Agende no Task Scheduler para 1º do mês

Resultado: Arquivo Excel formatado pronto para apresentar
```

Dúvidas? Consulte o README.md ou CASO_DE_USO_NARRATIVO.md
