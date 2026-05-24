@echo off
REM ========================================
REM Gestao de Editais - Launcher v2
REM ========================================
REM Este script inicia o servidor de producao
REM do Sistema de Gestao de Editais
REM ========================================

cd /d "%~dp0"

REM Verifica se o ambiente virtual existe
if not exist ".venv\Scripts\python.exe" (
    echo ERRO: Ambiente virtual nao encontrado!
    echo Por favor, execute: python -m venv .venv
    echo E depois: .venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

REM Verifica se production.py existe
if not exist "production.py" (
    echo ERRO: Arquivo production.py nao encontrado!
    pause
    exit /b 1
)

echo ========================================
echo Gestao de Editais - Iniciando...
echo ========================================
echo.
echo O navegador sera aberto automaticamente em http://127.0.0.1:5003
echo.
echo Para encerrar o servidor, pressione CTRL+C
echo.
echo ========================================

REM Inicia o servidor de producao
".venv\Scripts\python.exe" production.py

pause
