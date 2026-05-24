$TargetFile = "c:\Users\higosantos\Documents\gestao_editais\gestao_editais_novo\Gestao_Editais.bat"
$ShortcutFile = "$env:USERPROFILE\Desktop\Gestao_Editais.lnk"
$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut($ShortcutFile)
$Shortcut.TargetPath = $TargetFile
$Shortcut.WorkingDirectory = "c:\Users\higosantos\Documents\gestao_editais\gestao_editais_novo"
$Shortcut.IconLocation = "c:\Users\higosantos\Documents\gestao_editais\gestao_editais_novo\static\favicon.ico"
$Shortcut.Save()
Write-Host "Atalho atualizado: $ShortcutFile -> $TargetFile"
