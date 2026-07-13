import os
from dotenv import load_dotenv
from web3 import Web3

# Load variables from .env file
load_dotenv()

class Config:
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    ARC_RPC_URL = os.getenv("ARC_RPC_URL", "https://rpc.testnet.arc.network").strip()
    ALCHEMY_API_KEY = os.getenv("ALCHEMY_API_KEY", "").strip()
    
    # Try to parse Chain ID
    try:
        ARC_CHAIN_ID = int(os.getenv("ARC_CHAIN_ID", "5042002"))
    except ValueError:
        ARC_CHAIN_ID = 5042002

    # Try to parse Poll Interval
    try:
        POLL_INTERVAL = float(os.getenv("POLL_INTERVAL_SECONDS", "2"))
    except ValueError:
        POLL_INTERVAL = 2.0

    # Start block parser
    START_BLOCK_RAW = os.getenv("START_BLOCK", "latest").strip()
    if START_BLOCK_RAW.lower() == "latest":
        START_BLOCK = "latest"
    else:
        try:
            START_BLOCK = int(START_BLOCK_RAW)
        except ValueError:
            START_BLOCK = "latest"

def get_mainnet_rpc_candidates():
    """
    Returns a unique list of candidate Arc Mainnet RPC URLs.
    """
    candidates = []
    
    # 1. Custom URL from .env (if set)
    env_rpc = os.getenv("ARC_RPC_URL", "").strip()
    if env_rpc and env_rpc not in candidates:
        candidates.append(env_rpc)
        
    # 2. Custom Alchemy API key (if set)
    alchemy_key = os.getenv("ALCHEMY_API_KEY", "").strip()
    if alchemy_key:
        alchemy_url = f"https://arc-mainnet.g.alchemy.com/v2/{alchemy_key}"
        if alchemy_url not in candidates:
            candidates.append(alchemy_url)
            
    # 3. Default standard/guessed patterns
    defaults = [
        "https://arc-mainnet.g.alchemy.com/v2/demo",
        "https://rpc.mainnet.arc.network",
        "https://rpc.arc.network",
        "https://arc-mainnet.drpc.org",
        "https://arc.drpc.org",
    ]
    
    for d in defaults:
        if d not in candidates:
            candidates.append(d)
            
    return candidates


def validate_config():
    """
    Validates configuration and runs connection health checks on RPC.
    """
    errors = []
    if not Config.TELEGRAM_BOT_TOKEN or Config.TELEGRAM_BOT_TOKEN == "your_telegram_bot_token_here":
        errors.append("TELEGRAM_BOT_TOKEN is not configured in .env")
    if not Config.TELEGRAM_CHAT_ID or Config.TELEGRAM_CHAT_ID == "your_telegram_chat_id_here":
        errors.append("TELEGRAM_CHAT_ID is not configured in .env")
    if not Config.ARC_RPC_URL:
        errors.append("ARC_RPC_URL is not configured in .env")

    if errors:
        print("\n[!] Configuration Errors:")
        for err in errors:
            print(f"  - {err}")
        return False, None

    print(f"Connecting to RPC: {Config.ARC_RPC_URL}...")
    w3 = Web3(Web3.HTTPProvider(Config.ARC_RPC_URL))

    try:
        if not w3.is_connected():
            print("[!] Failed to connect to Arc RPC. Please check your ARC_RPC_URL.")
            return False, None
        
        # Verify Chain ID
        chain_id = w3.eth.chain_id
        print(f"[+] Connected successfully! Chain ID: {chain_id}")
        
        if chain_id != Config.ARC_CHAIN_ID:
            print(f"[!] Warning: Configured chain ID ({Config.ARC_CHAIN_ID}) does not match RPC chain ID ({chain_id}).")
            # We'll update the config chain ID dynamically to be safe
            Config.ARC_CHAIN_ID = chain_id
            
        current_block = w3.eth.block_number
        print(f"[+] Current Block Height: {current_block}")
        return True, w3
    except Exception as e:
        print(f"[!] Error verifying connection to RPC: {e}")
        return False, None

if __name__ == "__main__":
    # Test validator when run directly
    success, w3 = validate_config()
    if success:
        print("[+] Config is valid and RPC is reachable!")
    else:
        print("[!] Config validation failed.")
