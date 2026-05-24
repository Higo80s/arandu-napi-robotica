Adendo: migration v3, prefill e agendador

- Migration v3: use `python atualizar_banco_v3.py` para criar a tabela `acompanhamento`.
- Script `prefill_acompanhamento.py`: pré-cria linhas de acompanhamento para o mês atual para todos os bolsistas `ativo`.
  - Útil para automatizar via Task Scheduler (Windows) — agende `python C:\caminho\para\gestao_editais\prefill_acompanhamento.py` mensalmente.
- `requirements.txt` já presente com versões. Instale com `pip install -r requirements.txt`.

Notas de compatibilidade

- Os scripts usam `ON CONFLICT` quando disponível; existe fallback para versões antigas do SQLite.
- O app continua sendo desktop — o prefill facilita trazer registros mensais sem abrir a UI.
