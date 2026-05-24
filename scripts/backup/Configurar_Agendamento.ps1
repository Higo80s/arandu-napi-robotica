# Configurar_Backup_Agendado.ps1

# 1. Verificar Permissões de Administrador
if (!([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "ATENÇÃO: Este script precisa de permissões de ADMINISTRADOR!" -ForegroundColor Red
    Write-Host "Por favor, feche esta janela." -ForegroundColor Yellow
    Write-Host "Clique com o botão direito no arquivo 'Configurar_Backup_Agendado.ps1' e escolha 'Executar com o PowerShell'." -ForegroundColor Yellow
    Read-Host "Pressione Enter para sair"
    exit
}

$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonExe = Join-Path $ScriptPath ".venv\Scripts\python.exe"
$BackupScript = Join-Path $ScriptPath "backup_system.py"
$TaskName = "BackupGestaoEditais"

Write-Host "Configurando backup mensal (Dia 1, 10:00)..." -ForegroundColor Cyan

# 2. Usar schtasks para criar a tarefa (mais robusto que cmdlets nativos em algumas versões)
# /SC MONTHLY /D 1 -> Mensalmente no dia 1
# /ST 10:00 -> As 10 da manha
# /RL HIGHEST -> Executar com privilégios elevados se necessário (opcional, mas bom pra backup)
# /F -> Forçar overwrite se existir

$Command = "`"$PythonExe`" `"$BackupScript`""
$Params = "/Create /SC MONTHLY /D 1 /TN `"$TaskName`" /TR `"$Command`" /ST 10:00 /F"

Start-Process "schtasks.exe" -ArgumentList $Params -NoNewWindow -Wait

Write-Host ""
Write-Host "Verificando se a tarefa foi criada..." -ForegroundColor Cyan
schtasks /Query /TN $TaskName

Write-Host ""
Write-Host "Concluído! O backup rodará todo dia 1 do mês." -ForegroundColor Green
Read-Host "Pressione Enter para sair"
