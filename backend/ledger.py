import csv
from pathlib import Path

LEDGER_FILE = Path(__file__).parent / "ledger.csv"
FIELDNAMES = [
    "event_id", "event_name", "first_name", "last_name", 
    "email", "phone", "uid", "hash", "num_tickets", "checked_in" 
]

# Ensure ledger file exists and has headers
if not LEDGER_FILE.exists():
    with open(LEDGER_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()

def get_ledger():
    """Reads the ledger CSV and returns a list of transaction dictionaries."""
    ledger = []
    try:
        with open(LEDGER_FILE, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    # Type conversion and validation
                    row["num_tickets"] = int(row.get("num_tickets", 0))
                    row["checked_in"] = int(row.get("checked_in", 0))
                    
                    if not row.get("event_id") or row["num_tickets"] == 0:
                        continue
                    
                    ledger.append(row)
                except Exception:
                    continue  
    except FileNotFoundError:
        pass
    return ledger

def add_transaction(event_id, event_name, first_name, last_name, email, phone, uid, hash_value, num_tickets):
    """Appends a transaction to the ledger CSV with hash and contact info."""
    num_tickets = int(num_tickets)
    with open(LEDGER_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writerow({
            "event_id": event_id,
            "event_name": event_name,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "uid": uid,
            "hash": hash_value,
            "num_tickets": num_tickets,
            "checked_in": 0 # Initialize checked_in count
        })

def get_tickets_sold(event_id):
    """Returns the total number of tickets sold for a given event ID."""
    ledger = get_ledger()
    total = sum(
        row.get("num_tickets", 0)
        for row in ledger
        if str(row.get("event_id")) == str(event_id)
    )
    return total

def update_checkin_status(uid, count):
    """
    Increments the 'checked_in' count for a specific UID to support partial check-in.
    """
    ledger = get_ledger()
    updated_ledger = []
    
    found = False
    for row in ledger:
        if row.get("uid") == uid:
            row["checked_in"] = row.get("checked_in", 0) + count
            found = True
        updated_ledger.append(row)
    
    if found:
        # Rewrite the entire CSV file with updated data
        with open(LEDGER_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(updated_ledger)
        return True
    return False
