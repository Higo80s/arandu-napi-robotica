@echo off
REM ========================================
REM Gestao de Editais - Bootstrapper
REM ========================================
REM Este script prepara o ambiente e inicia o servidor
REM Logs sao salvos em startup.log
REM ========================================

cd /d "%~dp0"

echo [%DATE% %TIME%] Iniciando launcher... > startup.log

REM Verifica python no venv
if not exist ".venv\Scripts\python.exe" (
    echo [%DATE% %TIME%] ERRO: Ambiente virtual nao encontrado em .venv\Scripts\python.exe >> startup.log
    exit /b 1
)

REM Verifica production.py
if not exist "production.py" (
    echo [%DATE% %TIME%] ERRO: production.py nao encontrado >> startup.log
    exit /b 1
)

echo [%DATE% %TIME%] Iniciando production.py... >> startup.log

REM Executa e captura saida
".venv\Scripts\python.exe" production.py >> startup.log 2>&1

if %errorlevel% neq 0 (
    echo [%DATE% %TIME%] ERRO: production.py encerrou com codigo %errorlevel% >> startup.log
) else (
    echo [%DATE% %TIME%] Servidor encerrado normalmente. >> startup.log
)
