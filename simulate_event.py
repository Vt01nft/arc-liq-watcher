import os
import sys
from config import validate_config, Config
from telegram_client import send_telegram_message

def test_telegram_alert():
    """
    Sends realistic mock alerts for Uniswap V2 and V3 pool creations to verify Telegram formatting.
    """
    print("\n--- Sending Mock Uniswap V2 Alert ---")
    mock_token0 = "0x0006ed5d37a9d6687d1ecc8b642ff9c4760d9a16" # Mock USDC
    mock_token1 = "0x8e604ae97dda3deb77d9856606a8dc3135998fc4" # Mock BIRDIE
    mock_pair = "0x913b8a1c720d2d3851b4fe4e548cf549646b9a12"
    mock_tx = "0x1a8f9b964dca31f9b3fa73f32f31c783cca1c0412eab19a4c1b78a45efdec"
    
    explorer = Config.ARC_RPC_URL.replace("rpc.", "testnet.arcscan.app") # Fallback to testnet
    if "mainnet" in Config.ARC_RPC_URL:
        explorer = "https://arcscan.app"
    else:
        explorer = "https://testnet.arcscan.app"

    v2_msg = (
        f"🚀 <b>New DEX Pool Created (Uniswap V2 Clone) [SIMULATION]</b>\n\n"
        f"<b>Token 0:</b> USD Coin (USDC)\n"
        f"<code>{mock_token0}</code>\n\n"
        f"<b>Token 1:</b> Birdie Coin (BIRDIE)\n"
        f"<code>{mock_token1}</code>\n\n"
        f"<b>Pool Pair Address:</b>\n"
        f"<code>{mock_pair}</code>\n\n"
        f"🔗 <a href='{explorer}/address/{mock_pair}'>View Pool on Explorer</a>\n"
        f"🔗 <a href='{explorer}/tx/{mock_tx}'>View Transaction</a>"
    )
    
    if send_telegram_message(v2_msg):
        print("[+] Mock V2 alert sent successfully!")
    else:
        print("[!] Mock V2 alert failed.")

    print("\n--- Sending Mock Uniswap V3 Alert ---")
    mock_pool = "0x53964dca31f9b3fa73f32f31c783cca1c0412eab"
    v3_msg = (
        f"🦄 <b>New DEX Pool Created (Uniswap V3 Clone) [SIMULATION]</b>\n\n"
        f"<b>Token 0:</b> USD Coin (USDC)\n"
        f"<code>{mock_token0}</code>\n\n"
        f"<b>Token 1:</b> Birdie Coin (BIRDIE)\n"
        f"<code>{mock_token1}</code>\n\n"
        f"<b>Fee Tier:</b> 0.3%\n"
        f"<b>Pool Address:</b>\n"
        f"<code>{mock_pool}</code>\n\n"
        f"🔗 <a href='{explorer}/address/{mock_pool}'>View Pool on Explorer</a>\n"
        f"🔗 <a href='{explorer}/tx/{mock_tx}'>View Transaction</a>"
    )
    
    if send_telegram_message(v3_msg):
        print("[+] Mock V3 alert sent successfully!")
    else:
        print("[!] Mock V3 alert failed.")

def main():
    print("==================================================")
    print("          Arc Liquidity Bot Simulator            ")
    print("==================================================")
    
    # 1. Check if .env exists
    if not os.path.exists(".env"):
        print("[!] Error: .env file not found!")
        print("Please copy .env.example to .env and configure your variables:")
        print("   cp .env.example .env")
        sys.exit(1)
        
    # 2. Validate Config and RPC
    success, w3 = validate_config()
    if not success:
        print("\n[!] Configuration or RPC health check failed.")
        print("Verify your settings in .env before running.")
        sys.exit(1)
        
    print("\n[+] Config is valid!")
    print(f"    Active RPC: {Config.ARC_RPC_URL}")
    print(f"    Active Chain ID: {Config.ARC_CHAIN_ID}")
    print(f"    Telegram Bot Token: {Config.TELEGRAM_BOT_TOKEN[:10]}...")
    print(f"    Telegram Chat ID: {Config.TELEGRAM_CHAT_ID}")
    
    # 3. Test sending Telegram alerts
    test_telegram_alert()
    print("\n[+] Verification steps completed!")
    print("Check your Telegram app for the mock liquidity alerts.")

if __name__ == "__main__":
    main()
