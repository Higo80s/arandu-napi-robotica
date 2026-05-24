# Caso de Uso Narrativo: Implementação de Bolsa em Gestão de Editais

## Contexto: Segunda-feira, 9 de dezembro de 2025

**Cenário:** Você trabalha como assistente administrativo no Departamento de Pós-Graduação de uma universidade. Sua chefia, a Profa. Dra. Marina, chega com um problema:

---

## 🔴 O Problema

**Marina:** "Oi! Temos uma situação complicada aqui. O processo SEI 2025001234 da bolsa de mestrado do João Silva chegou hoje, financiado pelo edital CAPES 2025-001. A bolsa começa em janeiro de 2026 e vai até dezembro de 2026 (12 meses). Só que ninguém implementou essa bolsa no sistema ainda. Preciso que você cadastre isso e me gere um relatório com todas as parcelas mensais para acompanhamento. Além disso, precisamos receber uma notificação automática no começo de cada mês para registrar se a requisição de pagamento foi feita. Pode fazer?"

Você pega os dados:
- Processo SEI: 2025001234
- Bolsista: João Silva
- CPF: 123.456.789-00
- Nível: Mestrado
- Programa: Engenharia de Sistemas
- Orientador: Prof. Dr. Carlos
- Campus: Centro
- Data de início no curso: 01/08/2023
- Data de início da bolsa: 01/01/2026
- Duração: 12 meses
- Previsão de defesa: 15/12/2026
- Email bolsista: joao.silva@university.edu.br
- Email programa: posgrad@university.edu.br

---

## 📊 Passo 1: Criar o Edital (se não existir)

Você abre o sistema **Gestão de Editais** (uma aplicação Tkinter com tema escuro). A interface está limpa, profissional, com abas bem organizadas.

**Clica em:** Tab "Cadastro de Edital"

```
┌─────────────────────────────────────────┐
│ GESTÃO DE EDITAIS                       │
├─────────────────────────────────────────┤
│ [Edital] [Modalidades] [Bolsistas] [Consulta] [Acompanhamento]
├─────────────────────────────────────────┤
│ Número do Edital:    │ CAPES 2025-001
│ Descrição:           │ Bolsas de Mestrado CAPES 2025
│ Agência de Fomento:  │ CAPES
│ Código do Projeto:   │ PROJ-2025-042
│ Descrição Projeto:   │ Programa de Pós-Graduação em Eng. Sistemas
│
│ [Cadastrar]  [Limpar]
└─────────────────────────────────────────┘
```

**Por que usar um banco de dados?**

Você se pergunta: *"Por que não usar apenas uma planilha Excel?"*

A resposta é clara:
- **Integridade:** Constraints de foreign key garantem que nenhuma bolsa seja cadastrada para um edital inexistente
- **Auditoria:** Cada inserção/atualização é rastreável (datas, usuários - tema para futura expansão)
- **Escalabilidade:** Com 50 editais, 200 bolsistas, 12 parcelas cada, são 2.400 registros - Excel fica lento
- **Automação:** Queries automáticas para relatórios, sem erros de fórmula
- **Segurança:** Backup fácil, sem perda de dados por "save acidental"

Você clica em **[Cadastrar]** e um dialog confirma:
```
✓ Edital cadastrado com sucesso!
```

**No banco (SQLite):**
```sql
INSERT INTO editais (numero_edital, descricao, agencia_fomento, codigo_projeto, descricao_projeto)
VALUES ('CAPES 2025-001', 'Bolsas de Mestrado CAPES 2025', 'CAPES', 'PROJ-2025-042', 'Programa de PG em Eng. Sistemas');
-- Resultado: edital_id = 7 (auto-incremento)
```

**Arquivo:** `gestao_editais.db` (SQLite) ← Localizado na mesma pasta da aplicação, fácil backup

---

## 🎓 Passo 2: Definir a Modalidade

**Clica em:** Tab "Modalidades"

```
┌─────────────────────────────────────────┐
│ Selecione o Edital:  │ CAPES 2025-001
│ Nível:               │ mestrado
│ Número de Vagas:     │ 5
│ Valor Mensal (R$):   │ 1500.00
│
│ [Cadastrar]  [Limpar]
└─────────────────────────────────────────┘
```

**Por que separar modalidades de editais?**

