# status_bot.ps1
# Query active python processes running our bot files
$processes = Get-CimInstance Win32_Process -Filter "name = 'python.exe' or name = 'python3.exe'" | Where-Object { $_.CommandLine -like "*scanner.py*" -or $_.CommandLine -like "*watcher.py*" }

if ($processes) {
    Write-Host "[+] Arc Liquidity Watcher is ACTIVE" -ForegroundColor Green
    foreach ($p in $processes) {
        Write-Host "  - Process ID: $($p.ProcessId)" -ForegroundColor Green
        Write-Host "    Command:    $($p.CommandLine)" -ForegroundColor Gray
    }
} else {
    Write-Host "[-] Arc Liquidity Watcher is INACTIVE" -ForegroundColor Red
}
