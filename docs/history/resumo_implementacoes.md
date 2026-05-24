# Resumo das Implementações - Fase 2

## 1. Campo "Início Curso" - Já é Opcional ✅

Verificação feita:
- Linha 564 app.py: já trata com `if request.form['data_inicio_curso'] else None`
- Linha 695: mesma lógica
- Linha 760: mesma lógica

**Ação:** Nenhuma necessária, já funcional!

## 2. Popup de Pendências - IMPLEMENTAR

**Objetivo:** Ao abrir edição de bolsista, mostrar modal com campos vazios

**Implementação:**
- Adicionar JavaScript em `templates/bolsistas/form.html`
- Modal Bootstrap
- Verificar campos obrigatórios vazios
- Exibir apenas ao carregar modo edição (não em novo)

## 3. Toggle Ativo com Memória - IMPLEMENTAR

**Problema:** Ao desmarcar "ativo", perde data_fim_bolsa anterior

**Solução:**
- Adicionar campo `data_fim_bolsa_backup` no modelo
- Migração do banco
- Lógica de salvamento/restauração no app.py

## 4. Colunas SEI e Formulário - IMPLEMENTAR

**Campos existentes:**
- processo_sei ✅
- numero_formulario ✅

**Ação:**
- Adicionar colunas em `templates/bolsistas/index.html`
- Testar proporcionalidade da tabela

## Scripts Criados

1. verificar_issues_sistema.py ✅
2. corrigir_ppgmat_duplicata.py ✅
3. corrigir_ppgcem_triplicata.py ✅
4. veri ficar_ppgfcet.py ✅