Diferentes editais podem ter diferentes níveis e valores. Exemplo:
- Edital CAPES 2025-001: 5 vagas de mestrado @ R$ 1.500/mês, 3 vagas de doutorado @ R$ 2.000/mês
- Edital CNPq 2025-002: 2 vagas de pós-doc @ R$ 4.500/mês

A tabela `modalidades` implementa isso:
```
┌──────┬──────────┬────────┬───────┬─────────────┐
│ id   │ edital_id│ nivel  │ vagas │ valor_mensal│
├──────┼──────────┼────────┼───────┼─────────────┤
│ 15   │ 7        │mestrado│ 5     │ 1500.00     │
│ 16   │ 7        │doutorado│ 3    │ 2000.00     │
└──────┴──────────┴────────┴───────┴─────────────┘
```

Você clica em **[Cadastrar]** → Sucesso!

---

## 👤 Passo 3: Cadastrar a Bolsa (Bolsista)

**Clica em:** Tab "Bolsistas"

```
┌─────────────────────────────────────────────────────┐
│ Edital:                      │ CAPES 2025-001
│ Nível:                       │ mestrado
├─────────────────────────────────────────────────────┤
│ Processo SEI:                │ 2025001234
│ Nome do Bolsista:            │ João Silva
│ CPF:                         │ 123.456.789-00
│ Orientador:                  │ Prof. Dr. Carlos
│ Campus:                      │ Centro
│ Programa:                    │ Engenharia de Sistemas
│ Data de Início no Curso:     │ 01/08/2023
│ Data de Início da Bolsa:     │ 01/01/2026
│ Meses de Duração:            │ 12
│ Previsão de Defesa:          │ 15/12/2026
│ Email do Bolsista:           │ joao.silva@university.edu.br
│ Email do Programa:           │ posgrad@university.edu.br
│
│ [Cadastrar]  [Limpar]
└─────────────────────────────────────────────────────┘
```

**O que acontece nos bastidores:**

```python
# Em db.py (módulo centralizado de banco de dados)
def criar_bolsista(edital_id, processo, nome, cpf, orientador, ...):
    # 1. Validação de datas
    data_fim = calcular_data_fim_bolsa(data_inicio_bolsa_iso, meses)
    # João: 01/01/2026 + 12 meses = 31/12/2026
    
    # 2. Inserção com conversão de formatos
    # UI usa: DD/MM/YYYY (01/01/2026)
    # DB usa: YYYY-MM-DD ISO (2026-01-01)
    
    # 3. Status inicial: 'ativo'
    
    # 4. Commit na transação
    cursor.execute('''
        INSERT INTO bolsistas (...) 
        VALUES (...)
    ''')
    conn.commit()
```

**No banco:**
```sql
INSERT INTO bolsistas (edital_id, processo_sei, nome, cpf, ..., status)
VALUES (7, '2025001234', 'João Silva', '123.456.789-00', ..., 'ativo');
-- Resultado: bolsista_id = 42
```

Clica em **[Cadastrar]** → ✓ Sucesso!

---

## 📅 Passo 4: Sistema de Acompanhamento (Parcelas Mensais)

**Clica em:** Tab "Acompanhamento"

Aqui é onde acontece a mágica. A tela mostra:

```
┌────────────────────────────────────────────────────────┐
│ ACOMPANHAMENTO DE BOLSAS                               │
├────────────────────────────────────────────────────────┤
│ [Prefill Mês Atual] [Registrar Parcela] [Exportar CSV] │
├────────────────────────────────────────────────────────┤
│ Bolsista          │ Nível    │ Ref. Mês │ Parcela │ Req│
├────────────────────────────────────────────────────────┤
│ João Silva        │ Mestrado │ 2025-12  │ 0       │ -  │
│ (Duplo-clique para editar)                             │
└────────────────────────────────────────────────────────┘
```

**O fluxo:**

### a) **Prefill Automático (Script Agendado)**

Você recebeu um email com instruções sobre o agendador de tarefas do Windows. Marina pediu para configurar um automático, então:

**Você configura o Agendador de Tarefas do Windows:**

1. Abre: `taskschd.msc` (Agendador de Tarefas)
2. Cria nova tarefa "Prefill Bolsas"
3. Trigger: **Primeiro dia de cada mês, 06:00 AM**
4. Ação: Executar `python prefill_acompanhamento.py`

