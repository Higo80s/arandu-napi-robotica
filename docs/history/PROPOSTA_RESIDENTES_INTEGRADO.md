# Análise e Proposta: Gestão Integrada de Residentes Pós-Doutorais

**Data:** 31/01/2026  
**Problema Identificado:** Potencial duplicação entre registros de residentes no módulo `/posdoc` e vinculação ao Edital 21 para contabilização financeira.

---

## 🔍 Situação Atual

### Estrutura Existente

O modelo `Residente` já está bem projetado com:

✅ **Campo `recebe_bolsa`** (Boolean) - Diferencia bolsistas de voluntários  
✅ **Campo `valor_bolsa`** (Float, opcional) - Valor personalizado da bolsa  
✅ **Campo opcional `edital_id`** - Permite vínculo com qualquer edital (incluindo Edital 21)  
✅ **Campo opcional `modalidade_id`** - Permite vínculo com modalidade de bolsa  
✅ **Campos `tem_adicional`, `valor_adicional`** - Para parcelas extras

### Problema Potencial

**Cenário de Risco:**
1. Residente bolsista é cadastrado em `/posdoc` com `recebe_bolsa=True` e `valor_bolsa=5000`
2. **MAS** não está vinculado a nenhum edital (`edital_id=NULL`)
3. **RESULTADO:** O valor da bolsa **NÃO é contabilizado** nos relatórios financeiros que somam apenas bolsistas vinculados a editais

**Cenário de Duplicação:**
1. Residente cadastrado em `/posdoc` 
2. Mesmo residente cadastrado novamente vinculado ao "Edital 21"
3. **RESULTADO:** Dupla contagem ou dados inconsistentes

---

## ✅ Proposta de Solução: Arquitetura Unificada

### Opção 1: **Vínculo Obrigatório para Bolsistas** (Recomendada ⭐)

**Regra de Negócio:**
- Se `recebe_bolsa = True` → `edital_id` é **obrigatório**
- Se `recebe_bolsa = False` (voluntário) → `edital_id` permanece **opcional**

**Implementação:**
1. **Validação no Formulário** (`posdoc/form.html`):
   ```javascript
   // Se marcar "Recebe Bolsa", campo "Edital" torna-se obrigatório
   document.getElementById('recebe_bolsa').addEventListener('change', function() {
       document.getElementById('edital_id').required = this.checked;
   });
   ```

2. **Validação no Backend** (`app.py`):
   ```python
   if request.form.get('recebe_bolsa') == 'on':
       if not request.form.get('edital_id'):
           flash('Residentes bolsistas devem ser vinculados a um edital!', 'error')
           return redirect(...)
   ```

3. **Criação de Edital Genérico "Pós-Doc"** (se não existir Edital 21):
   - Número: 21 (ou outro)
   - Descrição: "Residência Pós-Doutoral - Geral"
   - Modalidades incluem valores típicos de pós-doc (ou valores personalizados via `valor_bolsa`)

**Vantagens:**
- ✅ Todos os bolsistas são contabilizados automaticamente
- ✅ Não há duplicação (CPF único garante)
- ✅ Relatórios financeiros incluem residentes automaticamente
- ✅ Mantém flexibilidade para voluntários (sem edital)

---

### Opção 2: **Contabilização Alternativa** (Menos Recomendada)

Modificar relatórios financeiros para incluir residentes com `recebe_bolsa=True` **mesmo sem edital vinculado**.

**Implementação:**
```python
# Em relatórios financeiros
total_bolsas_residentes = db.session.query(
    db.func.sum(Residente.valor_bolsa)
).filter(
    Residente.recebe_bolsa == True,
    Residente.ativo == True
).scalar() or 0
```

**Desvantagens:**
- ❌ Lógica duplicada em vários relatórios
- ❌ Risco de esquecer de incluir em novos relatórios
- ❌ Sem rastreabilidade de qual "edital" financia

---

## 🎯 Recomendação Final

**Adotar Opção 1** com as seguintes ações:

### Ação 1: Validação de Formulário
- Tornar `edital_id` obrigatório quando `recebe_bolsa=True`
- Mensagem clara: *"Bolsistas devem ser vinculados a um edital para contabilização"*

### Ação 2: Criar/Verificar Edital 21
- Se não existir, criar Edital genérico para pós-doc
- Modalidades: "Pós-Doc Nacional", "Pós-Doc Internacional", etc.
- Valores padrão ou permitir personalização via `valor_bolsa`

### Ação 3: Migração de Dados (se necessário)
```python
# Script para vincular residentes bolsistas existentes ao Edital 21
residentes_sem_edital = Residente.query.filter(
    Residente.recebe_bolsa == True,
    Residente.edital_id == None
).all()

edital_21 = Edital.query.filter_by(numero=21).first()

for r in residentes_sem_edital:
    r.edital_id = edital_21.id
    
db.session.commit()
```

### Ação 4: Atualizar Relatórios
- Incluir flag visual nos relatórios: "Residente Pós-Doutoral" vs "Discente"
- Separar contabilização:
  - Bolsistas Discentes (Graduação, Mestrado, Doutorado)
  - Bolsistas Pós-Doc (Residentes)
  - Voluntários Pós-Doc

---

## 📊 Estrutura Final

```
Residentes Cadastrados (/posdoc)
│
├─ Voluntários (recebe_bolsa=False, edital_id=NULL)
│  └─ Apenas registro acadêmico, sem contabilização financeira
│
└─ Bolsistas (recebe_bolsa=True, edital_id=OBRIGATÓRIO)
   ├─ Vinculados ao Edital 21 (ou outro específico)
   └─ Contabilizados automaticamente em relatórios financeiros
```

---

## 🌸 Conclusão da Equipe Yoko

> "A arquitetura atual já suporta gestão integrada. Precisamos apenas adicionar **validação de vínculo obrigatório** para bolsistas e garantir que o Edital 21 (ou equivalente) exista. Isso elimina duplicação e garante contabilização correta sem criar tabelas ou lógicas adicionais."

**Implementar Opção 1 leva ~20 minutos** e resolve definitivamente o problema.

**Decisão Necessária:**
- Higo, posso prosseguir com a implementação da Opção 1?
- Confirmar se o "Edital 21" já existe ou precisa ser criado?
