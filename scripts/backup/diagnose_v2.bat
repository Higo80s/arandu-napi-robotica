@echo off
cd /d "%~dp0"
echo ==========================================
echo       MODO DE DIAGNOSTICO DETALHADO
echo ==========================================
echo Iniciando servidor e capturando erros...
echo.

date /t > diag_run.txt
time /t >> diag_run.txt

echo [CMD] Start python production.py >> diag_run.txt
.\.venv\Scripts\python.exe production.py >> diag_run.txt 2>&1

echo [CMD] Exit Code: %errorlevel% >> diag_run.txt

echo ==========================================
echo PROCESSO FINALIZADO
echo ==========================================
echo Se houve erro, ele foi salvo em diag_run.txt
echo.
echo CONTEUDO DO LOG:
type diag_run.txt
echo.
pause