```python
# prefill_acompanhamento.py
if __name__ == '__main__':
    inserted, ref = db.prefill_mes_atual()
    print(f"Prefill completado para {ref}: {inserted} registros inseridos")
    
    # Envia email para bolsistas (futura funcionalidade)
    # notificar_bolsistas(ref)
```

**O que o script faz:**

```python
# db.prefill_mes_atual()
ref = "2026-01"  # Janeiro 2026

# Para cada bolsista com status = 'ativo':
for bolsista_id, data_inicio_bolsa in bolsistas_ativos:
    parcela = calcular_parcela(data_inicio_bolsa, ref)
    # João: parcela 1 em 2026-01, parcela 2 em 2026-02, ...
    
    # Upsert com fallback (compatibilidade com SQLite antigo)
    INSERT OR IGNORE INTO acompanhamento (bolsista_id, referencia_mes, parcela)
    VALUES (42, '2026-01', 1)
```

**Motivação do agendamento automático:**

❌ **Sem automação:**
- Marina precisa lembrar de registrar cada mês
- Risco de esquecer → bolsa não registrada → complicações legais

✅ **Com automação:**
- No dia 1º de cada mês, 06:00, os registros são criados automaticamente
- Marina recebe email (futuro) com lista de bolsas para revisar
- Zero risco de esquecimento

---

### b) **Registrar Parcela Manualmente**

Agora é dia 15 de janeiro de 2026. A requisição de pagamento para a parcela 1 foi feita.

Você abre a aba Acompanhamento e vê:

```
┌────────────────────────────────────────────────────────┐
│ João Silva      │ 2026-01 │ 1 │ R$ 1.500 │ [ ? ]      │
│ (Duplo-clique para editar)                             │
└────────────────────────────────────────────────────────┘
```

**Duplo-clique:**

```
┌─────────────────────────────────────────┐
│ EDITAR ACOMPANHAMENTO - JOÃO SILVA      │
├─────────────────────────────────────────┤
│ Referência:      2026-01 (janeiro)
│ Parcela:         1 / 12
│ Valor:           R$ 1.500,00
│
│ Requisição Nº:   │ REQ-2026-001
│ Observações:     │ Pagamento autorizado 15/01/2026
│
│ [Registrar]  [Cancelar]
└─────────────────────────────────────────┘
```

Você preenche:
- **Requisição Nº:** REQ-2026-001
- **Observações:** "Pagamento autorizado 15/01/2026"
- Clica em **[Registrar]**

**O que acontece:**

```python
# db.registrar_acompanhamento()
def registrar_acompanhamento(bolsista_id, ref_mes, parcela, requisicao, observacoes):
    # Tenta UPDATE com ON CONFLICT (SQLite 3.24+)
    try:
        INSERT INTO acompanhamento (...)
        VALUES (42, '2026-01', 1, 'REQ-2026-001', 'Pagamento autorizado...')
        ON CONFLICT(bolsista_id, referencia_mes) DO UPDATE SET
            requisicao_pagamento = 'REQ-2026-001',
            observacoes = 'Pagamento autorizado...',
            criado_em = datetime('now')
    except OperationalError:
        # Fallback para SQLite antigo: SELECT → UPDATE
        cursor.execute('SELECT id FROM acompanhamento WHERE ...')
        if exists:
            UPDATE acompanhamento SET ...
        else:
            INSERT INTO acompanhamento SET ...
```

**Por que usar Upsert com fallback?**

- **ON CONFLICT:** Versões modernas do SQLite (seguro, atômico)
- **Fallback (SELECT→UPDATE/INSERT):** Compatibilidade com versões antigas
- **Resultado:** O código funciona em qualquer máquina do departamento

✓ Registro salvo!

---

## 📊 Passo 5: Gerar Relatório

Marina diz: *"Preciso de um relatório com todas as bolsas de janeiro para o diretor."*

**Você clica em:** Tab Acompanhamento → [Exportar CSV]

```python
# db.obter_acompanhamento_para_csv()
SELECT 
    bolsistas.nome,
    bolsistas.cpf,
    bolsistas.nivel,
    acompanhamento.referencia_mes,
    acompanhamento.parcela,
    acompanhamento.requisicao_pagamento,
    acompanhamento.observacoes
FROM acompanhamento
JOIN bolsistas ON acompanhamento.bolsista_id = bolsistas.id
WHERE referencia_mes = '2026-01'
ORDER BY bolsistas.nome
```

**Arquivo gerado:** `acompanhamento_2026-01.csv`

```
Nome,CPF,Nivel,Referencia,Parcela,Requisicao,Observacoes
João Silva,123.456.789-00,Mestrado,2026-01,1,REQ-2026-001,Pagamento autorizado 15/01/2026
Maria Santos,234.567.890-11,Doutorado,2026-01,1,REQ-2026-002,Pagamento autorizado 16/01/2026
```

Você envia para Marina → **Problema resolvido em 30 minutos!**

---

## ✏️ Editar um Registro

Mês seguinte. Você descobre que o CPF de João estava errado (erro de digitação).

**No Tab Bolsistas:**

1. Procura por "João Silva"
2. Duplo-clique na linha
3. Corrige CPF: 123.456.789-00 → 123.456.789-11
4. Clica em **[Atualizar]**

```python
# db.atualizar_bolsista()
UPDATE bolsistas 
SET cpf = '123.456.789-11'
WHERE id = 42
```

✓ Editado! O banco mantém histórico através de `data_criacao`/`data_atualizacao` (tema para expansão).

---

## 🗑️ Deletar um Registro

Cenário: João desistiu do mestrado (infelizmente).

**Você muda o status de "ativo" para "desligado":**

```python
# db.atualizar_bolsista(..., status='desligado')
UPDATE bolsistas 
SET status = 'desligado'
WHERE id = 42
```

**Por que não deletar?**

- **Auditoria:** Precisa manter registro histórico
- **Foreign Keys:** Acompanhamento continua vinculado
- **Integridade:** `ON DELETE CASCADE` poderia apagar histórico de pagamentos

✓ Softdelete implementado (deactivation, não deletion)

---

## 🔗 Integração com Banco de Dados: Arquitetura

### **Estrutura do Banco:**

```
gestao_editais.db (SQLite)
│
├── editais
│   ├── id (PK)
│   ├── numero_edital (TEXT, UNIQUE)
│   ├── descricao
│   ├── agencia_fomento
│   ├── codigo_projeto
│   └── descricao_projeto
│
├── modalidades
│   ├── id (PK)
│   ├── edital_id (FK → editais.id)
│   ├── nivel (CHECK: 'graduação', 'mestrado', 'doutorado', 'pós-doutorado')
│   ├── vagas (INTEGER)
│   └── valor_mensal (REAL)
│
├── bolsistas
│   ├── id (PK)
│   ├── edital_id (FK → editais.id)
│   ├── processo_sei (TEXT)
│   ├── nome, cpf, orientador, campus, programa
│   ├── nivel (CHECK: mesmo que modalidades)
│   ├── data_inicio_curso (DATE, ISO format: YYYY-MM-DD)
│   ├── data_inicio_bolsa (DATE)
│   ├── meses_duracao (INTEGER)
│   ├── data_fim_bolsa (DATE, calculada)
│   ├── previsao_defesa (DATE, nullable)
│   ├── email_bolsista, email_programa (TEXT)
│   ├── status (CHECK: 'ativo', 'desligado', 'substituído')
│   └── criado_em (TIMESTAMP)
│
├── acompanhamento (NEW - para tracking mensal)
│   ├── id (PK)
│   ├── bolsista_id (FK → bolsistas.id, ON DELETE CASCADE)
│   ├── referencia_mes (TEXT: YYYY-MM)
│   ├── parcela (INTEGER)
│   ├── requisicao_pagamento (TEXT, nullable)
│   ├── observacoes (TEXT, nullable)
│   ├── criado_em (TIMESTAMP)
│   └── UNIQUE(bolsista_id, referencia_mes)
│
└── substituicoes (para tracking de quando bolsista é substituído)
    ├── id (PK)
    ├── bolsista_id_saida (FK)
    ├── bolsista_id_entrada (FK)
    ├── data_substituicao (DATE)
    └── motivo (TEXT)
```

### **Por que SQLite e não MySQL/PostgreSQL?**

| Aspecto | SQLite | MySQL | PostgreSQL |
|---------|--------|-------|-----------|
| **Setup** | Zero - arquivo local | Requer servidor | Requer servidor |
| **Backup** | Copy do arquivo .db | Dump SQL complexo | Dump SQL complexo |
| **Acesso** | Qualquer máquina com Python | Requer credenciais/rede | Requer credenciais/rede |
| **Tamanho máx** | ~1 TB (suficiente para bolsas) | Ilimitado | Ilimitado |
| **Escalabilidade** | ~10.000 registros OK | Milhões OK | Milhões OK |
| **Custo** | R$ 0 | R$ 50-200/mês | R$ 50-200/mês |
| **Caso uso** | Desktop admin, PME | Website, SaaS | Website crítico |

**Conclusão:** SQLite é perfeito para um sistema de gestão de bolsas em nível departamental.

---

## 🤖 Agendamento de Tarefas: Status e Impacto

### **Status Atual: Configurado e Documentado**

**Arquivo:** `README.md` contém instruções completas.

**Configuração no Windows Task Scheduler:**

```
Tarefa: "Prefill Bolsas do Mês"
├── Trigger: 1º dia do mês, 06:00 AM
├── Ação: C:\Users\higosantos\Documents\gestao_editais\prefill_acompanhamento.py
├── Condição: Apenas se conectado (ou sempre, conforme política)
└── Resultado: Cria registros de acompanhamento para bolsistas ativos
```

### **Como Impacta o Projeto:**

```timeline
Antes (Manual):
  └─ Marina lembra (ou não) → abre sistema → clica em prefill → ERRO possível

Depois (Automático):
  └─ 06:00 AM, dia 1º do mês
     └─ Tarefa executada
        └─ prefill_acompanhamento.py chama db.prefill_mes_atual()
           └─ Query insere (bolsista_id, '2026-02', parcela=2)
              └─ Log registrado (possível expansão de email)
                 └─ Marina abre aba Acompanhamento → vê tudo pronto
                    └─ Registra requisições durante o mês
                       └─ Gera CSV no fim do mês
                          └─ Director recebe relatório
```

**Impacto quantificável:**
- ⏱️ Economia: ~5 minutos/mês × 12 meses = 1 hora/ano
- 🛡️ Confiabilidade: 0% chance de esquecimento
- 📊 Consistência: Todos os meses cadastrados automaticamente

---

## 📈 Geração de Relatórios

### **Atualmente Implementado:**

1. **CSV (Acompanhamento)** - Exportação simples
   ```
   [Exportar CSV] → acompanhamento_YYYY-MM.csv
   ```

2. **Excel** (Em planejamento - reportlab framework pronto)
3. **PDF** (Em planejamento - reportlab framework pronto)

### **Fluxo de Relatório:**

```
DB Query 
  ↓
Fetch Dados 
  ↓
Format CSV/Excel/PDF 
  ↓
Salva em disco 
  ↓
Usuário baixa/envia
```

**Exemplo de dados de saída:**

```
RELATÓRIO DE ACOMPANHAMENTO - JANEIRO 2026

Edital: CAPES 2025-001
Período: Janeiro 2026
Data de Geração: 2026-01-31

┌─────────────────────────────────────────────────────────────┐
│ Bolsista      │ Nível │ Parcela │ Valor  │ Requisição │ Obs│
├─────────────────────────────────────────────────────────────┤
│ João Silva    │ Mest. │ 1/12    │ 1.500  │ REQ-001    │ OK │
│ Maria Santos  │ Dout. │ 1/8     │ 2.000  │ REQ-002    │ OK │
│ Pedro Costa   │ Mest. │ 5/12    │ 1.500  │ REQ-003    │ OK │
└─────────────────────────────────────────────────────────────┘

TOTAL: R$ 5.000,00

Assinado digitalmente em: 2026-01-31 14:30:00
```

---

## 🎯 Fluxo Completo de Uso (Um Dia na Vida)

### **Segunda, 2 de janeiro de 2026 - 06:00 AM**

```
Tarefa agendada dispara automaticamente
  ↓
prefill_acompanhamento.py executa
  ↓
db.prefill_mes_atual() insere:
  - João Silva: 2026-01, parcela 1
  - Maria Santos: 2026-01, parcela 1
  - Pedro Costa: 2026-01, parcela 5
  ↓
Status: ✓ 3 registros inseridos
```

### **Terça, 3 de janeiro - 09:00 AM**

```
Marina checa inbox → vê lista de bolsas para revisar
  ↓
Abre app → Tab Acompanhamento
  ↓
Vê listagem já preenchida (automática!)
  ↓
Nota mental: "Preciso revisar requisições até o dia 15"
```

### **Sexta, 15 de janeiro - 14:00 PM**

```
Requisições confirmadas pela CAPES
  ↓
Você abre app → Tab Acompanhamento
  ↓
Duplo-clique em cada bolsa
  ↓
Preenche:
  - João Silva: Requisição REQ-2026-001
  - Maria Santos: Requisição REQ-2026-002
  - Pedro Costa: Requisição REQ-2026-003
  ↓
Status: ✓ 3 parcelas marcadas como requisitadas
```

### **Quarta, 29 de janeiro - 15:30 PM**

```
Marina precisa enviar relatório ao director
  ↓
Você abre app → Tab Acompanhamento
  ↓
Clica em [Exportar CSV]
  ↓
Arquivo: acompanhamento_2026-01.csv gerado
  ↓
Abre em Excel, formata, adiciona assinatura
  ↓
Envia para director
  ↓
Director recebe: "Todas as 3 bolsas ativas pagaram em janeiro. Situação controlada."
```

---

## 🔍 Análise Expert: Pontos Fortes e Melhorias

### **✅ Pontos Fortes**

1. **Separação de Responsabilidades (Refactoring DB)**
   - `db.py` centraliza todo SQL
   - `app.py` é apenas UI
   - **Vantagem:** Fácil testar, refatorar, reusar lógica

2. **Compatibilidade SQLite (Upsert com Fallback)**
   - Tenta `ON CONFLICT` (SQLite 3.24+)
   - Se falhar, usa `SELECT→UPDATE/INSERT`
   - **Vantagem:** Funciona em qualquer Windows, sem atualizar SQLite

3. **Conversão de Datas (Localização)**
   - UI: DD/MM/YYYY (formato brasileiro)
   - DB: YYYY-MM-DD (ISO, standard internacional)
   - Funções helpers: `converter_data_br_para_iso()`
   - **Vantagem:** Zero confusão, relatórios corretos

4. **Soft-Delete (Status = 'desligado')**
   - Não apaga, apenas marca inativo
   - **Vantagem:** Auditoria, rastreabilidade, sem perda de histórico

5. **Automação com Task Scheduler**
   - Prefill automático no 1º do mês
   - **Vantagem:** Zero risco de esquecimento, previsível

### **⚠️ Melhorias Futuras**

1. **Autenticação e Controle de Acesso**
   ```python
   # Atualmente: App é local, sem login
   # Futuro: Adicionar login de usuário
   # Admin: Pode deletar/editar tudo
   # Coord: Pode ver/registrar bolsas
   # Bolsista: Pode ver próprio acompanhamento
   ```

2. **Email Automático**
   ```python
   # Prefill + enviar email para coordenação:
   # "3 bolsas criadas para fevereiro. Registre requisições até 15/02."
   ```

3. **Dashboard / Gráficos**
   ```python
   # Visão de alto nível:
   # - Bolsas ativas por edital
   # - Parcelas pagas vs. pendentes
   # - Forecast de gastos mensais
   ```

4. **Migrações Versionadas**
   ```
   atualizar_banco_v1.py → criar_banco.py
   atualizar_banco_v2.py → adicionar data_inicio_curso
   atualizar_banco_v3.py → adicionar acompanhamento
   atualizar_banco_v4.py → FUTURO: auditoria/logs
   ```

5. **Relatórios Mais Elaborados (PDF, Excel)**
   - Código estrutura já existe (`reportlab`, `openpyxl`)
   - Faltam: templates, formatação, assinatura digital

6. **Backup Automático**
   ```python
   # Weekly backup de gestao_editais.db para cloud/rede
   # Evita perda por hardware failure
   ```

7. **API REST (Para integração futura)**
   ```python
   # GET /api/bolsistas/ativo → lista bolsas ativas
   # POST /api/acompanhamento → registrar parcela
   # Permite integração com sistema administrativo institucional
   ```

### **🎓 Análise de Arquitetura**

#### **Padrão: MVC Híbrido**

```
┌─────────────────────┐
│   View (Tkinter)    │  ← UI: Abas, inputs, Treeviews
│   app.py (1678 lin) │
└──────────┬──────────┘
           │
    ┌──────▼──────┐
    │ Lógica UI   │  ← Validações de formato, conversão datas
    └──────┬──────┘
           │
    ┌──────▼──────────────────────┐
    │  Model (Banco de Dados)      │
    │  db.py (300 linhas)          │  ← SQL centralizado
    │  ├── editais                 │
    │  ├── modalidades             │
    │  ├── bolsistas               │
    │  ├── acompanhamento          │
    │  └── helpers (calcular, etc) │
    └──────┬──────────────────────┘
           │
           ▼
    gestao_editais.db (SQLite)
```

#### **Benefícios dessa arquitetura:**

| Camada | Benefício |
|--------|-----------|
| **View** | Apenas apresentação, Tkinter responsável |
| **UI Logic** | Validações reutilizáveis, helpers testáveis |
| **Model** | SQL isolado, queries otimizáveis, sem repeticao |
| **DB** | Normalize 3NF, integridade via constraints |

#### **Exemplo de Escalabilidade:**

Se no futuro precisar de:
- **API REST?** Crie `api.py` que chama funções de `db.py`
- **CLI?** Crie `cli.py` que chama funções de `db.py`
- **Reports?** Crie `reports.py` com queries em `db.py`

Tudo reutiliza `db.py` → DRY (Don't Repeat Yourself)

---

## 🎬 Cenário: Mudança de Requisitos

**Cenário Real:**

Marina: *"Preciso adicionar um campo 'bolsista_substituto' para rastrear quem substitui quem quando alguém sai."*

**Sem essa arquitetura:**
- Seria necessário editar SQL em 5 lugares diferentes em `app.py`
- Risco de inconsistência
- Difícil testar

**Com db.py:**
1. Cria migração: `atualizar_banco_v4.py`
   ```python
   ALTER TABLE bolsistas ADD COLUMN bolsista_substituto_id INTEGER REFERENCES bolsistas(id);
   ```

2. Adiciona função em `db.py`:
   ```python
   def registrar_substituicao(bolsista_saida_id, bolsista_entrada_id):
       # Lógica de substituição
   ```

3. Chama em `app.py`:
   ```python
   db.registrar_substituicao(old_id, new_id)
   ```

**Tempo total:** 15 minutos vs. 2 horas sem modularização

---

## 📋 Resumo Executivo (Para Marina)

**Marina, aqui está o status:**

✅ **Bolsa de João Silva implementada:**
- Processo: 2025001234
- Mestrado, 12 meses, R$ 1.500/mês
- Total estimado: R$ 18.000

✅ **Sistema configurado:**
- Banco de dados SQLite (local, sem dependências externas)
- Acompanhamento mensal automático (prefill no 1º do mês)
- Exportação de relatórios em CSV
- Histórico completo e auditável

✅ **Próximas ações:**
- Dia 1º de fevereiro: sistema automaticamente criará parcela 2
- Sempre que requisição for feita: você registra no sistema
- Fim de mês: você exporta relatório para o director

✅ **Vantagens:**
- Zero risco de esquecer de registrar
- Relatórios gerados em segundos
- Backup local fácil
- Escalável para 100+ bolsas

🎯 **Resultado:** Processo de bolsa 100% controlado, auditável e automatizado.

---

## 📝 Conclusão Técnica

Este sistema demonstra como uma aplicação desktop bem estruturada pode resolver problemas administrativos reais:

1. **Problema:** Rastreamento manual de bolsas → erros
2. **Solução:** Base de dados + UI intuitiva + automação
3. **Resultado:** Processo controlado, auditável, escalável

**Stack utilizado:**
- **Frontend:** Tkinter + ttkthemes (interface desktop limpa)
- **Backend:** Python 3.8+ com SQLite3
- **Padrão:** MVC com separação clara db.py/app.py
- **Automação:** Windows Task Scheduler

**Essa é uma arquitectura sólida para um MVP (Mínimo Produto Viável) que pode evoluir para:**
- Multi-usuário (com autenticação)
- Na nuvem (migrar DB para PostgreSQL)
- Com API REST (para integrações)
- Dashboard (com gráficos em tempo real)

**Mas por enquanto,** resolve 100% o problema de Marina de forma simples, maintível e sem dependências externas desnecessárias.

---

**Assinado:** Seu Assistente Administrativo, Data: 2025-12-09
