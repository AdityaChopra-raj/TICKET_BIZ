import csv
from pathlib import Path
import hashlib
from datetime import datetime

LEDGER_FILE = Path(__file__).parent / "ledger.csv"

# Ensure ledger file exists
if not LEDGER_FILE.exists():
    with open(LEDGER_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["event","first_name","last_name","uid","tickets","timestamp","hash"])
        writer.writeheader()

def calculate_hash(record, previous_hash=""):
    record_string = f"{record['event']}{record['first_name']}{record['last_name']}{record['uid']}{record['tickets']}{record['timestamp']}{previous_hash}"
    return hashlib.sha256(record_string.encode()).hexdigest()

def add_transaction(event, first_name, last_name, uid, tickets):
    ledger = get_ledger()
    previous_hash = ledger[-1]["hash"] if ledger else ""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    record = {
        "event": event,
        "first_name": first_name,
        "last_name": last_name,
        "uid": uid,
        "tickets": tickets,
        "timestamp": timestamp,
        "hash": ""
    }
    record["hash"] = calculate_hash(record, previous_hash)

    with open(LEDGER_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=record.keys())
        writer.writerow(record)

def get_ledger():
    records = []
    with open(LEDGER_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["tickets"] = int(row["tickets"])
            records.append(row)
    return records
