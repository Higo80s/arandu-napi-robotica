# Análise do Módulo de Residentes (Pós-Doutorado)

## 🔍 Estado Atual

### ✅ O que JÁ existe:
1. **Modelo de Dados Completo** (`models.py` - Classe `Residente`)
   - Campos específicos: `supervisor`, `projeto_pesquisa`, `agencia_fomento`
   - Suporte a cotas adicionais (`tem_adicional`, `valor_adicional`)
   - Valor de bolsa personalizado (`valor_bolsa`)
   - Vínculo com Edital, Modalidade e Programa
   - Status ativo/inativo

### ❌ O que FALTA:
1. **Rotas CRUD** - Não encontradas rotas específicas para:
   - Listar residentes (`/residentes` ou `/posdoc`)
   - Cadastrar novo residente
   - Editar residente
   - Visualizar detalhes

2. **Templates** - Nenhum template dedicado encontrado:
   - `templates/residentes/index.html`
   - `templates/residentes/novo.html`
   - `templates/residentes/editar.html`

3. **Relatórios Específicos** - Sem relatórios customizados para pós-doc

4. **Integração no Menu** - Link "Pós-Doutorado" existe no menu, mas aponta para função inexistente

---

## 💡 Proposta de Melhoria

### Opção A: Implementação Completa (2-3 horas)
**Escopo:**
- Criar rotas CRUD completas (`/residentes/*`)
- Templates responsivos (similar aos de Bolsistas)
- Relatório individual de residente
- Link funcional no menu

**Impacto:** Sistema completo e padronizado

### Opção B: Implementação Mínima Viável (30-45 min)
**Escopo:**
- Rota de listagem básica
- Formulário de cadastro simples
- Aproveitar lógica existente de Bolsistas

**Impacto:** Funcional, mas sem polimento

### Opção C: Adiar para Fase 7 (Pós-Entrega)
**Justificativa:**
- Sistema atual está completo para Bolsistas (foco principal)
- Residentes podem ser gerenciados manualmente no banco até então
- Não impacta entrega imediata

**Impacto:** Zero no cronograma de hoje

---

## 🎯 Recomendação da Equipe Yoko

**Sugestão: Opção B (Implementação Mínima Viável)**

**Justificativa:**
- Completa a funcionalidade sem comprometer entrega
- Aproveita 90% do código de Bolsistas (refatoração)
- Residentes ficam acessíveis via interface
- Tempo estimado: 45 minutos

**Próximos Passos (se aprovado):**
1. Criar blueprint `residentes_bp.py` (ou adicionar rotas no `app.py`)
2. Templates simples (clone de Bolsistas com ajustes)
3. Link funcional no menu

---

## ❓ Decisão Necessária

**Higo, qual opção prefere?**
- **A)** Implementação Completa (investe 2-3h agora)
- **B)** Implementação Mínima (rápida, funcional)
- **C)** Adiar para outra iteração

A equipe está pronta para qualquer caminho! 🌸
