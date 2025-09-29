import csv
from pathlib import Path
import hashlib
from datetime import datetime

LEDGER_FILE = Path(__file__).parent / "ledger.csv"

def get_ledger():
    if not LEDGER_FILE.exists():
        return []
    ledger = []
    with open(LEDGER_FILE, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["tickets"] = int(row.get("tickets", 0))
            ledger.append(row)
    return ledger

def add_transaction(event, first_name, last_name, uid, tickets, email):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ledger = get_ledger()
    previous_hash = ledger[-1]["hash"] if ledger else "0"*64
    # Generate SHA256 hash for blockchain
    hash_input = f"{previous_hash}{event}{first_name}{last_name}{uid}{tickets}{timestamp}"
    block_hash = hashlib.sha256(hash_input.encode()).hexdigest()
    
    row = {
        "event": event,
        "first_name": first_name,
        "last_name": last_name,
        "uid": uid,
        "tickets": tickets,
        "email": email,
        "timestamp": timestamp,
        "hash": block_hash,
        "previous_hash": previous_hash
    }
    
    file_exists = LEDGER_FILE.exists()
    with open(LEDGER_FILE, "a", newline="", encoding="utf-8") as f:
        fieldnames = ["event","first_name","last_name","uid","tickets","email","timestamp","hash","previous_hash"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)
