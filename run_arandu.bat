title Arandu Server (Porta 5000)
echo ====================================================
echo      INICIANDO ARANDU (PORTA 5000)
echo ====================================================
echo.

cd /d "%~dp0"

echo [1] Verificando Ambiente Virtual...
if not exist "venv\Scripts\activate.bat" (
    echo [ERRO] Ambiente virtual (venv) nao encontrado!
    pause
    exit /b 1
)

echo [2] Ativando Ambiente Virtual...
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

echo [3] Iniciando Servidor Flask...
echo.
echo ====================================================
echo O SISTEMA ESTA RODANDO!
echo Acesse no navegador: http://127.0.0.1:5000
echo Para parar o servidor, pressione CTRL+C ou feche esta janela.
echo ====================================================
echo.

set FLASK_APP=app.py
set FLASK_ENV=development
python app.py

pause
