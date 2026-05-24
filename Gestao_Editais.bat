@echo off
REM ======================================================
REM   GESTAO DE EDITAIS - LAUNCHER ORIGINAL
REM   Inicia servidor + Splash Loader HTML
REM ======================================================

cd /d "%~dp0"

REM Verifica se o ambiente virtual existe
if not exist "venv\Scripts\python.exe" (
    echo [ERRO] Ambiente Python nao encontrado!
    echo Verifique se a pasta .venv existe em:
    echo %~dp0
    pause
    exit /b 1
)

REM 1. Inicia o servidor Flask em segundo plano (oculto)
echo Iniciando servidor Flask...
start /B "" "venv\Scripts\pythonw_robotica.exe" "app.py"

REM 2. Abre imediatamente o Splash Loader no navegador
REM O arquivo splash_loader.html vai aguardar o servidor subir e redirecionar
echo Abrindo Splash Screen...
start "" "splash_loader.html"

REM O script bat termina aqui, mas o servidor continua rodando em background
exit
