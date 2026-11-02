$ErrorActionPreference = 'Stop'
$projectDir = $PSScriptRoot
$pythonExe = Join-Path $projectDir '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonExe)) {
    throw 'Create .venv and install requirements.txt first; see README.md.'
}
$logDir = Join-Path $projectDir '.runtime'
New-Item -ItemType Directory -Path $logDir -Force | Out-Null
$services = @(
    @{ Name = 'api'; Port = 5000; Args = '-X utf8 healthkit_api_server.py' },
    @{ Name = 'dashboard'; Port = 8508; Args = '-X utf8 -m streamlit run app_final.py --server.port=8508 --server.address=127.0.0.1 --server.headless=true' },
    @{ Name = 'risk'; Port = 8509; Args = '-X utf8 -m streamlit run app_risk_alert.py --server.port=8509 --server.address=127.0.0.1 --server.headless=true' }
)
foreach ($service in $services) {
    $listener = Get-NetTCPConnection -State Listen -LocalPort $service.Port -ErrorAction SilentlyContinue
    if ($listener) {
        Write-Host "Port $($service.Port) is occupied; skipping $($service.Name)."
        continue
    }
    $process = Start-Process -FilePath $pythonExe -ArgumentList $service.Args -WorkingDirectory $projectDir -WindowStyle Hidden -RedirectStandardOutput (Join-Path $logDir "$($service.Name).out.log") -RedirectStandardError (Join-Path $logDir "$($service.Name).err.log") -PassThru
    Start-Sleep -Milliseconds 500
    $process.Refresh()
    if ($process.HasExited) {
        throw "$($service.Name) exited during startup. See .runtime/$($service.Name).err.log."
    }
    @{ Id = $process.Id; Started = $process.StartTime.ToUniversalTime().ToString('o') } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $logDir "$($service.Name).process.json")
    Write-Host "Started $($service.Name): PID $($process.Id), port $($service.Port)"
}
Write-Host 'Main dashboard: http://localhost:8508'
Write-Host 'Risk dashboard: http://localhost:8509'
