@echo off
REM Aviso ultimo mes de bolsa — bolsista + orientador (idempotente por competencia).
cd /d "%~dp0.."
set FLASK_APP=app.py
call venv\Scripts\activate.bat
flask aviso-ultimo-mes-bolsa
