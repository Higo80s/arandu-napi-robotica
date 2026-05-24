' ============================================================
'  Cria atalho no Desktop - Arandu NAPI-Robotica
' ============================================================

Dim oShell, oFSO, oLink
Set oShell = CreateObject("WScript.Shell")
Set oFSO   = CreateObject("Scripting.FileSystemObject")

Dim desktopPath
desktopPath = oShell.SpecialFolders("Desktop")

Dim batPath
batPath = "C:\Users\higosantos\Documents\gestao_editais\arandu-napi-robotica\Abrir_NAPI_Robotica.bat"

Dim iconPath
iconPath = "C:\Users\higosantos\Documents\gestao_editais\arandu-napi-robotica\static\favicon.ico"

Dim shortcutPath
shortcutPath = desktopPath & "\Arandu NAPI-Robotica.lnk"

Set oLink = oShell.CreateShortcut(shortcutPath)
oLink.TargetPath      = batPath
oLink.WorkingDirectory = "C:\Users\higosantos\Documents\gestao_editais\arandu-napi-robotica\"
oLink.Description     = "Abrir Arandu NAPI-Robotica (Sistema de Gestao)"
oLink.WindowStyle     = 7

If oFSO.FileExists(iconPath) Then
    oLink.IconLocation = iconPath
End If

oLink.Save

MsgBox "Atalho criado no Desktop com sucesso!" & Chr(13) & Chr(10) & "Procure por 'Arandu NAPI-Robotica'.", vbInformation, "Arandu Setup"

Set oLink  = Nothing
Set oShell = Nothing
Set oFSO   = Nothing
