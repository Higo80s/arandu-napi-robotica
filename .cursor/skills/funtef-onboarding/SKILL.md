---
name: funtef-onboarding
description: Fluxo de onboarding FUNTEF/Conveniar no Arandu NAPI-Robotica. Use ao cadastrar bolsistas, configurar e-mails FUNTEF, ou implementar notificacoes pos-cadastro.
---

# FUNTEF / Conveniar — NAPI-Robotica

## Fluxo operacional

1. Coordenador publica edital com lista de aprovados.
2. Operador monta pasta na Nuvem com documentacao assinada.
3. Operador cadastra o bolsista no Conveniar (acao externa).
4. No Arandu, aba Vigencia e Bolsa: stepper FUNTEF etapa 1 — marcar Conveniar + link da Nuvem + **Atualizar Cadastro**.
5. Sistema envia e-mail automatico a FUNTEF (etapa 2; uma vez; nao exige contrato pronto).
6. Ao retorno do contrato, marcar etapa 3 (Contrato FUNTEF pronto) + Atualizar Cadastro.
7. Etapa 4: Ativar Bolsista (Fundação) — so apos etapas 1-3.
   - Informe a data de liberacao da Fundação.
   - O sistema mostra a previa do e-mail de confirmacao (inicio, fim, parcelas).
   - Confirme para ativar e enviar ao bolsista + orientador (ou desmarque o envio).
   - Reenvio manual na ficha; tarefa diaria cobre ativos implantados sem o e-mail.

## UI na ficha

Na edicao (`/bolsistas/<id>/editar`), aba **Vigência & Bolsa**, bloco `#funtefStepper`:

- Trilho 1–4 (Nuvem → E-mail → Contrato → Ativar) com estados feito / atual / bloqueado.
- Etapa atual derivada de `conveniar_cadastrado` + `link_pasta_nuvem`, `funtef_email_enviado_em`, `funtef_contrato_pronto`, `implantacao_pendente`.
- Checkbox contrato desabilitado ate o e-mail FUNTEF.
- Checkout de relatorio final fica fora do stepper.

Estilos: `static/css/styles.css` (classe `.funtef-stepper`).

## E-mail FUNTEF

Template `templates/emails/funtef_verificacao.html` inclui:

- Projeto/edital: numero, **numero_convenio**, **coordenador_geral_proppg**, SEI
- Bolsista: nome, CPF, nascimento, e-mail, telefone, modalidade, valor parcela, qtd parcelas, inicio, termino, orientador

Campos novos no bolsista: `data_nascimento`, `telefone`. Valor da parcela vem da `modalidade.valor_mensal`.

## Arquivos

- `services/funtef_onboarding_service.py`
- `templates/bolsistas/form.html` (stepper + dados pessoais)
- `templates/emails/funtef_verificacao.html`
- `/admin/config-funtef` — destinatarios editaveis
- `scripts/migrate_funtef_onboarding.py`
