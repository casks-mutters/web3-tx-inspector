#!/usr/bin/env python3
import argparse
import os
import sys
import time
from dataclasses import dataclass, asdict
from typing import Dict, Any
from web3 import Web3

DEFAULT_RPC = os.getenv("RPC_URL", "https://mainnet.infura.io/v3/your_api_key")

NETWORKS = {
    1: "Ethereum Mainnet",
    10: "Optimism",
    56: "BNB Smart Chain",
    137: "Polygon",
    42161: "Arbitrum One",
    8453: "Base",
}

EXPLORERS = {
    1: "https://etherscan.io",
    10: "https://optimistic.etherscan.io",
    56: "https://bscscan.com",
    137: "https://polygonscan.com",
    42161: "https://arbiscan.io",
    8453: "https://basescan.org",
}


def is_tx_hash(v: str) -> bool:
    return isinstance(v, str) and v.startswith("0x") and len(v) == 66 and all(c in "0123456789abcdefABCDEF" for c in v[2:])


def connect(rpc: str):
    start = time.time()
    w3 = Web3(Web3.HTTPProvider(rpc, request_kwargs={"timeout": 20}))
    if not w3.is_connected():
        print(f"❌ Could not connect to RPC: {rpc}")
        sys.exit(1)
    return w3, time.time() - start


def explorer_url(chain_id: int, tx_hash: str) -> str:
    base = EXPLORERS.get(chain_id)
    return f"{base}/tx/{tx_hash}" if base else "N/A"


@dataclass
class TxSummary:
    chainId: int
    network: str
    txHash: str
    from_addr: str
    to_addr: str
    blockNumber: int
    timestamp: int
    confirmations: int
    status: int
    gasUsed: int
    gasLimit: int
    gasEfficiency: float
    gasPriceGwei: float
    totalFeeEth: float
    baseFeeGwei: float
    miner: str
    explorer: str


def fetch_summary(w3: Web3, tx_hash: str) -> Dict[str, Any]:
    tx = w3.eth.get_transaction(tx_hash)
    if tx.blockNumber is None:
        print("⏳ Pending transaction.")
        sys.exit(0)

    receipt = w3.eth.get_transaction_receipt(tx_hash)
    block = w3.eth.get_block(receipt.blockNumber)
    latest = w3.eth.block_number

    gas_limit = tx.gas or 0
    gas_eff = (receipt.gasUsed / gas_limit * 100) if gas_limit else 0.0

    gas_price = getattr(receipt, "effectiveGasPrice", getattr(receipt, "gasPrice", 0))
    total_fee = receipt.gasUsed * gas_price

    base_fee = block.get("baseFeePerGas", 0)

    chain = w3.eth.chain_id

    summary = TxSummary(
        chainId=chain,
        network=NETWORKS.get(chain, f"Chain {chain}"),
        txHash=tx_hash,
        from_addr=tx["from"],
        to_addr=tx["to"] or "(contract creation)",
        blockNumber=receipt.blockNumber,
        timestamp=block.timestamp,
        confirmations=max(0, latest - receipt.blockNumber),
        status=receipt.status,
        gasUsed=receipt.gasUsed,
        gasLimit=gas_limit,
        gasEfficiency=round(gas_eff, 2),
        gasPriceGwei=float(Web3.from_wei(gas_price, "gwei")),
        totalFeeEth=float(Web3.from_wei(total_fee, "ether")),
        baseFeeGwei=float(Web3.from_wei(base_fee, "gwei")),
        miner=block.get("miner", "N/A"),
        explorer=explorer_url(chain, tx_hash),
    )
    return asdict(summary)


def parse_args():
    p = argparse.ArgumentParser(description="Web3 transaction inspector with efficiency metrics.")
    p.add_argument("tx_hash")
    p.add_argument("--rpc", default=DEFAULT_RPC)
    p.add_argument("--json", action="true", help="Output JSON")
    return p.parse_args()


def main():
    args = parse_args()

    if not is_tx_hash(args.tx_hash):
        print("❌ Invalid tx hash.")
        sys.exit(1)

    w3, latency = connect(args.rpc)
    print(f"⚡ RPC latency: {latency:.3f}s")

    summary = fetch_summary(w3, args.tx_hash)

    if args.json:
        import json
        print(json.dumps(summary, indent=2, sort_keys=True))
        return

    print(f"🌐 Network: {summary['network']} ({summary['chainId']})")
    print(f"🔗 Explorer: {summary['explorer']}")
    print(f"👤 From: {summary['from_addr']}")
    print(f"🎯 To: {summary['to_addr']}")
    print(f"📦 Status: {'Success' if summary['status'] else 'Failed'}")
    print(f"⛏  Miner: {summary['miner']}")
    print(f"🔢 Block: {summary['blockNumber']}  ⏱  {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(summary['timestamp']))} UTC")
    print(f"🔁 Confirmations: {summary['confirmations']}")
    print(f"⛽ Gas Used: {summary['gasUsed']}/{summary['gasLimit']} ({summary['gasEfficiency']}%)")
    print(f"⛽ Gas Price: {summary['gasPriceGwei']:.2f} gwei  BaseFee: {summary['baseFeeGwei']:.2f} gwei")
    print(f"💰 Total Fee: {summary['totalFeeEth']:.6f} ETH")


if __name__ == "__main__":
    main()
