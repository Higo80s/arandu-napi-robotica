@echo off
REM Script batch para criar agendamento (execute como Administrador)
REM Clique com botão direito em cmd.exe, selecione "Executar como administrador"
REM Depois execute: criar_agendamento.bat

cd /d "C:\Users\higosantos\Documents\gestao_editais"

echo.
echo ========================================
echo  Criando Agendamento no Task Scheduler
echo ========================================
echo.

REM Verificar se está executando como administrador
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Execute este script como Administrador!
    echo Clique com botao direito em cmd.exe e selecione "Executar como administrador"
    pause
    exit /b 1
)

echo Criando tarefa: Exportar Excel Gestao Editais...
echo.

REM Criar a tarefa
schtasks /create ^
    /tn "Exportar Excel Gestão Editais" ^
    /tr "python.exe \"C:\Users\higosantos\Documents\gestao_editais\exportar_excel_mensal.py\"" ^
    /sc monthly ^
    /d 1 ^
    /st 10:00:00 ^
    /f

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo  SUCESSO! Agendamento criado.
    echo ========================================
    echo.
    echo Detalhes:
    echo   - Nome: Exportar Excel Gestao Editais
    echo   - Frequencia: 1o dia de cada mes
    echo   - Horario: 10:00 AM
    echo.
    echo Verificando tarefa...
    schtasks /query /tn "Exportar Excel Gestão Editais"
    echo.
) else (
    echo.
    echo ERRO ao criar a tarefa!
    echo.
)

pause
