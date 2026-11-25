# Plano — NAPI Robótica

Fonte de escopo: `.cursor/rules/escopo-vs-proppg.mdc`. Modelo Flask: `../arandu_proppg`.

## Próximo incremento

Tirar PROAP da navegação, do formulário/serviço de edital e desregistrar `blueprints/proap.py`. Teste: edital salva sem `proap_distribuicao_id`; menu não aponta para Recursos. Tabelas `proap_*` ficam no banco até migration com backup — não dropar no mesmo passo.

Depois, na mesma leva de limpeza: cortar redirect `posdoc.novo` / `posdoc_index` e o blueprint `profissionais` não registrado.
