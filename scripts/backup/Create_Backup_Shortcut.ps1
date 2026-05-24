
$WshShell = New-Object -comObject WScript.Shell
$Desktop = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $Desktop "Realizar Backup.lnk"
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "$PWD\Realizar_Backup_Agora.bat"
$Shortcut.WorkingDirectory = "$PWD"
$Shortcut.IconLocation = "shell32.dll,45"
$Shortcut.Description = "Clique para realizar um backup completo do sistema"
$Shortcut.Save()
Write-Host "Atalho de Backup criado em: $ShortcutPath"
