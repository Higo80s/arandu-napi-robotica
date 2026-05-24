@echo off
REM ======================================
REM MENU PRINCIPAL - Gestão de Editais
REM ======================================

setlocal enabledelayedexpansion

:menu
cls
echo.
echo ╔═════════════════════════════════════════════════════════╗
echo ║                                                         ║
echo ║          GESTAO DE EDITAIS - MENU PRINCIPAL            ║
echo ║                                                         ║
echo ║            Versão 7.0 (PostgreSQL)                    ║
echo ║                                                         ║
echo ╚═════════════════════════════════════════════════════════╝
echo.

echo  📊 AÇÕES DISPONÍVEIS:
echo.
echo   [1] ⭐ INICIAR APLICAÇÃO
echo       (Inicia PostgreSQL + Restaura Backup + App)
echo.
echo   [2] 🔄 RESTAURAR BACKUP MANUALMENTE
echo       (Apenas restaura dados PostgreSQL)
echo.
echo   [3] ✓ VERIFICAR PRÉ-REQUISITOS
echo       (Checa Python, PostgreSQL, etc)
echo.
echo   [4] 🔗 CRIAR ATALHO NO DESKTOP
echo       (Adiciona atalho para acesso rápido)
echo.
echo   [5] 📖 ABRIR DOCUMENTAÇÃO
echo       (Guia completo de setup)
echo.
echo   [6] 🌍 ABRIR APLICAÇÃO (se já rodando)
echo       (Abre http://localhost:5000)
echo.
echo   [7] 🛑 PARAR POSTGRESQL
echo       (Encerra serviço PostgreSQL)
echo.
echo   [0] ✗ SAIR
echo.

set /p choice="Digite a opção (0-7): "

if "!choice!"=="1" (
    goto opcao_iniciar
) else if "!choice!"=="2" (
    goto opcao_restaurar
) else if "!choice!"=="3" (
    goto opcao_verificar
) else if "!choice!"=="4" (
    goto opcao_atalho
) else if "!choice!"=="5" (
    goto opcao_docs
) else if "!choice!"=="6" (
    goto opcao_abrir
) else if "!choice!"=="7" (
    goto opcao_parar
) else if "!choice!"=="0" (
    echo.
    echo Até logo!
    timeout /t 2 >nul
    exit /b 0
) else (
    echo.
    echo ✗ Opção inválida!
    timeout /t 2 >nul
    goto menu
)

REM ========================
REM OPÇÃO 1: INICIAR APP
REM ========================
:opcao_iniciar
cls
echo.
echo ⭐ INICIANDO APLICAÇÃO...
echo.
call launch_with_postgres.bat
goto menu

REM ========================
REM OPÇÃO 2: RESTAURAR
REM ========================
:opcao_restaurar
cls
echo.
echo 🔄 RESTAURANDO BACKUP...
echo.
python restore_backup_postgres.py
echo.
pause
goto menu

REM ========================
REM OPÇÃO 3: VERIFICAR
REM ========================
:opcao_verificar
cls
echo.
echo ✓ VERIFICANDO PRÉ-REQUISITOS...
echo.
call verificar_setup.bat
goto menu

REM ========================
REM OPÇÃO 4: ATALHO
REM ========================
:opcao_atalho
cls
echo.
echo 🔗 CRIANDO ATALHO NO DESKTOP...
echo.
call criar_atalho.bat
goto menu

REM ========================
REM OPÇÃO 5: DOCUMENTAÇÃO
REM ========================
:opcao_docs
cls
echo.
echo 📖 ABRINDO DOCUMENTAÇÃO...
echo.
if exist RESTAURACAO_POSTGRES.md (
    start notepad RESTAURACAO_POSTGRES.md
) else (
    echo ✗ Arquivo RESTAURACAO_POSTGRES.md não encontrado
    pause
)
goto menu

REM ========================
REM OPÇÃO 6: ABRIR WEB
REM ========================
:opcao_abrir
cls
echo.
echo 🌍 ABRINDO APLICAÇÃO...
echo.
echo   Acessando: http://localhost:5000
echo.
start http://localhost:5000
echo   ✓ Navegador aberto
echo.
pause
goto menu

REM ========================
REM OPÇÃO 7: PARAR POSTGRESQL
REM ========================
:opcao_parar
cls
echo.
echo 🛑 PARANDO POSTGRESQL...
echo.
net stop postgresql-x64-17 >nul 2>&1
if errorlevel 1 (
    net stop postgresql-x64-16 >nul 2>&1
)
if errorlevel 1 (
    echo ✗ Erro ao parar PostgreSQL
) else (
    echo ✓ PostgreSQL parado
)
echo.
pause
goto menu
