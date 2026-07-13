import time
import os
import sys
from web3 import Web3
from config import Config, validate_config
from telegram_client import send_telegram_message

# Dynamic Keccak signatures
V2_PAIR_CREATED_SIG = "PairCreated(address,address,address,uint256)"
V3_POOL_CREATED_SIG = "PoolCreated(address,address,uint24,int24,address)"

# Minimal ERC20 ABI to query token metadata
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [],
        "name": "name",
        "outputs": [{"name": "", "type": "string"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    }
]

# Configurable paths
STATE_FILE = "last_block.txt"
EXPLORER_URL = os.getenv("ARC_EXPLORER_URL", "https://testnet.arcscan.app").rstrip("/")

def get_last_processed_block(w3):
    """
    Retrieves the last processed block from the state file.
    Falls back to Config.START_BLOCK if file doesn't exist or is invalid.
    """
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                block = int(f.read().strip())
                print(f"[+] Resuming from last saved block: {block}")
                return block
        except Exception:
            print("[!] State file corrupted. Falling back to configured start block.")
            
    if isinstance(Config.START_BLOCK, int):
        print(f"[+] Starting from configured block: {Config.START_BLOCK}")
        return Config.START_BLOCK
        
    latest = w3.eth.block_number
    print(f"[+] Starting from latest block: {latest}")
    return latest

def save_last_processed_block(block):
    """
    Saves the last processed block number to keep track of state across restarts.
    """
    try:
        with open(STATE_FILE, "w") as f:
            f.write(str(block))
    except Exception as e:
        print(f"[!] Warning: Failed to save block state: {e}")

def get_token_info(w3, token_address):
    """
    Queries basic token metadata (symbol, name, decimals) via ERC20 contract.
    """
    token_address = Web3.to_checksum_address(token_address)
    contract = w3.eth.contract(address=token_address, abi=ERC20_ABI)
    
    # Defaults in case of failures
    symbol = "UNKNOWN"
    name = "Unknown Token"
    decimals = 18
    
    try:
        symbol = contract.functions.symbol().call()
    except Exception:
        pass
        
    try:
        name = contract.functions.name().call()
    except Exception:
        pass
        
    try:
        decimals = contract.functions.decimals().call()
    except Exception:
        pass
        
    return {
        "address": token_address,
        "symbol": symbol,
        "name": name,
        "decimals": decimals
    }

def handle_v2_pool(w3, log, tx_hash):
    """
    Decodes Uniswap V2 PairCreated event logs.
    """
    try:
        # topics[1] = token0 (padded)
        # topics[2] = token1 (padded)
        token0_address = Web3.to_checksum_address("0x" + log['topics'][1].hex()[-40:])
        token1_address = Web3.to_checksum_address("0x" + log['topics'][2].hex()[-40:])
        
        # data contains pair (padded) and uint256 index
        data_hex = log['data'].hex() if isinstance(log['data'], bytes) else log['data']
        # Remove 0x prefix if present
        if data_hex.startswith("0x"):
            data_hex = data_hex[2:]
            
        # Word 1 (first 64 chars) is pair address
        pair_hex = "0x" + data_hex[24:64]
        pair_address = Web3.to_checksum_address(pair_hex)
        
        token0_info = get_token_info(w3, token0_address)
        token1_info = get_token_info(w3, token1_address)
        
        # Format Alert
        alert_msg = (
            f"🚀 <b>New DEX Pool Created (Uniswap V2 Clone)</b>\n\n"
            f"<b>Token 0:</b> {token0_info['name']} ({token0_info['symbol']})\n"
            f"<code>{token0_address}</code>\n\n"
            f"<b>Token 1:</b> {token1_info['name']} ({token1_info['symbol']})\n"
            f"<code>{token1_address}</code>\n\n"
            f"<b>Pool Pair Address:</b>\n"
            f"<code>{pair_address}</code>\n\n"
            f"🔗 <a href='{EXPLORER_URL}/address/{pair_address}'>View Pool on Explorer</a>\n"
            f"🔗 <a href='{EXPLORER_URL}/tx/{tx_hash}'>View Transaction</a>"
        )
        print(f"\n[🔥] DETECTED V2 POOL CREATION: {token0_info['symbol']}/{token1_info['symbol']} at {pair_address}")
        send_telegram_message(alert_msg)
        
    except Exception as e:
        print(f"[!] Error decoding Uniswap V2 log: {e}")

