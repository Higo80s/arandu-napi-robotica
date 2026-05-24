
$TargetFile = "$PSScriptRoot\Gestao_Editais.bat"
$ShortcutFile = "$PSScriptRoot\Gestao de Editais.lnk"
$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut($ShortcutFile)
$Shortcut.TargetPath = $TargetFile
$Shortcut.WorkingDirectory = $PSScriptRoot
$Shortcut.IconLocation = "$PSScriptRoot\icon.ico"
$Shortcut.Save()

Write-Host "Shortcut created at $ShortcutFile"

$DesktopPath = [Environment]::GetFolderPath("Desktop")
$DesktopShortcut = "$DesktopPath\Gestao de Editais.lnk"
$Shortcut = $WScriptShell.CreateShortcut($DesktopShortcut)
$Shortcut.TargetPath = $TargetFile
$Shortcut.WorkingDirectory = $PSScriptRoot
$Shortcut.IconLocation = "$PSScriptRoot\icon.ico"
$Shortcut.Save()

Write-Host "Desktop Shortcut created at $DesktopShortcut"
