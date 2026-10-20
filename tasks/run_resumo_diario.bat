@echo off
REM Resumo diario: tarefas /anotacoes/ + alertas — agendar no Windows (ex.: 08:00).
cd /d "%~dp0.."
set FLASK_APP=app.py
call venv\Scripts\activate.bat
flask send-daily-digest
