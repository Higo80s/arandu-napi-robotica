' ============================================================
'  ARANDÚ NAPI-ROBÓTICA — Inicializador Invisível
'  Este script inicia o servidor Flask SEM abrir janela preta.
'  Configurado para rodar automaticamente no login do Windows.
' ============================================================

Dim oShell
Set oShell = CreateObject("WScript.Shell")

Dim projectDir
projectDir = "C:\Users\higosantos\Documents\gestao_editais\arandu-napi-robotica"

Dim venvPython
venvPython = projectDir & "\venv\Scripts\python.exe"

Dim appScript
appScript = projectDir & "\app.py"

' Verifica se o servidor já está rodando (evita duplicatas)
Dim oExec, result
Set oExec = oShell.Exec("netstat -ano")
result = ""
Do While Not oExec.StdOut.AtEndOfStream
    result = result & oExec.StdOut.ReadLine()
Loop

If InStr(result, ":5005") = 0 Then
    ' Servidor não está rodando. Inicia silenciosamente.
    ' WindowStyle 0 = sem janela visível
    oShell.Run """" & venvPython & """ """ & appScript & """", 0, False
End If

Set oShell = Nothing
