@echo off
REM ========================================
REM Gestao de Editais - Boot System
REM ========================================

cd /d "%~dp0"

echo [%DATE% %TIME%] Booting... > app.log

REM Check Environment
if not exist ".venv\Scripts\python.exe" (
    echo [%DATE% %TIME%] FATAL: Venv missing >> app.log
    exit /b 1
)

echo [%DATE% %TIME%] Starting Server... >> app.log

REM Run
".venv\Scripts\python.exe" production.py >> app.log 2>&1

echo [%DATE% %TIME%] Server Stopped. >> app.log
