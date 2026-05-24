# FAQ - Perguntas Frequentes

## Geral

### P: Como fazer backup dos dados?
**R**: O banco SQLite é um arquivo único. Basta copiar:
```
C:\Users\SEU_USUARIO\Documents\gestao_editais\gestao_editais.db
```
para um local seguro (OneDrive, pen drive, etc).

---

### P: Posso usar em outro computador?
**R**: Sim! Basta:
1. Instalar Python 3.8+ no novo PC
2. Copiar a pasta `gestao_editais/` inteira
3. Executar: `.\.venv\Scripts\pip.exe install -r requirements.txt`
4. Rodar: `python app.py`

**Ou** se quiser os dados também:
- Copie o arquivo `gestao_editais.db` para o novo computador

---

### P: Quantas bolsas/editais o sistema suporta?
**R**: SQLite tem limite teórico de ~140 TB. Praticamente:
- ✅ Sem problema: até 10.000 bolsistas
- ⚠️ Pode ficar lento: acima de 100.000 registros

Para aplicação em universidade pequena/média, sem limites práticos.

---

### P: Como adicionar mais usuários?
**R**: O sistema **não tem multi-usuário nativo**. Opções:
1. **Compartilhar arquivo DB**: Deixar `gestao_editais.db` em pasta compartilhada do Windows
2. **Passar para servidor**: Migrar para PostgreSQL/MySQL (requer desenvolvimento)
3. **Usar nuvem**: Sincronizar com OneDrive/Google Drive

---

## Operacional

### P: Perdi minha senha. Como recupero?
**R**: O sistema não tem autenticação/senha. Qualquer pessoa com acesso ao arquivo pode abrir.

**Solução de segurança**:
- Proteja a pasta com permissões Windows
- Ou use BitLocker para criptografar a unidade

---

### P: Como imprimir um relatório?
**R**: 
1. Exporte em Excel (**Acompanhamento** → **Exportar Excel**)
2. Abra em Microsoft Excel
3. Customize layout e clique **Imprimir**

---

### P: Posso adicionar mais campos/colunas?
**R**: Sim! Exemplos:

**Novo campo em Bolsistas (e-mail)**:
1. Edite `criar_banco.py`, adicione coluna:
   ```python
   cursor.execute("""ALTER TABLE bolsistas ADD COLUMN email TEXT""")
   ```
2. Crie arquivo de migração `atualizar_banco_v3.py`
3. Execute a migração
4. Edite `app.py` para mostrar o campo na UI

Fácil para campos simples. Para estruturas complexas, avise para ajuda.

---

### P: Como fazer backup automático?
**R**: Opções:

**Opção 1: Agendar cópia**
```powershell
# Crie arquivo: backup.ps1
$origem = "C:\Users\SEU_USUARIO\Documents\gestao_editais\gestao_editais.db"
$destino = "C:\Backups\gestao_editais_$(Get-Date -Format 'yyyy-MM-dd').db"
Copy-Item $origem -Destination $destino
```

Agende no Task Scheduler para rodar diariamente.

**Opção 2: Usar OneDrive/Google Drive**
- Mova toda pasta `gestao_editais/` para nuvem
- Sincroniza automaticamente

---

## Técnico

### P: Onde ficam os logs?
**R**: O sistema não mantém log file. Apenas:
- **Erros na UI**: Aparecem em caixas de diálogo
- **Console**: Se iniciou pelo terminal, erros lá aparecem
- **Task Scheduler**: Logs em `Event Viewer` → Windows Logs → Application

---

### P: Como ver a estrutura do banco?
**R**: Use DB Browser (SQLite):
1. Download: https://sqlitebrowser.org/
2. Abra `gestao_editais.db`
3. Veja structure, dados, execute queries custom

---

### P: Posso acessar o banco de dentro da aplicação?
**R**: Sim! Todas funções estão em `db.py`. Exemplo:

```python
import db

# Listar todos editais
editais = db.obter_todos_editais()
print(editais)

# Inserir novo bolsista
novo_id = db.inserir_bolsista(
    edital_id=1,
    cpf="123.456.789-00",
    nome="João Silva",
    programa="Engenharia",
    campus="Campus Centro",
    nivel="Mestrado",
    data_inicio="2025-09-01"
)
```

---

### P: Como fazer query SQL diretamente?
**R**: Edite `db.py` ou crie script novo:

```python
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'gestao_editais.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Sua query aqui
cursor.execute("SELECT * FROM bolsistas WHERE status = 'ativo'")
resultados = cursor.fetchall()

for row in resultados:
    print(row)

conn.close()
```

---

## Problemas Comuns

### P: "Erro: database is locked"
**R**: Outro processo está usando. Solução:
```powershell
# Feche a aplicação
taskkill /im python.exe /f

# Ou reinicie PC
```

---

### P: Exportação de Excel fica vazia
**R**: Verifique:
1. Existem registros de acompanhamento nesse mês?
2. A tabela `acompanhamento` tem dados?

**Debug**:
```python
import db
acomp = db.obter_acompanhamento(referencia_mes='2025-12')
print(f"Registros encontrados: {len(acomp)}")
```

---

### P: Datas mostram errado
**R**: Verificar:
1. Formato de entrada: deve ser DD/MM/YYYY
2. Formato do banco: internamente é YYYY-MM-DD (esperado)
3. Formato de saída: Excel é DD/MM/YYYY (esperado)

Se mostrar errado, edite `converter_data_iso_para_br()` em `app.py`.

---

### P: Não consigo instalar `openpyxl`
**R**: Verifique:
```powershell
# 1. Virtual env ativo?
.\.venv\Scripts\Activate.ps1

# 2. Pip funciona?
.\.venv\Scripts\pip.exe --version

# 3. Instale novamente
.\.venv\Scripts\pip.exe install openpyxl
```

Se ainda falhar, pode ser antivírus bloqueando. Tente:
```powershell
.\.venv\Scripts\pip.exe install openpyxl --no-cache-dir
```

---

## Roadmap / Futuro

### Funcionalidades em discussão
- [ ] Multi-usuário com autenticação
- [ ] Sincronização de dados em nuvem
- [ ] Relatórios com gráficos
- [ ] Integração com email (enviar Excel automaticamente)
- [ ] Aplicação web (Flask/Django)
- [ ] Backup automático via cloud
- [ ] Notificações de pagamentos vencidos

### Como sugerir melhorias?
Abra uma issue no GitHub ou envie email para: tim@example.com

---

## Contato / Suporte

**Desenvolvedor**: Tim Couto  
**Email**: tim@example.com  
**GitHub**: https://github.com/seu-usuario/gestao_editais  
**Última atualização**: Dezembro 2025

---

## Versões

| Versão | Data | Mudanças |
|--------|------|----------|
| 3.0 | Dez 2025 | ✨ Exportação Excel com formatação profissional + Task Scheduler |
| 2.1 | Nov 2025 | 🐛 Correções de bugs em edição |
| 2.0 | Out 2025 | 🏗️ Refatoração para padrão MVC + db.py |
| 1.0 | Set 2025 | 🎉 Lançamento inicial |

