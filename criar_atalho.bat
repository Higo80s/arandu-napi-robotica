@echo off
REM Script para criar atalho no Desktop

setlocal enabledelayedexpansion

echo Criando atalho no Desktop...

set "DESKTOP=%USERPROFILE%\Desktop"
set "TARGET=C:\Users\higosantos\Documents\gestao_editais\arandu-napi-robotica\launch_with_postgres.bat"
set "SHORTCUT=%DESKTOP%\Arandú Napi-Robótica.lnk"

REM Criar atalho usando PowerShell (mais confiável)
powershell -NoProfile -Command ^
    "$WshShell = New-Object -ComObject WScript.Shell; " ^
    "$Shortcut = $WshShell.CreateShortcut('%SHORTCUT%'); " ^
    "$Shortcut.TargetPath = '%TARGET%'; " ^
    "$Shortcut.WorkingDirectory = '%cd%'; " ^
    "$Shortcut.Save()" 

if errorlevel 1 (
    echo ERRO: Falha ao criar atalho
    pause
    exit /b 1
)

echo ✓ Atalho criado: !SHORTCUT!
echo.
echo Você pode clicar duplo no atalho para iniciar a aplicação.
echo.
pause
