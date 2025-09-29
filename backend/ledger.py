import csv, hashlib, datetime
from pathlib import Path

LEDGER_CSV = Path(__file__).parent / "ledger.csv"

def add_block(uid, first, last, action):
    ledger = read_ledger()
    index = len(ledger)
    prev_hash = ledger[-1]["hash"] if ledger else "0"*64
    timestamp = datetime.datetime.utcnow().isoformat()
    raw = f"{index}{uid}{first}{last}{action}{timestamp}{prev_hash}".encode()
    block_hash = hashlib.sha256(raw).hexdigest()
    row = {"index":index,"uid":uid,"first":first,"last":last,"action":action,"timestamp":timestamp,"hash":block_hash,"prev_hash":prev_hash}
    with open(LEDGER_CSV,"a",newline="",encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if f.tell()==0:
            writer.writeheader()
        writer.writerow(row)

def read_ledger():
    if not LEDGER_CSV.exists(): return []
    with open(LEDGER_CSV,"r",newline="",encoding="utf-8") as f:
        return list(csv.DictReader(f))
