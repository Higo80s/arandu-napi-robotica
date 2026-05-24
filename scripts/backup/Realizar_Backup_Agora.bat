@echo off
cd /d "%~dp0"

echo ==========================================
echo      Backup Gestao de Editais
echo ==========================================

:: Verificar se o venv existe
if not exist ".venv\Scripts\python.exe" (
    echo Erro: Ambiente virtual nao encontrado.
    echo Por favor, configure o ambiente primeiro.
    pause
    exit /b
)

:: Instalar dependencias se necessario (em background seria melhor, mas aqui garantir eh bom)
echo Verificando dependencias do backup...
.venv\Scripts\pip install -r requirements_backup.txt > nul 2>&1

:: Executar script
echo Executando script de backup...
.venv\Scripts\python backup_system.py

echo.
echo Concluido.
pause
