# ========================================
# Gestao de Editais - Criar Atalho
# ========================================
# Este script cria apenas o atalho principal na Area de Trabalho
# Os demais ficam na pasta do projeto para organização
# ========================================

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$WScriptShell = New-Object -ComObject WScript.Shell

# ========================================
# AREA DE TRABALHO - Apenas o principal
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Criando atalho na Area de Trabalho..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Criar atalho PRINCIPAL para iniciar (PowerShell Launcher)
$ShortcutPath1 = Join-Path $DesktopPath "Gestao de Editais.lnk"

# Forçar remoção de atalho existente
if (Test-Path $ShortcutPath1) {
    Remove-Item $ShortcutPath1 -Force
    Write-Host "Atalho antigo removido." -ForegroundColor Yellow
}

$Shortcut = $WScriptShell.CreateShortcut($ShortcutPath1)

# Target: PowerShell (Native Windows Binary)
$Shortcut.TargetPath = "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"

# Arguments: Run our script, hidden, bypassing policy
# Note: We use quotes around the file path in case of spaces
$LauncherPath = Join-Path $ScriptDir "launcher.ps1"
$Shortcut.Arguments = "-ExecutionPolicy Bypass -WindowStyle Hidden -File ""$LauncherPath"""

$Shortcut.WorkingDirectory = $ScriptDir

# Icon setup
$IconPath = Join-Path $ScriptDir "icon.ico"
if (-not (Test-Path $IconPath)) {
    # Failover to static favicon if icon.ico missing
    $IconPath = Join-Path $ScriptDir "static\favicon.ico"
}
$Shortcut.IconLocation = $IconPath

$Shortcut.Description = "Sistema de Gestao de Editais"
$Shortcut.Save()

Write-Host "[OK] Atalho 'Gestao de Editais.lnk' criado na Area de Trabalho!" -ForegroundColor Green
Write-Host "     (Inicia em modo producao - sem console)" -ForegroundColor Gray

# ========================================
# PASTA DO PROJETO - Atalhos adicionais
# ========================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Criando atalhos na pasta do projeto..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Criar atalho para debug (com console) na pasta do projeto
$ShortcutPath2 = Join-Path $ScriptDir "Gestao de Editais (Debug).lnk"
$Shortcut2 = $WScriptShell.CreateShortcut($ShortcutPath2)
$Shortcut2.TargetPath = Join-Path $ScriptDir "Iniciar_Gestao_Editais.bat"
$Shortcut2.WorkingDirectory = $ScriptDir
$Shortcut2.IconLocation = Join-Path $ScriptDir "icon.ico"
$Shortcut2.Description = "Sistema de Gestao de Editais - Modo Debug (Com Console)"
$Shortcut2.Save()

Write-Host "[OK] Atalho 'Gestao de Editais (Debug).lnk' criado no projeto!" -ForegroundColor Green
Write-Host "     (Inicia com console visivel para debug)" -ForegroundColor Gray

# Criar atalho para parar servidor na pasta do projeto
$ShortcutPath3 = Join-Path $ScriptDir "Parar Servidor.lnk"
$Shortcut3 = $WScriptShell.CreateShortcut($ShortcutPath3)
$Shortcut3.TargetPath = Join-Path $ScriptDir "Parar_Gestao_Editais.bat"
$Shortcut3.WorkingDirectory = $ScriptDir
$Shortcut3.IconLocation = Join-Path $ScriptDir "icon.ico"
$Shortcut3.Description = "Parar o Servidor de Gestao de Editais"
$Shortcut3.Save()

Write-Host "[OK] Atalho 'Parar Servidor.lnk' criado no projeto!" -ForegroundColor Green
Write-Host "     (Para o servidor quando necessario)" -ForegroundColor Gray

# ========================================
# LIMPEZA - Remove atalhos antigos da Area de Trabalho
# ========================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Limpando atalhos desnecessarios..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Remove atalhos antigos/duplicados da área de trabalho
$OldShortcuts = @(
    "Gestao Editais.lnk",
    "Gestao de Editais (Oculto).lnk",
    "Parar Gestao de Editais.lnk",
    "Iniciar_Gestao_Editais_Oculto.lnk"
)

foreach ($shortcut in $OldShortcuts) {
    $path = Join-Path $DesktopPath $shortcut
    if (Test-Path $path) {
        Remove-Item $path -Force
        Write-Host "[OK] Removido: $shortcut" -ForegroundColor Yellow
    }
}

# ========================================
# RESUMO FINAL
# ========================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Atalhos organizados com sucesso!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "AREA DE TRABALHO:" -ForegroundColor Cyan
Write-Host "  [*] Gestao de Editais.lnk" -ForegroundColor White
Write-Host "      (Duplo clique para iniciar o sistema)" -ForegroundColor Gray
Write-Host ""
Write-Host "PASTA DO PROJETO:" -ForegroundColor Cyan
Write-Host "  [*] Gestao de Editais (Debug).lnk" -ForegroundColor White
Write-Host "      (Para debug com console visivel)" -ForegroundColor Gray
Write-Host "  [*] Parar Servidor.lnk" -ForegroundColor White
Write-Host "      (Para encerrar o servidor)" -ForegroundColor Gray
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Pronto para usar em producao!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Pause
