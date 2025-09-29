import csv
from pathlib import Path
import hashlib

LEDGER_FILE = Path(__file__).parent / "ledger.csv"

def add_transaction(event_name, email, tickets_bought, timestamp,
                    first_name="", last_name="", student_id=""):
    """
    Adds a transaction to the blockchain-style ledger.
    Includes:
    - Event info
    - Customer info (first name, last name, student ID, email)
    - Number of tickets bought
    - Timestamp
    - Previous hash and current hash
    """
    previous_hash = ""
    if LEDGER_FILE.exists():
        with open(LEDGER_FILE, newline="") as f:
            rows = list(csv.DictReader(f))
            if rows:
                previous_hash = rows[-1]["hash"]

    # Generate a short unique ticket UID
    ticket_uid = hashlib.sha256(f"{email}{timestamp}".encode()).hexdigest()[:8]

    # Compute current hash
    data_str = f"{event_name}{email}{tickets_bought}{timestamp}{previous_hash}{first_name}{last_name}{student_id}"
    current_hash = hashlib.sha256(data_str.encode()).hexdigest()

    file_exists = LEDGER_FILE.exists()
    with open(LEDGER_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "ticket_uid","event","first_name","last_name","student_id",
            "email","tickets_bought","timestamp","prev_hash","hash"
        ])
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "ticket_uid": ticket_uid,
            "event": event_name,
            "first_name": first_name,
            "last_name": last_name,
            "student_id": student_id,
            "email": email,
            "tickets_bought": tickets_bought,
            "timestamp": timestamp,
            "prev_hash": previous_hash,
            "hash": current_hash
        })

def get_ledger():
    """
    Returns all transactions from the ledger as a list of dictionaries.
    """
    if not LEDGER_FILE.exists():
        return []
    with open(LEDGER_FILE, newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)
