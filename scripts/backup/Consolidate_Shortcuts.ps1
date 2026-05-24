# Remove old shortcuts and create single functional one
$desktopPath = [Environment]::GetFolderPath("Desktop")
$projectPath = "C:\Users\higosantos\Documents\gestao_editais\gestao_editais_novo"

# Remove old shortcuts
$shortcuts = @("Gestao de Editais.lnk", "Gestão_editais.lnk", "gestao de editais.lnk", "Gestao_Editais.lnk")
foreach ($shortcut in $shortcuts) {
    $path = Join-Path $desktopPath $shortcut
    if (Test-Path $path) {
        Remove-Item $path-Force
        Write-Host "Removido: $shortcut"
    }
}

# Create new shortcut
$WScriptShell = New-Object -ComObject WScript.Shell
$shortcutPath = Join-Path $desktopPath "Gestão de Editais.lnk"
$shortcut = $WScriptShell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = Join-Path $projectPath ".venv\Scripts\python.exe"
$shortcut.Arguments = "dev_server.py"
$shortcut.WorkingDirectory = $projectPath
$shortcut.Description = "Gestão de Editais - Sistema Web"
$shortcut.IconLocation = "C:\Windows\System32\imageres.dll,1"
$shortcut.Save()

Write-Host "✅ Atalho criado: Gestão de Editais.lnk"
Write-Host "Localização: $shortcutPath"
