' Arandu Robotica - lancador invisivel para o Agendador de Tarefas.
Option Explicit

If WScript.Arguments.Count < 1 Then
    WScript.Quit 1
End If

Dim target, label, title, scriptDir, ps1, cmd, sh
target = WScript.Arguments(0)
title = "Arandu Rob" & ChrW(243) & "tica"
If WScript.Arguments.Count >= 2 Then
    label = Replace(WScript.Arguments(1), "_", " ")
Else
    label = "Tarefa automatica"
End If

scriptDir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
ps1 = scriptDir & "\run_task_silent.ps1"
cmd = "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File """ & ps1 & """" _
    & " -Title """ & title & """" _
    & " -Label """ & Replace(label, """", "'") & """" _
    & " -Target """ & target & """"

Set sh = CreateObject("WScript.Shell")
sh.Run cmd, 0, False
Set sh = Nothing
