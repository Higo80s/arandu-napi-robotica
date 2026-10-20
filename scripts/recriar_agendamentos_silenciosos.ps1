# Recria os agendamentos do Arandu Robotica sem janela preta e com resumo no canto.
# Fonte da verdade: somente AranduRobotica_*. Remove aliases antigos deste repo.
$ErrorActionPreference = 'Continue'
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Vbs = Join-Path $Root 'scripts\launch_silent.vbs'
$Wscript = Join-Path $env:SystemRoot 'System32\wscript.exe'

function Remove-TaskIfExists {
    param([string]$Name)
    schtasks /Query /TN $Name 1>$null 2>$null
    if ($LASTEXITCODE -ne 0) {
        return
    }
    $out = & schtasks /Delete /TN $Name /F 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "REM $Name" -ForegroundColor Yellow
    } else {
        Write-Host "FALHA ao remover $Name exit=$LASTEXITCODE" -ForegroundColor Red
        Write-Host $out
    }
}

function New-SilentTask {
    param(
        [string]$Name,
        [string]$LabelToken,
        [string]$TargetRel,
        [string]$Time
    )
    $target = Join-Path $Root $TargetRel
    if (-not (Test-Path $target)) {
        Write-Host "PULA $Name - alvo nao encontrado: $target" -ForegroundColor Yellow
        return
    }
    $tr = "$Wscript $Vbs $target $LabelToken"
    $out = & schtasks /Create /SC DAILY /TN $Name /TR $tr /ST $Time /RU $env:USERNAME /F 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "OK  $Name - diario $Time" -ForegroundColor Green
    } else {
        Write-Host "FALHA $Name exit=$LASTEXITCODE" -ForegroundColor Red
        Write-Host $out
    }
}

Write-Host "Recriando agendamentos silenciosos do Arandu Robotica..." -ForegroundColor Cyan

# Aliases antigos deste repo (janela preta / horario duplicado). Nao mexer em AranduProppg_* nem Arandu_Pagamentos_Nuvem.
@(
    'Arandu_PagamentoBolsas_Nuvem',
    'Arandu_AvisoUltimoMesBolsa',
    'Arandu_CobrancaRelatorioFinal',
    'Arandu_ResumoDiario'
) | ForEach-Object { Remove-TaskIfExists $_ }

New-SilentTask -Name 'AranduRobotica_ResumoDiario' -LabelToken 'Resumo_diario' `
    -TargetRel 'tasks\run_resumo_diario.bat' -Time '08:00'
New-SilentTask -Name 'AranduRobotica_CobrancaRelatorioFinal' -LabelToken 'Cobranca_relatorio_final' `
    -TargetRel 'tasks\run_cobranca_relatorio_final.bat' -Time '08:05'
New-SilentTask -Name 'AranduRobotica_AvisoUltimoMesBolsa' -LabelToken 'Aviso_ultimo_mes_de_bolsa' `
    -TargetRel 'tasks\run_aviso_ultimo_mes_bolsa.bat' -Time '08:10'
New-SilentTask -Name 'AranduRobotica_ConfirmacaoInicioBolsa' -LabelToken 'Confirmacao_de_inicio_de_bolsa' `
    -TargetRel 'tasks\run_confirmacao_inicio_bolsa.bat' -Time '08:12'
New-SilentTask -Name 'AranduRobotica_PagamentoBolsasNuvem' -LabelToken 'Pagamento_de_bolsas_na_Nuvem' `
    -TargetRel 'tasks\run_enviar_pagamento_bolsas.bat' -Time '08:15'

Write-Host "Pronto. As tarefas rodam ocultas e mostram apenas o resumo no canto inferior direito." -ForegroundColor Cyan
Write-Host "Logs: $Root\logs\cron_*.log"
