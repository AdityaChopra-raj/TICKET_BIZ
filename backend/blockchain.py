import time
from web3 import Web3
from web3.exceptions import TransactionNotFound

def init_web3(rpc_url):
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        raise ConnectionError("Unable to connect to RPC node.")
    return w3

def make_ticket_hash(ticket_number: str, event_name: str, timestamp: int = None) -> bytes:
    ts = str(timestamp or int(time.time()))
    from web3 import Web3
    return Web3.keccak(text=f"{event_name}|{ticket_number}|{ts}")

def load_contract(w3: Web3, address: str, abi: list):
    return w3.eth.contract(address=Web3.to_checksum_address(address), abi=abi)

def store_hash_on_chain(w3, contract, account_address, private_key, ticket_hash, chain_id):
    nonce = w3.eth.get_transaction_count(account_address)
    txn = contract.functions.storeTicket(ticket_hash).build_transaction({
        "from": account_address,
        "nonce": nonce,
        "chainId": chain_id,
        "gas": 200000,
        "gasPrice": w3.to_wei("5", "gwei")
    })
    signed = w3.eth.account.sign_transaction(txn, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    if receipt.status != 1:
        raise RuntimeError("Transaction failed")
    return tx_hash.hex()

def check_hash_on_chain(contract, ticket_hash):
    stored, ts = contract.functions.isStored(ticket_hash).call()
    return stored, ts if stored else None
