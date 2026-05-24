# Relatório Técnico: Bolsas CAPES IES

## Situação Identificada

**Data:** 16/01/2026  
**Fonte:** Plataforma Sucupira vs Sistema Local

---

## 📊 Dados da Plataforma Sucupira

### Bolsistas IES Ativos (15 total)

**Doutorado (5 bolsistas):**
1. ANA CLAUDIA LAZAROTO - 01/01/2026 a 31/03/2026
2. ALINE FERNANDA CAMPAGNARO - 01/04/2025 a 31/03/2026  
3. CARLA FERNANDA MAREK - 01/12/2025 a 30/11/2027
4. MARCUS VINICIUS DA SILVA RODRIGUES - 01/12/2025 a 30/11/2027
5. SUZANA STRUIVING - 01/10/2024 a 31/08/2026
6. VIVIAN PRADO DE CAMARGO LEAO - 01/12/2025 a 30/11/2027 *(6º bolsista)*

**Mestrado (10 bolsistas):**
1. ANA CAROLINA MONTEIRO - 01/12/2025 a 30/11/2026
2. BERNARD MENE - 01/12/2025 a 30/11/2026
3. DANKA FARIAS DE OLIVEIRA - 01/12/2025 a 30/06/2027
4. GABRIELA WOLHMUTH - 01/05/2025 a 28/02/2026
5. GUILHERME SEVERO MEDEIROS - 01/12/2025 a 30/06/2026
6. ISABELA DA SILVA LEONARDO - 01/12/2025 a 30/11/2026
7. JAINARA BAPTISTA GASPAR - 01/12/2025 a 30/11/2026
8. MATEUS MOISES MUTOCOLA - 01/10/2024 a 31/08/2026
9. MATHEUS BUENO BARTKEVICIUS - 01/12/2025 a 30/11/2026
10. THEMIS RAQUEL DE JESUS DE OLIVEIRA - 01/12/2025 a 30/11/2026

**Total:** 6 Doutorado + 10 Mestrado = **16 bolsistas IES**

---

## 💾 Dados do Sistema Local

### Cotas IES Cadastradas

```sql
SELECT m.nivel, dc.qtd_concedida
FROM distribuicao_cotas dc
JOIN modalidades m ON dc.modalidade_id = m.id
WHERE dc.edital_id = 14 AND dc.programa_id IS NULL
```

**Resultado esperado:**
- Mestrado: 14 cotas
- Doutorado: 9 cotas
- **Total: 23 cotas IES**

### Bolsistas IES Cadastrados

```sql
SELECT COUNT(*) FROM bolsistas
WHERE agencia_fomento LIKE '%IES%' AND ativo = 1
```

**Resultado:** **0 bolsistas** ❌

---

##  Diagnóstico

### Problema Identificado

Os **16 bolsistas IES da Plataforma Sucupira NÃO estão cadastrados** no sistema local.

### Impacto

1. **Dashboard CAPES:**
   - Mostra 414 bolsas (correto para CAPES DS)
   - Não conta as 16 bolsas IES em uso
   - **Total real deveria ser: 414 + 16 = 430 bolsas**

2. **Relatórios Históricos:**
   - Não incluem os 16 bolsistas IES
   - Subestimam o impacto das bolsas CAPES

3. **Cotas IES:**
   - Sistema mostra 23 cotas "disponíveis"
   - **Na verdade:** 16 em uso + 7 livres = 23 total

---

## ✅ Solução Proposta

### Opção 1: Cadastro Manual (Recomendado)

Cadastrar os 16 bolsistas no sistema através da interface em:
- http://127.0.0.1:5003/bolsistas/novo

**Dados necessários:**
- Nome, CPF (fornecidos acima)
- Programa acadêmico (precisa ser identificado)
- Agência: "CAPES IES"
- Data início/fim (fornecidas acima)
- Orientador

### Opção 2: Script de Importação Automática

Criar script para importar bolsistas da Plataforma Sucupira via API/CSV.

### Opção 3: Sincronização Periódica

Implementar rotina de sincronização automática com Plataforma Sucupira.

---

## 📋 Próximas Ações

1. **Imediato:**
   - [ ] Identificar programa acadêmico de cada bolsista IES
   - [ ] Cadastrar os 16 bolsistas no sistema
   - [ ] Configurar `agencia_fomento = 'CAPES IES'`

2. **Verificação:**
   - [ ] Reexecutar `verificar_bolsas_ies.py`
   - [ ] Confirmar 16 bolsistas ativos
   - [ ] Ver dashboard atualizado (430 bolsas)

3. **Longo prazo:**
   - [ ] Criar processo de importação automática
   - [ ] Sincronizar mensalmente com Sucupira

---

## 📊 Totalização Final Esperada

| Tipo | CAPES DS | CAPES IES | Total |
|------|----------|-----------|-------|
| **Mestrado** | 263 | 10 | **273** |
| **Doutorado** | 151 | 6 | **157** |
| **TOTAL** | **414** | **16** | **430** |

**Diferença 430 vs 429:** Pode haver 1 bolsista adicional ou erro de contagem na Plataforma Sucupira.

---

## 🔧 Scripts Disponíveis

- `verificar_bolsas_ies.py` - Verifica bolsistas IES cadastrados
- `atualizar_cotas_capes_mestrado.py` - Atualiza cotas CAPES DS Mestrado
- `atualizar_cotas_capes_doutorado.py` - Atualiza cotas CAPES DS Doutorado

---

**Observação Técnica:**

As bolsas IES são rotativas da PROPPG. Quando um bolsista IES é vinculado a um programa temporariamente, ele deve ser cadastrado no sistema com:
- `agencia_fomento = 'CAPES IES'`
- `programa_id` = programa temporário
- `edital_id = 14` (CAPES DS)

Isso permite rastreamento completo mantendo diferenciação entre CAPES DS (fixo) e CAPES IES (rotativo).
