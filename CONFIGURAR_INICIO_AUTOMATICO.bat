@echo off
REM ============================================================
REM  ARANDÚ NAPI-ROBÓTICA — Configurador de Inicialização Automática
REM  Execute este arquivo UMA VEZ como Administrador.
REM  Após isso, o sistema iniciará automaticamente no login do Windows.
REM ============================================================

echo.
echo  =============================================
echo   ARANDU NAPI-ROBOTICA - Configurando Auto-Start
echo  =============================================
echo.

set VBS_PATH=C:\Users\higosantos\Documents\gestao_editais\arandu-napi-robotica\napi_iniciar_invisivel.vbs
set TASK_NAME=AranduNapiRobotica

echo [1] Removendo tarefa antiga (se existir)...
schtasks /delete /tn "%TASK_NAME%" /f >nul 2>&1

echo [2] Criando nova tarefa de inicializacao automatica...
schtasks /create /tn "%TASK_NAME%" /tr "wscript.exe \"%VBS_PATH%\"" /sc ONLOGON /ru "%USERNAME%" /rl HIGHEST /f

if %ERRORLEVEL% == 0 (
    echo.
    echo  =============================================
    echo   SUCESSO! O sistema agora vai iniciar
    echo   automaticamente toda vez que voce logar
    echo   no Windows. Sem janela preta!
    echo  =============================================
    echo.
    echo  Iniciando o servidor agora pela primeira vez...
    start "" wscript.exe "%VBS_PATH%"
    echo  Aguardando 5 segundos para o servidor subir...
    timeout /t 5 /nobreak >nul
    echo  Abrindo o navegador...
    start "" "http://127.0.0.1:5005"
) else (
    echo.
    echo  [ERRO] Falha ao criar tarefa agendada.
    echo  Tente executar este arquivo como Administrador:
    echo  Clique com botao direito - "Executar como Administrador"
    echo.
)

pause
