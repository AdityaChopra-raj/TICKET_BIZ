# ledger.py

import csv
import hashlib
from pathlib import Path

LEDGER_FILE = Path(__file__).parent / "ledger.csv"

FIELDS = ["event", "first_name", "last_name", "student_id", "email", "tickets", "check_ins", "prev_hash", "hash"]

def get_ledger():
    ledger = []
    if LEDGER_FILE.exists():
        with open(LEDGER_FILE, mode="r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert numeric fields
                row["tickets"] = int(row["tickets"])
                row["check_ins"] = int(row["check_ins"])
                ledger.append(row)
    return ledger

def compute_hash(record):
    record_string = (
        f"{record['event']}{record['first_name']}{record['last_name']}"
        f"{record['student_id']}{record['email']}{record['tickets']}{record['check_ins']}{record['prev_hash']}"
    )
    return hashlib.sha256(record_string.encode()).hexdigest()

def add_transaction(event, first_name, last_name, student_id, email, tickets, check_ins=0):
    ledger = get_ledger()
    prev_hash = ledger[-1]["hash"] if ledger else "0"*64
    record = {
        "event": event,
        "first_name": first_name,
        "last_name": last_name,
        "student_id": student_id,
        "email": email,
        "tickets": tickets,
        "check_ins": check_ins,
        "prev_hash": prev_hash,
        "hash": ""
    }
    record["hash"] = compute_hash(record)

    # Append to CSV
    write_header = not LEDGER_FILE.exists()
    with open(LEDGER_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if write_header:
            writer.writeheader()
        writer.writerow(record)
    return record

def update_check_in(uid_record_index, num_check_ins):
    """Update check-ins for a specific record index in ledger"""
    ledger = get_ledger()
    if uid_record_index < 0 or uid_record_index >= len(ledger):
        return False  # Invalid index

    record = ledger[uid_record_index]
    record["check_ins"] += num_check_ins
    record["tickets"] -= num_check_ins
    record["hash"] = compute_hash(record)
    ledger[uid_record_index] = record

    # Rewrite the ledger
    with open(LEDGER_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(ledger)
    return True
