@echo off
REM ========================================
REM Gestao de Editais - Stop Server
REM ========================================
REM Para o servidor de producao
REM ========================================

echo ========================================
echo Parando servidor Gestao de Editais...
echo ========================================
echo.

REM Mata todos os processos Python relacionados ao production.py
taskkill /F /IM pythonw.exe /FI "WINDOWTITLE eq production.py" 2>nul
taskkill /F /IM python.exe /FI "WINDOWTITLE eq production.py" 2>nul

REM Tenta matar processos Python na porta 5000
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5002" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a 2>nul
)

echo.
echo Servidor encerrado!
echo.

timeout /t 3
