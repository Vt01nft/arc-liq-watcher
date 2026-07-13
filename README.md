# Arc Network Liquidity Watcher

A Python bot designed to monitor the Arc EVM network for Uniswap V2 and V3 pool deployment events. The system includes an RPC scanner to auto-detect when mainnet goes live, and immediately transitions to block-by-block event polling to push Telegram alerts.

## Features
* **RPC Scanner**: Auto-detects working mainnet endpoints (Chain ID 5042) from a list of candidate patterns (Alchemy, dRPC, public nodes) and launches the watcher.
* **Liquidity Watcher**: Scans logs block-by-block using signature topic hashes for Uniswap V2 PairCreated and Uniswap V3 PoolCreated events.
* **Token Metadata Extraction**: Dynamically queries newly deployed token contracts for symbol, name, and decimals to populate alerts.
* **State Management**: Persists the last processed block number locally to avoid duplicate scanning or missed blocks during restarts.
* **Telegram Integration**: Generates HTML alerts containing token addresses, pool contracts, and explorer links.

## Project Structure
* `scanner.py`: Entry point for auto-detecting a live RPC endpoint before launching the watcher.
* `watcher.py`: Main block polling loop and log decoder.
* `config.py`: Loads environment configurations and handles RPC validation.
* `telegram_client.py`: Client for sending formatted HTML alerts to Telegram.
* `simulate_event.py`: Helper script to verify Telegram API credentials and message rendering.
* `start_bot.ps1` / `stop_bot.ps1`: Scripts to launch or terminate the bot in the background (Windows).

## Installation

Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

Duplicate `.env.example` as `.env` and fill in the required parameters:
* `TELEGRAM_BOT_TOKEN`: Token provided by BotFather.
* `TELEGRAM_CHAT_ID`: Direct user ID or negative group ID.
* `ALCHEMY_API_KEY`: Personal Alchemy developer key.
* `ARC_RPC_URL`: Default RPC fallback (e.g. testnet).
* `POLL_INTERVAL_SECONDS`: Block polling interval (recommended: 0.5 or 1).

## Usage

### 1. Test Telegram and RPC Connection
Verify credentials and view formatting in Telegram:
```bash
python simulate_event.py
```

### 2. Run RPC Auto-Detection & Watcher (Mainnet)
Start the scanner to cycle candidate endpoints until Chain ID 5042 responds:
```bash
python scanner.py
```

### 3. Run RPC Auto-Detection & Watcher (Testnet)
Start the scanner searching for testnet endpoints (Chain ID 5042002):
```bash
python scanner.py --test
```

### 4. Run Watcher Directly
If you already have a working RPC endpoint, launch the watcher directly:
```bash
python watcher.py
```
