@echo off
REM Confirmacao de inicio de bolsa — rede de seguranca (ativos sem e-mail).
cd /d "%~dp0.."
set FLASK_APP=app.py
call venv\Scripts\activate.bat
flask confirmacao-inicio-bolsa
