from pathlib import Path
p = Path(__file__).resolve().parents[1] / '.github' / 'copilot-instructions.md'
content = r'''# Copilot / AI Agent Instructions — Gestão de Editais

This file gives focused, actionable guidance for an AI coding agent to be productive immediately in this repository.

Key pointers
- **Entry point:** `app.py` — Tkinter GUI using `ttkthemes`. Inspect this file for UI flows, validation, and where UI calls DB helpers.
- **DB & migrations:** `criar_banco.py` creates `gestao_editais.db`. Migration examples are in `atualizar_banco_v2.py`. Add idempotent migration scripts for schema changes.
- **DB path convention:** Always use `os.path.join(os.path.dirname(__file__), 'gestao_editais.db')` to locate the DB. Do not rely on the current working directory.

Run & Dev workflows (PowerShell examples)
- Create DB (one-time):
  ```powershell
  cd C:\Users\higosantos\Documents\gestao_editais
  .\.venv\Scripts\python.exe criar_banco.py
  ```
- Launch app (use the venv to ensure dependencies):
  ```powershell
  cd C:\Users\higosantos\Documents\gestao_editais
  .\.venv\Scripts\python.exe app.py
  ```
- Quick syntax check before packaging:
  ```powershell
  .\.venv\Scripts\python.exe -m py_compile app.py
  ```

Project conventions & patterns
- **DB helpers:** `db.py` centralizes connection, schema creation (`ensure_db_schema()`), and export functions. Use parameterized queries and close connections.
- **Dates:** Stored as ISO `YYYY-MM-DD` in DB; UI accepts/displays `DD/MM/YYYY`. Use `converter_data_br_para_iso` / `converter_data_iso_para_br` in `app.py`.
- **Validation/UI refresh:** Use provided loaders like `carregar_editais_para_combo()` and `carregar_dados_consulta()` after DB changes to refresh UI state.

Integration points & important files
- `db.py`: connection and schema functions, exports (Excel) and helpers; update carefully on schema changes.
- `exportar_excel_mensal.py`: monthly Excel export implementation (uses `openpyxl`).
- Scheduling helpers: scripts that register Windows Task Scheduler jobs — schedule the venv Python explicitly.

Packaging gotchas observed
- Do NOT embed `gestao_editais.db` into a onefile exe (PyInstaller `--add-data` with onefile leads to ephemeral DB copies). Instead: build exe, then copy `gestao_editais.db` into `dist/` next to the exe.
- There were indentation-related SyntaxErrors introduced in `app.py` previously; run a syntax check before packaging.

Dependencies & optional libs
- Required: `ttkthemes`, `python-dateutil`, `openpyxl`. Install these in `.venv`.
- Optional: `reportlab` for PDF export. Prefer to wrap optional imports in try/except and disable UI items when missing.

Tests & validation
- Small test scripts and helpers exist in the repo. Run the syntax check and the small DB tests before packaging.

If you want, I can also:
- Add a runtime fallback in `app.py` to gracefully disable PDF export when `reportlab` is missing.
- Add a short release checklist that copies `gestao_editais.db` into `dist/` after building.

Please tell me which of those you'd like next.
'''
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text(content, encoding='utf-8')
print('WROTE', p)
