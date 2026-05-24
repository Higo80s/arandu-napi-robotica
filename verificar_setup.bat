@echo off
REM ======================================
REM PRÉ-VERIFICAÇÃO - Gestão de Editais
REM ======================================

setlocal enabledelayedexpansion

echo.
echo ======================================
echo   PRE-VERIFICACAO - Setup PostgreSQL
echo ======================================
echo.

set "checks=0"
set "warnings=0"

REM 1. Python
echo [1/6] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo   ✗ ERRO: Python não instalado
    echo   → Instale de https://www.python.org/
    set /a warnings=!warnings!+1
) else (
    for /f "tokens=*" %%i in ('python --version') do (
        echo   ✓ %%i
        set /a checks=!checks!+1
    )
)

REM 2. PostgreSQL
echo.
echo [2/6] Verificando PostgreSQL...
tasklist | find /i "postgres" >nul 2>&1
if errorlevel 1 (
    echo   ⚠ PostgreSQL não está rodando (é necessário)
    set /a warnings=!warnings!+1
) else (
    echo   ✓ PostgreSQL está rodando
    set /a checks=!checks!+1
)

REM 3. Arquivo Backup
echo.
echo [3/6] Verificando backup...
if exist backup_pre_auth_20260129_010726.zip (
    for /f "tokens=*" %%i in ('powershell -Command "(Get-Item backup_pre_auth_20260129_010726.zip).Length / 1MB"') do (
        echo   ✓ backup_pre_auth_20260129_010726.zip - %%i MB
        set /a checks=!checks!+1
    )
) else (
    echo   ✗ ERRO: backup_pre_auth_20260129_010726.zip não encontrado
    set /a warnings=!warnings!+1
)

REM 4. .env
echo.
echo [4/6] Verificando configuração...
if exist .env (
    echo   ✓ .env encontrado
    set /a checks=!checks!+1
) else (
    echo   ✗ .env não encontrado
    set /a warnings=!warnings!+1
)

REM 5. requirements.txt
echo.
echo [5/6] Verificando dependências...
if exist requirements.txt (
    echo   ✓ requirements.txt encontrado
    set /a checks=!checks!+1
) else (
    echo   ✗ requirements.txt não encontrado
    set /a warnings=!warnings!+1
)

REM 6. app.py
echo.
echo [6/6] Verificando código...
if exist app.py (
    echo   ✓ app.py encontrado
    set /a checks=!checks!+1
) else (
    echo   ✗ app.py não encontrado
    set /a warnings=!warnings!+1
)

REM Resumo
echo.
echo ======================================
echo   RESUMO: !checks!/6 verificações OK
if !warnings! gtr 0 (
    echo   ⚠ !warnings! avisos
)
echo ======================================
echo.

if !warnings! gtr 0 (
    echo Próximos passos:
    echo   1. Instale PostgreSQL se não tiver
    echo   2. Inicie o serviço PostgreSQL
    echo   3. Execute: python restore_backup_postgres.py
    echo.
)

echo Para iniciar:
echo   → .\launch_with_postgres.bat
echo.

pause
