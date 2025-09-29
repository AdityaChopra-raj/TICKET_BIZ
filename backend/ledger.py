# ledger.py
import csv
import hashlib
from pathlib import Path

LEDGER_FILE = Path(__file__).parent / "ledger.csv"

def hash_record(record, prev_hash="0"):
    """Generate a SHA-256 hash of the record combined with previous hash."""
    record_str = f"{record['event']}{record['first_name']}{record['last_name']}{record['uid']}{record['tickets']}{prev_hash}"
    return hashlib.sha256(record_str.encode()).hexdigest()

def get_ledger():
    """Retrieve ledger from CSV. Returns list of dicts."""
    ledger = []
    if LEDGER_FILE.exists():
        with open(LEDGER_FILE, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row["tickets"] = int(row["tickets"])
                row["checkins"] = int(row.get("checkins", 0))
                ledger.append(row)
    return ledger

def add_transaction(event, first_name, last_name, uid, tickets):
    """Add a new transaction (ticket purchase) to the ledger."""
    ledger = get_ledger()
    prev_hash = ledger[-1]["hash"] if ledger else "0"
    new_record = {
        "event": event,
        "first_name": first_name,
        "last_name": last_name,
        "uid": uid,
        "tickets": tickets,
        "checkins": 0,  # initially no check-ins
        "hash": hash_record({"event": event, "first_name": first_name, "last_name": last_name, "uid": uid, "tickets": tickets}, prev_hash)
    }
    ledger.append(new_record)
    
    # Write back to CSV
    with open(LEDGER_FILE, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["event", "first_name", "last_name", "uid", "tickets", "checkins", "hash"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in ledger:
            writer.writerow(row)

def update_checkin(uid, num_people=1):
    """Update the check-in count for a given UID."""
    ledger = get_ledger()
    updated = False
    for row in ledger:
        if row["uid"] == uid:
            if "checkins" not in row:
                row["checkins"] = 0
            row["checkins"] += num_people
            updated = True
            break
    if updated:
        # Rewrite CSV
        with open(LEDGER_FILE, "w", newline="", encoding="utf-8") as f:
            fieldnames = ["event", "first_name", "last_name", "uid", "tickets", "checkins", "hash"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in ledger:
                writer.writerow(row)
    return updated
