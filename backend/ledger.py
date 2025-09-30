import csv
from pathlib import Path

LEDGER_FILE = Path(__file__).parent / "ledger.csv"

# Ensure ledger file exists
if not LEDGER_FILE.exists():
    with open(LEDGER_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "event_id", "event_name", "first_name", "last_name", "uid", "num_tickets"
        ])
        writer.writeheader()

def get_ledger():
    ledger = []
    with open(LEDGER_FILE, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                row["num_tickets"] = int(row.get("num_tickets", 0))
                row["event_id"] = row.get("event_id", "")
                row["event_name"] = row.get("event_name", "")
                row["first_name"] = row.get("first_name", "")
                row["last_name"] = row.get("last_name", "")
                row["uid"] = row.get("uid", "")
                ledger.append(row)
            except Exception:
                continue  # skip malformed row
    return ledger

def add_transaction(event_id, event_name, first_name, last_name, uid, num_tickets):
    """Add a transaction to the ledger CSV."""
    num_tickets = int(num_tickets)
    with open(LEDGER_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "event_id", "event_name", "first_name", "last_name", "uid", "num_tickets"
        ])
        writer.writerow({
            "event_id": event_id,
            "event_name": event_name,
            "first_name": first_name,
            "last_name": last_name,
            "uid": uid,
            "num_tickets": num_tickets
        })

def get_tickets_sold(event_id):
    """Return the total number of tickets sold for a given event."""
    ledger = get_ledger()
    total = sum(
        row.get("num_tickets", 0)
        for row in ledger
        if row.get("event_id") == event_id
    )
    return total

def get_transactions_by_uid(uid):
    """Return all transactions for a given UID."""
    ledger = get_ledger()
    return [row for row in ledger if row.get("uid") == uid]

