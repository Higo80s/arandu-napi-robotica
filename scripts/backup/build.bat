@echo off
echo Atualizando dependências...
call .venv\Scripts\activate.bat
pip install ttkthemes python-dateutil pyinstaller openpyxl reportlab

echo Gerando executável...
pyinstaller --onefile --windowed --name "GestaoEditais" --icon "icon.ico" ^
--collect-all ttkthemes ^
--hidden-import dateutil.relativedelta ^
--add-data "db.py;." ^
app.py

if %ERRORLEVEL% neq 0 (
    echo Erro ao gerar o executavel.
    pause
    exit /b %ERRORLEVEL%
)

echo Copiando banco de dados para dist\
if exist gestao_editais.db (
    copy /Y gestao_editais.db dist\gestao_editais.db >nul
    echo Banco copiado para dist\gestao_editais.db
) else (
    echo AVISO: gestao_editais.db nao encontrado. Crie-o com criar_banco.py primeiro.
)

echo.
echo ✅ CONCLUÍDO!
echo Executável em: dist\GestaoEditais.exe
echo.
echo IMPORTANTE: O banco de dados (gestao_editais.db) deve permanecer na mesma pasta do .exe.
pause