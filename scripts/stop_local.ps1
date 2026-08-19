$ErrorActionPreference = "Stop"
$Ports = 8501, 11434

foreach ($Port in $Ports) {
    $Listeners = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    foreach ($Listener in $Listeners) {
        Stop-Process -Id $Listener.OwningProcess -Force
        Write-Host "Stopped process $($Listener.OwningProcess) on port $Port."
    }
}