def handle_v3_pool(w3, log, tx_hash):
    """
    Decodes Uniswap V3 PoolCreated event logs.
    """
    try:
        # topics[1] = token0 (padded)
        # topics[2] = token1 (padded)
        # topics[3] = fee (padded)
        token0_address = Web3.to_checksum_address("0x" + log['topics'][1].hex()[-40:])
        token1_address = Web3.to_checksum_address("0x" + log['topics'][2].hex()[-40:])
        
        # fee is topics[3]
        fee = int(log['topics'][3].hex(), 16)
        
        # data contains tickSpacing and pool (padded)
        data_hex = log['data'].hex() if isinstance(log['data'], bytes) else log['data']
        if data_hex.startswith("0x"):
            data_hex = data_hex[2:]
            
        # Word 2 (chars 64 to 128) is pool address
        pool_hex = "0x" + data_hex[88:128]
        pool_address = Web3.to_checksum_address(pool_hex)
        
        token0_info = get_token_info(w3, token0_address)
        token1_info = get_token_info(w3, token1_address)
        
        alert_msg = (
            f"🦄 <b>New DEX Pool Created (Uniswap V3 Clone)</b>\n\n"
            f"<b>Token 0:</b> {token0_info['name']} ({token0_info['symbol']})\n"
            f"<code>{token0_address}</code>\n\n"
            f"<b>Token 1:</b> {token1_info['name']} ({token1_info['symbol']})\n"
            f"<code>{token1_address}</code>\n\n"
            f"<b>Fee Tier:</b> {fee / 10000}%\n"
            f"<b>Pool Address:</b>\n"
            f"<code>{pool_address}</code>\n\n"
            f"🔗 <a href='{EXPLORER_URL}/address/{pool_address}'>View Pool on Explorer</a>\n"
            f"🔗 <a href='{EXPLORER_URL}/tx/{tx_hash}'>View Transaction</a>"
        )
        print(f"\n[🔥] DETECTED V3 POOL CREATION: {token0_info['symbol']}/{token1_info['symbol']} at {pool_address}")
        send_telegram_message(alert_msg)
        
    except Exception as e:
        print(f"[!] Error decoding Uniswap V3 log: {e}")

def watch_liquidity(override_rpc=None):
    # 1. Validate Config & Get Web3 Instance
    if override_rpc:
        print(f"[+] Initializing watcher on RPC: {override_rpc}")
        w3 = Web3(Web3.HTTPProvider(override_rpc, request_kwargs={'timeout': 5}))
    else:
        success, w3 = validate_config()
        if not success:
            print("[!] Invalid config. Exiting.")
            sys.exit(1)
        
    # Calculate keccak topics
    v2_topic = w3.keccak(text=V2_PAIR_CREATED_SIG).hex()
    v3_topic = w3.keccak(text=V3_POOL_CREATED_SIG).hex()
    
    print(f"[+] Loaded Event Topics:")
    print(f"  - Uniswap V2 PairCreated: {v2_topic}")
    print(f"  - Uniswap V3 PoolCreated: {v3_topic}")
    
    # We query the block number inside a try-except to prevent startup crash on rate limits
    current_block = None
    while current_block is None:
        try:
            current_block = get_last_processed_block(w3)
        except Exception as e:
            print(f"[!] Error fetching starting block (rate limited?): {e}. Retrying in 5 seconds...")
            time.sleep(5)
    
    print("\n[+] Starting liquidity event watcher loop. Polling block-by-block...")
    send_telegram_message("🤖 <b>Arc Liquidity Watcher is now ONLINE</b> and listening for pool creations...")

    
    max_batch_size = 100
    
    while True:
        try:
            latest_block = w3.eth.block_number
            if current_block > latest_block:
                time.sleep(Config.POLL_INTERVAL)
                continue
                
            # Determine scanning range (with batch size safety)
            end_block = min(latest_block, current_block + max_batch_size - 1)
            
            print(f"\rScanning blocks {current_block} to {end_block} (Latest: {latest_block})...", end="", flush=True)
            
            # Fetch matching logs
            logs = w3.eth.get_logs({
                'fromBlock': current_block,
                'toBlock': end_block,
                'topics': [[v2_topic, v3_topic]]
            })
            
            for log in logs:
                tx_hash = log['transactionHash'].hex()
                topic_sig = log['topics'][0].hex()
                
                if topic_sig == v2_topic:
                    handle_v2_pool(w3, log, tx_hash)
                elif topic_sig == v3_topic:
                    handle_v3_pool(w3, log, tx_hash)
                    
            # Update state
            current_block = end_block + 1
            save_last_processed_block(current_block - 1)
            
        except KeyboardInterrupt:
            print("\n[+] Stopping watcher. Goodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"\n[!] Error in watch loop: {e}")
            time.sleep(5) # Cooldown on failure

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Arc Network Liquidity Watcher")
    parser.add_argument("--rpc", help="Override RPC URL to scan")
    args = parser.parse_args()
    
    watch_liquidity(override_rpc=args.rpc)

