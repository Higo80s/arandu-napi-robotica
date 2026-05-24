# 📦 SISTEMA DE BACKUP - Documentação

## Visão Geral

Sistema automático de backup para PostgreSQL com:
- ✅ Backup automático comprimido (GZIP)
- ✅ Restauração rápida e segura
- ✅ Limpeza automática de backups antigos
- ✅ Logs detalhados
- ✅ Metadados de cada backup

---

## 📁 Estrutura de Arquivos

```
backups/
├── postgres/
│   ├── auto/           # Backups automáticos
│   │   ├── backup_20260129_180316.sql.gz
│   │   └── backup_20260129_180316.sql.gz.json (metadados)
│   └── manual/         # Backups manuais
│       └── SNAPSHOT_*.sql
logs/
└── backup/             # Logs de operações
    ├── backup_202601.log
    └── cleanup_202601.log
scripts/
├── backup_postgres.py          # Criar backup
├── restore_postgres.py         # Restaurar backup
└── cleanup_old_backups.py      # Limpar backups antigos
```

---

## 🚀 Uso

### 1. Criar Backup Manual

```bash
cd c:\Users\higosantos\Documents\gestao_editais\gestao_editais_novo
python scripts\backup_postgres.py
```

**Resultado:**
- Arquivo criado em: `backups/postgres/auto/backup_YYYYMMDD_HHMMSS.sql.gz`
- Metadados em: `backup_YYYYMMDD_HHMMSS.sql.gz.json`
- Log em: `logs/backup/backup_YYYYMM.log`

---

### 2. Restaurar Backup

#### Modo Interativo:
```bash
python scripts\restore_postgres.py
```

Escolha o backup da lista e confirme digitando `RESTAURAR`.

#### Modo Não-Interativo:
```bash
python scripts\restore_postgres.py 1
```

(Onde `1` é o número do backup mais recente)

**⚠️ ATENÇÃO:** A restauração SUBSTITUI TODOS os dados do banco!

---

### 3. Limpar Backups Antigos

#### Modo Dry-Run (Preview):
```bash
python scripts\cleanup_old_backups.py --dry-run
```

Mostra quais backups seriam removidos SEM deletar.

#### Executar Limpeza:
```bash
python scripts\cleanup_old_backups.py
```

#### Políticas:
- **Retenção:** 30 dias (padrão)
- **Mínimo a manter:** 7 backups (segurança)
- **Customizar:** `python scripts\cleanup_old_backups.py --days 60`

---

## ⏰ Agendamento Automático (Windows Task Scheduler)

### Passo 1: Criar Tarefa de Backup Diário

1. Abrir **Task Scheduler** (Agendador de Tarefas)
2. **Criar Tarefa Básica**
3. Nome: `Backup PostgreSQL - Gestão Editais`
4. Gatilho: **Diariamente** às **03:00**
5. Ação: **Iniciar um Programa**
   - Programa: `C:\Users\higosantos\Documents\gestao_editais\gestao_editais_novo\.venv\Scripts\python.exe`
   - Argumentos: `scripts\backup_postgres.py`
   - Iniciar em: `C:\Users\higosantos\Documents\gestao_editais\gestao_editais_novo`

### Passo 2: Criar Tarefa de Limpeza Semanal

1. Nome: `Limpeza Backups - Gestão Editais`
2. Gatilho: **Semanalmente** (domingos) às **04:00**
3. Ação: **Iniciar um Programa**
   - Programa: `C:\Users\higosantos\Documents\gestao_editais\gestao_editais_novo\.venv\Scripts\python.exe`
   - Argumentos: `scripts\cleanup_old_backups.py`
   - Iniciar em: `C:\Users\higosantos\Documents\gestao_editais\gestao_editais_novo`

---

## 📊 Metadados do Backup

Cada backup `.sql.gz` tem um arquivo `.json` correspondente:

```json
{
  "filename": "backup_20260129_180316.sql.gz",
  "timestamp": "20260129_180316",
  "size_mb": 0.04,
  "original_size_mb": 0.35,
  "compression_ratio": 88.6,
  "database": "gestao_editais",
  "created_at": "2026-01-29T18:03:16.775325"
}
```

---

## 🔍 Verificar Logs

### Log de Backups:
```bash
type logs\backup\backup_202601.log
```

### Log de Limpeza:
```bash
type logs\backup\cleanup_202601.log
```

---

## ⚠️ Troubleshooting

### Erro: `pg_dump.exe não encontrado`

**Solução:** Atualizar caminho no script

1. Localizar instalação do PostgreSQL:
   ```bash
   dir "C:\Program Files\PostgreSQL\" /b
   ```

2. Editar `scripts/backup_postgres.py`:
   ```python
   self.pg_dump_path = r"C:\Program Files\PostgreSQL\[SUA_VERSÃO]\bin\pg_dump.exe"
   ```

### Erro: `PGPASSWORD authentication failed`

**Solução:** Verificar senha no script ou usar `.pgpass`

### Backup muito grande

**Solução:** 
- Comprimir ainda mais: Adicionar `--compress=9` no pg_dump
- Fazer backup parcial (excluir tabelas de log)

---

## 🛡️ Segurança

### Proteção de Senha

**Recomendado para produção:**

1. Usar arquivo `.pgpass` (Windows: `%APPDATA%\postgresql\pgpass.conf`):
   ```
   localhost:5432:gestao_editais:postgres:admin123
   ```

2. Ou usar variáveis de ambiente:
   ```bash
   set PGPASSWORD=admin123
   python scripts\backup_postgres.py
   ```

### Permissões de Acesso

- Backups contêm TODOS os dados sensíveis
- Proteger diretório `backups/` com permissões adequadas
- Considerar criptografia para backups em produção

---

## 📈 Estatísticas

### Taxa de Compressão

SQL puro comprime ~85-90% com GZIP:
- **Original:** 0.35 MB
- **Comprimido:** 0.04 MB
- **Economia:** 88.6%

### Tempo de Execução

- **Backup:** ~5-10 segundos (para DB de 500 registros)
- **Restauração:** ~10-20 segundos
- **Limpeza:** <1 segundo

---

## 🎯 Checklist de Segurança

Antes de confiar 100% no sistema:

- [ ] Criar backup manual
- [ ] Testar restauração em banco de teste
- [ ] Verificar logs de sucesso
- [ ] Configurar tarefas agendadas
- [ ] Testar limpeza (dry-run primeiro)
- [ ] Documentar procedimentos para equipe TI
- [ ] Simular recuperação de desastre completa

---

## 📞 Suporte

**Em caso de problemas:**

1. Verificar logs em `logs/backup/`
2. Executar backup manual para teste
3. Contatar equipe de desenvolvimento

**Equipe Técnica:**
- Yoko (IA Lead)
- Katsuko (Backend Specialist)

---

**Versão:** 1.0  
**Última Atualização:** 29/01/2026  
**Status:** ✅ Testado e Operacional
