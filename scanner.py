import time
import sys
import os
import argparse
from web3 import Web3
from config import Config, get_mainnet_rpc_candidates, validate_config
from telegram_client import send_telegram_message
from watcher import watch_liquidity


TESTNET_RPC_CANDIDATES = [
    "https://rpc.testnet.arc.network",
    "https://arc-testnet.drpc.org"
]

def scan_rpcs(candidates, target_chain_id, poll_interval=5):
    """
    Continually polls the candidates list for an active RPC returning target_chain_id.
    """
    print(f"[+] Starting RPC Scanner.")
    print(f"    Target Chain ID: {target_chain_id}")
    print(f"    Candidates to scan: {len(candidates)}")
    for c in candidates:
        print(f"      - {c}")
    print(f"    Polling every {poll_interval} seconds...")
    
    # Notify telegram scanner is active
    network_name = "Mainnet" if target_chain_id == 5042 else "Testnet"
    send_telegram_message(
        f"🔍 <b>Arc {network_name} RPC Scanner is now active</b>\n"
        f"Scanning {len(candidates)} candidates for Chain ID <code>{target_chain_id}</code>..."
    )

    while True:
        for url in candidates:
            print(f"\rTesting: {url} ... ", end="", flush=True)
            try:
                # Set a short timeout of 3 seconds to keep scanning snappy
                w3 = Web3(Web3.HTTPProvider(url, request_kwargs={'timeout': 3}))
                if w3.is_connected():
                    chain_id = w3.eth.chain_id
                    if chain_id == target_chain_id:
                        print(f"[SUCCESS] (Chain ID matches: {chain_id})")
                        
                        # Send alert to Telegram
                        msg = (
                            f"🚨 <b>Arc {network_name} RPC Detected!</b>\n\n"
                            f"<b>URL:</b> <code>{url}</code>\n"
                            f"<b>Chain ID:</b> <code>{chain_id}</code>\n\n"
                            f"📈 Starting the liquidity watcher loop now..."
                        )
                        send_telegram_message(msg)
                        
                        # Return working RPC
                        return url
                    else:
                        print(f"[WRONG CHAIN] (Chain ID: {chain_id})")
                else:
                    print("[OFFLINE]")
            except Exception as e:
                print(f"[ERROR: {str(e)[:30]}]")
                
        time.sleep(poll_interval)

def main():
    parser = argparse.ArgumentParser(description="Arc Mainnet RPC Scanner and Auto-Launcher")
    parser.add_argument("--test", action="store_true", help="Test mode: Scan for testnet RPC (Chain ID 5042002)")
    parser.add_argument("--poll", type=int, default=5, help="Poll interval in seconds")
    args = parser.parse_args()

    # Verify Telegram config before starting scanner
    if not Config.TELEGRAM_BOT_TOKEN or Config.TELEGRAM_BOT_TOKEN == "paste_your_token_here":
        print("[!] Error: TELEGRAM_BOT_TOKEN is not configured in .env")
        sys.exit(1)
    if not Config.TELEGRAM_CHAT_ID or Config.TELEGRAM_CHAT_ID == "paste_your_id_here":
        print("[!] Error: TELEGRAM_CHAT_ID is not configured in .env")
        sys.exit(1)

    if args.test:
        print("[*] Running in TEST MODE (scanning for Testnet chain 5042002)...")
        candidates = TESTNET_RPC_CANDIDATES
        # Add custom config rpc if it matches testnet
        if Config.ARC_RPC_URL not in candidates:
            candidates.insert(0, Config.ARC_RPC_URL)
        target_chain = 5042002
    else:
        print("[*] Running in MAINNET MODE (scanning for Mainnet chain 5042)...")
        candidates = get_mainnet_rpc_candidates()
        target_chain = 5042

    # Run scanner until a working RPC is found
    working_rpc = scan_rpcs(candidates, target_chain, poll_interval=args.poll)
    
    # Launch liquidity watcher
    print(f"\n[+] Launching watcher on discovered RPC: {working_rpc}")
    
    # Dynamic settings override for watcher explorer
    if target_chain == 5042:
        os.environ["ARC_EXPLORER_URL"] = "https://arcscan.app"
    else:
        os.environ["ARC_EXPLORER_URL"] = "https://testnet.arcscan.app"
        
    watch_liquidity(override_rpc=working_rpc)

if __name__ == "__main__":
    main()
