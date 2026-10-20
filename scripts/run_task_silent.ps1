# Arandu Robotica - executa tarefa sem janela e mostra resumo no canto inferior direito.
param(
    [string]$Title = 'Arandu Robotica',
    [string]$Label = 'Tarefa automatica',
    [Parameter(Mandatory = $true)][string]$Target,
    [string]$WorkingDirectory = '',
    [switch]$NoNotify
)

$ErrorActionPreference = 'Continue'

function Show-CornerNotify {
    param([string]$TipTitle, [string]$TipText, [string]$Icon = 'Info')
    try {
        Add-Type -AssemblyName System.Windows.Forms -ErrorAction Stop
        Add-Type -AssemblyName System.Drawing -ErrorAction Stop
        $n = New-Object System.Windows.Forms.NotifyIcon
        $n.Icon = [System.Drawing.SystemIcons]::Information
        if ($Icon -eq 'Error') { $n.Icon = [System.Drawing.SystemIcons]::Error }
        $n.Visible = $true
        $tipIcon = if ($Icon -eq 'Error') {
            [System.Windows.Forms.ToolTipIcon]::Error
        } else {
            [System.Windows.Forms.ToolTipIcon]::Info
        }
        $n.ShowBalloonTip(6000, $TipTitle, $TipText, $tipIcon)
        Start-Sleep -Milliseconds 6300
        $n.Visible = $false
        $n.Dispose()
    } catch {
        # Sessao sem interface grafica: tarefa continua silenciosamente.
    }
}

if (-not (Test-Path -LiteralPath $Target)) {
    if (-not $NoNotify) {
        Show-CornerNotify -TipTitle $Title -TipText "Falha: arquivo nao encontrado - $Label" -Icon Error
    }
    exit 1
}

$root = if ($WorkingDirectory) {
    $WorkingDirectory
} else {
    (Resolve-Path (Join-Path (Split-Path -Parent $Target) '..')).Path
}
$logDir = Join-Path $root 'logs'
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir | Out-Null
}
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$safeLabel = ($Label -replace '[^\w\-]+', '_').Trim('_')
$logOut = Join-Path $logDir "cron_${safeLabel}_${stamp}.out.log"
$logErr = Join-Path $logDir "cron_${safeLabel}_${stamp}.err.log"

try {
    $p = Start-Process -FilePath 'cmd.exe' `
        -ArgumentList @('/c', $Target) `
        -WorkingDirectory (Split-Path -Parent $Target) `
        -WindowStyle Hidden -Wait -PassThru `
        -RedirectStandardOutput $logOut `
        -RedirectStandardError $logErr
    $exitCode = $p.ExitCode
} catch {
    $exitCode = 1
    Set-Content -Path $logErr -Value $_.Exception.Message -Encoding UTF8
}

if ($null -eq $exitCode) { $exitCode = 0 }
if ($exitCode -eq 0) {
    $summary = "$Label concluida (00)."
    try {
        $marker = Get-Content -LiteralPath $logOut -Encoding UTF8 |
            Where-Object { $_ -like 'ARANDU_TASK_NOTIFICATION=*' } |
            Select-Object -Last 1
        if ($marker) {
            $payload = ($marker.Substring('ARANDU_TASK_NOTIFICATION='.Length) | ConvertFrom-Json)
            if ($payload.message) { $summary = [string]$payload.message }
        }
    } catch {}
} else {
    $summary = "$Label falhou (codigo $exitCode). Consulte a pasta logs."
}
if ($summary.Length -gt 250) { $summary = $summary.Substring(0, 247) + '...' }

if (-not $NoNotify) {
    Show-CornerNotify -TipTitle $Title -TipText $summary -Icon $(if ($exitCode) { 'Error' } else { 'Info' })
}

Get-ChildItem -Path $logDir -Filter 'cron_*.log' -ErrorAction SilentlyContinue |
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-14) } |
    Remove-Item -Force -ErrorAction SilentlyContinue

exit $exitCode
