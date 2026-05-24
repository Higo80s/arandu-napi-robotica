@echo off
REM ============================================================
REM  VERIFICADOR: Checar se o venv do NAPI existe
REM  Chamado pelo inicializador invisivel
REM ============================================================
set PROJECT_DIR=C:\Users\higosantos\Documents\gestao_editais\arandu-napi-robotica
set VENV_PYTHON=%PROJECT_DIR%\venv\Scripts\python.exe

cd /d "%PROJECT_DIR%"
"%VENV_PYTHON%" app.py
