$ErrorActionPreference = 'Stop'
$logDir = Join-Path $PSScriptRoot '.runtime'
foreach ($name in @('api', 'dashboard', 'risk')) {
    $recordPath = Join-Path $logDir "$name.process.json"
    if (-not (Test-Path -LiteralPath $recordPath)) { continue }
    $record = Get-Content -LiteralPath $recordPath -Raw | ConvertFrom-Json
    $process = Get-Process -Id $record.Id -ErrorAction SilentlyContinue
    # Start time protects unrelated processes if Windows has reused the PID.
    if ($process -and $process.StartTime.ToUniversalTime().ToString('o') -eq $record.Started) {
        Stop-Process -Id $process.Id
        Write-Host "Stopped $name (PID $($process.Id))."
    }
    Remove-Item -LiteralPath $recordPath
}
