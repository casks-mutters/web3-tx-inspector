# web3-tx-inspector

A lightweight, developer-friendly CLI tool for inspecting Ethereum (EVM) transactions with **minimal RPC calls**.  
It focuses on performance, clarity, and useful metrics such as **gas efficiency**, **fee breakdown**, and **block explorer links**.

This repo contains **two files only**:
- `app.py` — The CLI script  
- `README.md` — This documentation  


## Features

- Fetches transaction receipt + block + metadata with minimal RPC calls
- Computes:
  - Gas efficiency (% of gas used vs. gas limit)
  - Total gas fee (ETH)
  - Gas price and base fee at time of execution
- Detects pending transactions
- Shows miner/validator address
- Auto-selects explorer URLs (Etherscan, Polygonscan, Arbiscan, BaseScan, etc.)
- JSON output option for automation
- Supports custom RPC endpoints via:
  - `--rpc`
  - or `RPC_URL` environment variable  


## Installation

Requires Python 3.10+ and `web3` library:

