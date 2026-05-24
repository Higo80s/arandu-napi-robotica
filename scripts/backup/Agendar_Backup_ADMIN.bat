@echo off
echo Solicitando permissoes de Administrador...
powershell -Command "Start-Process powershell -ArgumentList '-ExecutionPolicy Bypass -File \"%~dp0Configurar_Agendamento.ps1\"' -Verb RunAs"
echo.
echo Se uma janela de confirmacao apareceu, clique em SIM.
echo.
pause
