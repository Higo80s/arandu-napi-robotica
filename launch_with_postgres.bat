@echo off
REM ======================================
REM LAUNCHER - Gestão de Editais + PostgreSQL
REM ======================================
REM Este script inicia a aplicação com PostgreSQL configurado

setlocal enabledelayedexpansion

echo.
echo ========================================
echo   GESTAO DE EDITAIS v7.0 - PostgreSQL
echo ========================================
echo.

REM 1. Verificar se PostgreSQL está rodando
echo [1/4] Verificando PostgreSQL...
tasklist | find /i "postgres" >nul 2>&1

if errorlevel 1 (
    echo   AVISO: PostgreSQL não está em execução
    echo   Iniciando PostgreSQL...
    
    REM Tentar iniciar serviço PostgreSQL (Windows)
    net start postgresql-x64-17 >nul 2>&1
    if errorlevel 1 (
        net start postgresql-x64-16 >nul 2>&1
    )
    if errorlevel 1 (
        echo.
        echo   ERRO: Não consegui iniciar PostgreSQL.
        echo   Por favor, inicie manualmente:
        echo     1. Abra Services (services.msc)
        echo     2. Procure por "postgresql"
        echo     3. Clique com botão direito e "Start"
        echo.
        pause
        exit /b 1
    )
    echo   ✓ PostgreSQL iniciado
    timeout /t 3
) else (
    echo   ✓ PostgreSQL já está rodando
)

REM 2. Verificar e restaurar banco se necessário
echo.
echo [2/4] Verificando banco de dados...

python -c "import psycopg2; psycopg2.connect(host='localhost', port='5432', user='postgres', password='admin123', database='arandu_napi_robotica')" >nul 2>&1

if errorlevel 1 (
    echo   ERRO: Banco de dados 'arandu_napi_robotica' nao encontrado ou inacessivel.
    echo   Por favor, verifique se o script de criacao do banco foi executado.
    pause
    exit /b 1
) else (
    echo   ✓ Banco de dados acessível
)

REM 3. Verificar e instalar dependências Python
echo.
echo [3/4] Verificando dependências Python...

python -c "import flask; import flask_sqlalchemy; import psycopg2; import dotenv" >nul 2>&1

if errorlevel 1 (
    echo   Instalando dependências...
    pip install -q -r requirements.txt
    if errorlevel 1 (
        echo   ERRO: Falha ao instalar dependências
        pause
        exit /b 1
    )
)
echo   ✓ Dependências OK

REM 4. Iniciar aplicação
echo.
echo [4/4] Iniciando aplicação...
echo.
echo   =========================================
echo   Aplicação rodando em: http://localhost:5005
echo   =========================================
echo.


python app.py

pause
