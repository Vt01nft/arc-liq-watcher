# start_bot.ps1
# Get the directory where this script is located
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Start scanner.py in a hidden background window
Start-Process python -ArgumentList "scanner.py" -WindowStyle Hidden -WorkingDirectory $scriptDir

Write-Host "[+] Arc Liquidity Watcher has been launched silently in the background!" -ForegroundColor Green
Write-Host "[*] Check your Telegram chat to confirm the scanner started." -ForegroundColor Green
Write-Host "[*] To stop the bot later, run: .\stop_bot.ps1" -ForegroundColor Yellow
