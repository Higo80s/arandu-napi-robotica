    # Script PowerShell para criar agendamento automatico
# Execute como Administrador: Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process; .\criar_agendamento.ps1

$pythonPath = "C:\Python313\python.exe"
$scriptPath = "C:\Users\higosantos\Documents\gestao_editais\exportar_excel_mensal.py"
$workingDir = "C:\Users\higosantos\Documents\gestao_editais"

# Verificar se Python existe
if (-not (Test-Path $pythonPath)) {
    Write-Host "Erro: Python nao encontrado em: $pythonPath"
    Write-Host "Por favor, atualize o caminho do Python no script"
    exit 1
}

Write-Host "OK: Python encontrado em: $pythonPath"
Write-Host "OK: Script em: $scriptPath"
Write-Host ""

# Criar acao
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument $scriptPath -WorkingDirectory $workingDir

# Criar gatilho para o 1o dia de cada mes as 10:00
$trigger = New-ScheduledTaskTrigger -At "10:00AM" -Weekly -DaysOfWeek Tuesday

# Configuracoes de seguranca
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -RunLevel Highest

# Configuracoes gerais
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Criar tarefa
try {
    Register-ScheduledTask `
        -TaskName "Exportar Excel Gestao Editais" `
        -Action $action `
        -Trigger $trigger `
        -Principal $principal `
        -Settings $settings `
        -Description "Exporta relatorio de acompanhamento de bolsistas em Excel todo 1o dia do mes as 10:00" `
        -Force
    
    Write-Host "SUCESSO! Tarefa agendada com sucesso!"
    Write-Host ""
    Write-Host "Detalhes:"
    Write-Host "   - Nome: Exportar Excel Gestao Editais"
    Write-Host "   - Frequencia: Mensalmente (dia 1o)"
    Write-Host "   - Horario: 10:00 AM"
    Write-Host "   - Arquivo: $scriptPath"
    Write-Host ""
    Write-Host "Os arquivos Excel serao salvos em:"
    Write-Host "   C:\Users\higosantos\Documents\gestao_editais\acompanhamento_excel\"
    
} catch {
    Write-Host "Erro ao criar tarefa: $_"
    exit 1
}

# Verificar se foi criada
$task = Get-ScheduledTask -TaskName "Exportar Excel Gestao Editais" -ErrorAction SilentlyContinue
if ($task) {
    Write-Host ""
    Write-Host "OK: Tarefa verificada no Task Scheduler"
    Get-ScheduledTask -TaskName "Exportar Excel Gestao Editais" | Select-Object TaskName, State | Format-Table
}
