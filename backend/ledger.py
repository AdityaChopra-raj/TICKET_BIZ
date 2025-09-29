import csv, hashlib
from datetime import datetime
from pathlib import Path

LEDGER_FILE = Path(__file__).parent / "ledger.csv"

def hash_block(prev_hash, uid, first, last, action, timestamp):
    return hashlib.sha256(f"{prev_hash}{uid}{first}{last}{action}{timestamp}".encode()).hexdigest()

def add_block(uid, first, last, action):
    timestamp = datetime.utcnow().isoformat()
    prev_hash = ""
    ledger_rows = []
    if LEDGER_FILE.exists():
        with open(LEDGER_FILE,"r",newline="",encoding="utf-8") as f:
            reader = csv.DictReader(f)
            ledger_rows = list(reader)
            prev_hash = ledger_rows[-1]["hash"] if ledger_rows else ""
    block_hash = hash_block(prev_hash, uid, first, last, action, timestamp)
    row = {"index":len(ledger_rows)+1,"uid":uid,"first_name":first,"last_name":last,
           "action":action,"timestamp":timestamp,"previous_hash":prev_hash,"hash":block_hash}
    ledger_rows.append(row)
    with open(LEDGER_FILE,"w",newline="",encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        writer.writeheader()
        writer.writerows(ledger_rows)
    return row

def read_ledger():
    if LEDGER_FILE.exists():
        with open(LEDGER_FILE,"r",newline="",encoding="utf-8") as f:
            return list(csv.DictReader(f))
    return []
