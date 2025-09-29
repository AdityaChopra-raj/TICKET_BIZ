import csv, hashlib, os
from datetime import datetime

LEDGER_FILE = "ledger.csv"

def _hash_block(index, timestamp, uid, first, last, action, prev_hash):
    text = f"{index}{timestamp}{uid}{first}{last}{action}{prev_hash}"
    return hashlib.sha256(text.encode()).hexdigest()

def init_ledger():
    if not os.path.exists(LEDGER_FILE):
        with open(LEDGER_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["index","timestamp","uid","first_name","last_name","action","previous_hash","hash"])
            genesis_hash = _hash_block(0,"genesis","0","0","0","genesis","0")
            writer.writerow([0,"genesis","0","0","0","genesis","0",genesis_hash])

def add_block(uid, first_name, last_name, action):
    init_ledger()
    with open(LEDGER_FILE, "r", newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    last = rows[-1]
    prev_hash = last[-1]
    index = int(last[0]) + 1
    timestamp = datetime.utcnow().isoformat()
    h = _hash_block(index, timestamp, uid, first_name, last_name, action, prev_hash)
    with open(LEDGER_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([index, timestamp, uid, first_name, last_name, action, prev_hash, h])
    return {"index": index, "timestamp": timestamp, "uid": uid, "first_name": first_name, "last_name": last_name, "action": action, "previous_hash": prev_hash, "hash": h}

def read_ledger():
    init_ledger()
    with open(LEDGER_FILE, "r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))
