Option Explicit

Dim WshShell, FSO, strScriptDir, strBatchPath

Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")

' Get the absolute directory of this script
strScriptDir = FSO.GetParentFolderName(WScript.ScriptFullName)

' Construct path to boot.bat
strBatchPath = FSO.BuildPath(strScriptDir, "boot.bat")

' Run entry
If FSO.FileExists(strBatchPath) Then
    ' 0 = Hide Window, True = Wait for return (change to False if you want async)
    ' We use False so VBS exits immediately
    WshShell.Run chr(34) & strBatchPath & chr(34), 0, False
Else
    MsgBox "Arquivo de inicializacao nao encontrado: " & strBatchPath, 16, "Erro Fatal"
End If

Set WshShell = Nothing
Set FSO = Nothing
