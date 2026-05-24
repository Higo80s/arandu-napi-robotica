
@echo off
REM Gestao de Editais - Launcher Corrigido
cd /d "%~dp0"

echo Verificando ambiente...
if exist ".venv\Scripts\pythonw.exe" (
    echo Ambiente encontrado. Iniciando sistema...
    start "" ".venv\Scripts\pythonw.exe" "production.py"
    exit
) else (
    echo.
    echo [ERRO] Ambiente Python nao encontrado em: %~dp0.venv\Scripts\pythonw.exe
    echo Verifique se a pasta .venv existe.
    echo.
    pause
)
