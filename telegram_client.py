import requests
from config import Config

def send_telegram_message(text: str) -> bool:
    """
    Sends an HTML formatted message to the configured Telegram chat.
    """
    if not Config.TELEGRAM_BOT_TOKEN or not Config.TELEGRAM_CHAT_ID:
        print("[!] Telegram credentials not configured. Skipping alert.")
        return False
        
    url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": Config.TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        result = response.json()
        if response.status_code == 200 and result.get("ok"):
            return True
        else:
            print(f"[!] Telegram API error: {result.get('description', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"[!] Error sending Telegram alert: {e}")
        return False

if __name__ == "__main__":
    # Test telegram message sending.
    # Note: This requires real bot token and chat ID in .env.
    test_msg = (
        "🤖 <b>Arc Liquidity Watcher Test Alert</b>\n\n"
        "If you see this, your Telegram Bot integration is working perfectly!\n"
        "RPC Configured: <code>https://rpc.testnet.arc.network</code>"
    )
    print("Sending test message...")
    if send_telegram_message(test_msg):
        print("[+] Test alert sent successfully!")
    else:
        print("[!] Test alert failed. Verify your token and chat ID.")
