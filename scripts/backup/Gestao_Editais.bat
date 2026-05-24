@echo off
REM Gestao de Editais - Launcher
REM Inicia o sistema garantindo funcionalidade
cd /d "%~dp0"

if exist ".venv\Scripts\pythonw.exe" (
    start "" wscript.exe "run_hidden.vbs" ".venv\Scripts\pythonw.exe" "production.py"
) else (
    echo Ambiente Python nao encontrado.
    pause
)
