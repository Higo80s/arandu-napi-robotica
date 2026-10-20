@echo off

REM Cobranca relatorio final — bolsistas desligados sem checkout (intervalo 15 dias).

cd /d "%~dp0.."

set FLASK_APP=app.py

call venv\Scripts\activate.bat

flask cobranca-relatorio-final

