# stop_bot.ps1
# Find and stop the specific python background processes running our bot
$processes = Get-CimInstance Win32_Process -Filter "name = 'python.exe' or name = 'python3.exe'" | Where-Object { $_.CommandLine -like "*scanner.py*" -or $_.CommandLine -like "*watcher.py*" }

if ($processes) {
    foreach ($p in $processes) {
        Stop-Process -Id $p.ProcessId -Force
        Write-Host "[-] Stopped bot process (ID: $($p.ProcessId))" -ForegroundColor Red
    }
    Write-Host "[+] Arc Liquidity Watcher has been stopped successfully." -ForegroundColor Green
} else {
    Write-Host "[!] No running bot process detected." -ForegroundColor Yellow
}
