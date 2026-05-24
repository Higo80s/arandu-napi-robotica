$WScriptShell = New-Object -ComObject WScript.Shell
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $DesktopPath "Gestão de Editais.lnk"
$TargetDir = "C:\Users\higosantos\Documents\gestao_editais\gestao_editais_novo"
$TargetFile = Join-Path $TargetDir "Gestao_Editais.bat"

# Create Shortcut
$Shortcut = $WScriptShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $TargetFile
$Shortcut.WorkingDirectory = $TargetDir
$Shortcut.WindowStyle = 1   # Normal window
$Shortcut.Description = "Sistema de Gestão de Editais"
$Shortcut.IconLocation = "C:\Windows\System32\imageres.dll,1" # Document icon
$Shortcut.Save()

Write-Host "Atalho criado com sucesso em: $ShortcutPath"
if (Test-Path $ShortcutPath) {
    Write-Host "VERIFICADO: O arquivo existe."
}
else {
    Write-Host "ERRO: O arquivo não foi encontrado após criação."
}
