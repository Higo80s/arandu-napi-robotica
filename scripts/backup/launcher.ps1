# Launcher do Sistema de Gestao de Editais
$ErrorActionPreference = "Stop"

# Obter diretório do script
$ScriptPath = $PSScriptRoot
Set-Location $ScriptPath

# Configurar Log
$LogFile = Join-Path $ScriptPath "startup_ps.log"
"[" + (Get-Date).ToString() + "] Iniciando launcher.ps1..." | Out-File $LogFile -Encoding UTF8

try {
    # Definir caminhos
    $PythonExe = Join-Path $ScriptPath ".venv\Scripts\python.exe"
    $ProdScript = Join-Path $ScriptPath "production.py"

    # Verificações
    if (-not (Test-Path $PythonExe)) {
        throw "Python nao encontrado em: $PythonExe"
    }
    if (-not (Test-Path $ProdScript)) {
        throw "Script production.py nao encontrado em: $ProdScript"
    }

    "[" + (Get-Date).ToString() + "] Iniciando processo Python..." | Out-File -Append $LogFile -Encoding UTF8
    
    # Iniciar Python (Sem janela)
    # Usamos Start-Process com -WindowStyle Hidden para garantir que nada apareça
    $Process = Start-Process -FilePath $PythonExe -ArgumentList $ProdScript -WindowStyle Hidden -PassThru
    
    "[" + (Get-Date).ToString() + "] Processo iniciado. ID: $($Process.Id)" | Out-File -Append $LogFile -Encoding UTF8

}
catch {
    "[" + (Get-Date).ToString() + "] ERRO FATAL: $_" | Out-File -Append $LogFile -Encoding UTF8
    # Mostrar erro para usuário se falhar
    [System.Windows.Forms.MessageBox]::Show($_, "Erro ao Iniciar Sistema", 0, 16)
}
