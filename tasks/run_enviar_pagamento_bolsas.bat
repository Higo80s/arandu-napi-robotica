@echo off
REM Envia folha Pagamento de Bolsas para a Nuvem (dia 20 de cada mes).
cd /d "%~dp0.."
set FLASK_APP=app.py
"%~dp0..\venv\Scripts\python.exe" -m flask enviar-pagamento-bolsas
