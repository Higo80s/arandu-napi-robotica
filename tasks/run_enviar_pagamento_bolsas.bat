@echo off
REM Folha Pagamento de Bolsas → Nuvem. Agendar DIARIO (08:15).
REM Publica a partir do dia 20; se o PC estava off, faz catch-up na proxima execucao.
cd /d "%~dp0.."
set FLASK_APP=app.py
"%~dp0..\venv\Scripts\python.exe" -m flask enviar-pagamento-bolsas
