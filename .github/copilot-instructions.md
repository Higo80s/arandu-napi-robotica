# Copilot / AI Agent Instructions — Gestão de Editais

This project is a small desktop application (Tkinter) that manages research funding calls (editais) and scholarship holders (bolsistas) using a local SQLite database. Use these notes to make targeted, repository-specific code changes.

- **Entry point:** `app.py` launches the GUI (`ThemedTk` from `ttkthemes`). Treat it as the main application to inspect UI flows and DB usage.
- **Schema creation & migrations:** `criar_banco.py` creates `gestao_editais.db`. `atualizar_banco_v2.py` demonstrates a simple migration (adds `data_inicio_curso`). Always prefer adding migration scripts when changing schema.
- **Database file location:** The app uses `gestao_editais.db` located next to the scripts (`os.path.join(os.path.dirname(__file__), 'gestao_editais.db')`). When running scripts, run them from the project folder or ensure paths are resolved relative to the file.

- **Dependencies to install before running:**
  - `ttkthemes` (GUI theme) and `python-dateutil` (relativedelta). Example:

```powershell
pip install ttkthemes python-dateutil
```

- **Run / developer workflows:**
  - Create DB (one-time): `python criar_banco.py`
  - Run migrations (if needed): `python atualizar_banco_v2.py`
  - Launch app: `python app.py`

- **Data model & conventions**
  - Dates: stored in the DB as ISO strings `YYYY-MM-DD`. UI shows/accepts dates in `DD/MM/YYYY`. Use `converter_data_br_para_iso` and `converter_data_iso_para_br` in `app.py` for conversions.
  - Status: `bolsistas.status` uses a CHECK constraint and accepts `'ativo'`, `'desligado'`, `'substituido'` (see `criar_banco.py`).
  - Monetary values: stored as `REAL` in `modalidades.valor_mensal`. UI displays with `R$ {value:.2f}`.
  - Foreign keys: `modalidades.edital_id` and `bolsistas.edital_id` reference `editais.id` and rely on cascade delete.

- **Common SQL / code patterns to follow**
  - Use parameterized queries (already used here): `cursor.execute(sql, (param1, param2))` — follow this pattern when modifying or adding DB access.
  - Lookup pattern for `edital_id` from `numero_edital` (example in `cadastrar_modalidade`):

```py
cursor.execute("SELECT id FROM editais WHERE numero_edital = ?", (edital_numero,))
```

- **UI patterns & interactions**
  - Comboboxes load data from DB via `carregar_editais_para_combo()` and friends. When adding new editais, call these loader functions to refresh UI state.
  - Treeviews: `tree_bolsistas` supports double-click editing (see `editar_bolsista_selecionado`). When changing fields programmatically, call `carregar_dados_consulta()` to refresh listings.

- **Validation & error handling**
  - The GUI shows validation errors via `messagebox.showerror`/`showinfo` and prevents invalid inserts (e.g., date formats, numeric checks). Mirror these user-facing validations in any API or automation scripts to keep behavior consistent.

- **Gotchas & repo-specific notes (observed issues)**
  - There is a nested/indented function block inside `app.py` (the `abrir_janela_edicao_bolsista` function appears indented under `editar_bolsista_selecionado`). Be careful when editing — fix indentation if adding features to the edit dialog.
  - `atualizar_banco_v2.py` uses a naive `ALTER TABLE ADD COLUMN` and handles `OperationalError` for duplicates; follow its simple approach for small schema changes, but add idempotent checks when possible.
  - The app assumes a single-user, local DB. Do not add server-style concurrent DB access without switching to a client-server DB.

- **When adding features**
  - Add migration script to `atualizar_banco_*.py` for any schema change; run it in CI or include instructions in the README.
  - Keep UI validation logic in `app.py` consistent with DB constraints to avoid runtime errors.
  - Reuse helper functions: `converter_data_br_para_iso`, `converter_data_iso_para_br`, `calcular_data_fim_bolsa`.

- **Files to inspect for examples**
  - `app.py` — full UI flows, DB usage, validation, and date helpers.
  - `criar_banco.py` — canonical DB schema and constraints.
  - `atualizar_banco_v2.py` — example migration and pattern for adding columns safely.

If anything in these notes is unclear or you want more examples (e.g., a template migration, unit-test harness, or a small refactor to separate DB logic), tell me which area to expand and I'll update this file.
