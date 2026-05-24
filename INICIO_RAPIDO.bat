@echo off
REM ════════════════════════════════════════════════════════════════
REM  INICIO RAPIDO - Gestão de Editais com PostgreSQL
REM  Clique duplo neste arquivo para começar!
REM ════════════════════════════════════════════════════════════════

setlocal enabledelayedexpansion

cls
title Gestao de Editais - Inicio Rapido

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║        🚀 GESTAO DE EDITAIS - INICIO RAPIDO 🚀            ║
echo ║                                                            ║
echo ║           PostgreSQL + Flask v7.0                        ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo Bem-vindo! Este script vai iniciar tudo para você.
echo.
echo Etapas:
echo   1. Verificar PostgreSQL
echo   2. Restaurar backup (se necessário)
echo   3. Instalar dependências Python
echo   4. Iniciar aplicação
echo   5. Abrir navegador
echo.
echo ⏳ Aguarde... (será rápido!)
echo.
timeout /t 2

REM 1. Verificar e iniciar PostgreSQL
echo [1/5] Inicializando PostgreSQL...

tasklist | find /i "postgres" >nul 2>&1
if errorlevel 1 (
    echo   ⏳ PostgreSQL não está rodando. Iniciando...
    
    net start postgresql-x64-17 >nul 2>&1
    if errorlevel 1 (
        net start postgresql-x64-16 >nul 2>&1
    )
    
    if errorlevel 1 (
        echo   ✗ ERRO ao iniciar PostgreSQL
        echo.
        echo   Por favor, inicie manualmente:
        echo   1. Abra Services (services.msc)
        echo   2. Procure "postgresql"
        echo   3. Clique direito e "Start"
        echo.
        pause
        exit /b 1
    )
    timeout /t 2
)

echo   ✓ PostgreSQL OK
echo.

REM 2. Verificar banco de dados
echo [2/5] Verificando banco de dados...

python -c "import psycopg2; psycopg2.connect(host='localhost', port='5432', user='gestao_user', password='gestao_password', database='gestao_editais_db')" >nul 2>&1

if errorlevel 1 (
    echo   ⏳ Banco não encontrado. Restaurando backup...
    
    if not exist backup_pre_auth_20260129_010726.zip (
        echo   ✗ ERRO: backup_pre_auth_20260129_010726.zip não encontrado
        pause
        exit /b 1
    )
    
    python restore_backup_postgres.py
    if errorlevel 1 (
        echo   ✗ ERRO ao restaurar backup
        pause
        exit /b 1
    )
) else (
    echo   ✓ Banco de dados acessível
)

echo.

REM 3. Instalar dependências
echo [3/5] Verificando dependências Python...

python -c "import flask; import flask_sqlalchemy; import psycopg2; import dotenv" >nul 2>&1

if errorlevel 1 (
    echo   ⏳ Instalando dependências...
    pip install -q -r requirements.txt >nul 2>&1
)

echo   ✓ Dependências OK
echo.

REM 4. Iniciar aplicação
echo [4/5] Iniciando aplicação Flask...
echo   ⏳ Aguarde alguns segundos...
echo.

start http://localhost:5000

echo ════════════════════════════════════════════════════════════
echo [5/5] ✅ APLICACAO INICIADA COM SUCESSO!
echo ════════════════════════════════════════════════════════════
echo.
echo 🌐 Abra no navegador: http://localhost:5000
echo.
echo 📊 Dados: Restaurados do backup
echo 🐘 Banco: PostgreSQL (gestao_editais_db)
echo 🚀 App: Flask 3.1.2 - Rodando em http://localhost:5000
echo.
echo Para parar: Feche esta janela
echo.
echo ════════════════════════════════════════════════════════════
echo.

python app.py

echo.
echo ✓ Obrigado por usar Gestão de Editais!
echo.
pause
