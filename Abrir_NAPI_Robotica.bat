@echo off
REM ============================================================
REM  ARANDÚ NAPI-ROBÓTICA — Atalho do Desktop 
REM  Este atalho: (1) garante que o servidor está rodando
REM               (2) abre o navegador na URL correta
REM ============================================================

set VBS_PATH=C:\Users\higosantos\Documents\gestao_editais\arandu-napi-robotica\napi_iniciar_invisivel.vbs
set URL=http://127.0.0.1:5005

REM Inicia o servidor (caso ainda não esteja rodando)
start "" wscript.exe "%VBS_PATH%"

REM Aguarda 3 segundos para o servidor iniciar
timeout /t 3 /nobreak >nul

REM Abre o navegador padrão
start "" "%URL%"
